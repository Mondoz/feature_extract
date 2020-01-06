from __future__ import print_function
from PyQt5.QtWidgets import QDialog,QLabel,QLineEdit,QPushButton,QGridLayout,QVBoxLayout,QFileDialog,QApplication,QProgressBar
from PyQt5.QtGui import QIcon
import sys,os
import collections
import csv
import logging
import os
import file_path_find as ftool
import datetime
import SimpleITK as sitk
import radiomics
from radiomics import featureextractor

class mainDlg(QDialog):
    def __init__(self, parent=None):
        super(mainDlg, self).__init__(parent)
        self.setWindowTitle('Extract_Feature')
        self.setWindowIcon(QIcon('logo.png'))
        self.setui()

    def setui(self):
        inputFileLabel = QLabel('DirPath')
        self.inputFileLineEdit = QLineEdit()
        inputFileButton = QPushButton('SelectDir')
        startButton = QPushButton('Start')
        self.resultLineEdit = QLineEdit()
        self.pbar = QProgressBar()
        self.step = 0

        grid = QGridLayout()
        grid.addWidget(inputFileLabel, 0, 0)
        grid.addWidget(self.inputFileLineEdit, 0, 1)
        grid.addWidget(inputFileButton, 0, 2)
        grid2 = QGridLayout()
        grid2.addWidget(startButton, 1, 2, 1, 2)
        grid2.addWidget(self.resultLineEdit, 1, 0, 1, 2)
        grid3 = QGridLayout()
        grid3.addWidget(self.pbar,3,0)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(grid)
        mainLayout.addLayout(grid2)
        mainLayout.addLayout(grid3)

        self.setLayout(mainLayout)
        inputFileButton.clicked.connect(self.inputFileSelect)
        startButton.clicked.connect(self.run)

    def inputFileSelect(self):
        source_absolute_path = QFileDialog.getExistingDirectory(self, 'Open Dir', os.getcwd())
        self.inputFileLineEdit.setText(str(source_absolute_path))

    def run(self):
        filepath = str(self.inputFileLineEdit.text())
        print(filepath)
        self.process(filepath)
        self.resultLineEdit.setText(u'process finish')
        # self.pbar.setValue(100)

    def process(self,filepath):
        outPath = r''
        file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        # inputCSV = os.path.join(outPath, '2019110402.csv')
        outputFilepath = os.path.join(outPath, file_name + '_feature.csv')
        progress_filename = os.path.join(outPath, 'pyrad_log.txt')
        params = os.path.join(os.getcwd(), 'Params_AICC_1.yaml')

        # Configure logging
        rLogger = logging.getLogger('radiomics')

        # Set logging level
        # rLogger.setLevel(logging.INFO)  # Not needed, default log level of logger is INFO

        # Create handler for writing to log file
        handler = logging.FileHandler(filename=progress_filename, mode='w')
        handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s'))
        rLogger.addHandler(handler)

        # Initialize logging for batch log messages
        logger = rLogger.getChild('batch')

        # Set verbosity level for output to stderr (default level = WARNING)
        radiomics.setVerbosity(logging.INFO)

        logger.info('pyradiomics version: %s', radiomics.__version__)
        logger.info('Loading CSV')

        flists = []
        # try:
        #   with open(inputCSV, 'r') as inFile:
        #     cr = csv.DictReader(inFile, lineterminator='\n')
        #     flists = [row for row in cr]
        # except Exception:
        #   logger.error('CSV READ FAILED', exc_info=True)
        # print(flists)
        logger.info('Loading Done')
        flists = ftool.walkFile(filepath)
        logger.info('Patients: %d', len(flists))

        if os.path.isfile(params):
            logger.info('params is file')
            try:
                extractor = featureextractor.RadiomicsFeatureExtractor(params)
            except Exception as e:
                logger.error(e)
        else:  # Parameter file not found, use hardcoded settings instead
            settings = {}
            settings['binWidth'] = 25
            settings['resampledPixelSpacing'] = None  # [3,3,3]
            settings['interpolator'] = sitk.sitkBSpline
            settings['enableCExtensions'] = True

            extractor = featureextractor.RadiomicsFeatureExtractor(**settings)
            # extractor.enableInputImages(wavelet= {'level': 2})

        logger.info('Enabled input images types: %s', extractor.enabledImagetypes)
        logger.info('Enabled features: %s', extractor.enabledFeatures)
        logger.info('Current settings: %s', extractor.settings)

        headers = None

        for idx, entry in enumerate(flists):
            QApplication.processEvents()
            logger.info("(%d/%d) Processing Patient (Image: %s, Mask: %s)", idx, len(flists), entry['Image'],
                        entry['Mask'])

            imageFilepath = entry['Image']
            maskFilepath = entry['Mask']
            label = entry.get('Label', None)

            if str(label).isdigit():
                label = int(label)
            else:
                label = None

            if (imageFilepath is not None) and (maskFilepath is not None):
                featureVector = collections.OrderedDict(entry)
                featureVector['Image'] = os.path.basename(imageFilepath)
                featureVector['Mask'] = os.path.basename(maskFilepath)
                try:
                    featureVector.update(extractor.execute(imageFilepath, maskFilepath, label))
                    QApplication.processEvents()
                    with open(outputFilepath, 'a') as outputFile:
                        writer = csv.writer(outputFile, lineterminator='\n')
                        if headers is None:
                            headers = list(featureVector.keys())
                            writer.writerow(headers)

                        row = []
                        for h in headers:
                            row.append(featureVector.get(h, "N/A"))
                        writer.writerow(row)
                except Exception:
                    logger.error('FEATURE EXTRACTION FAILED', exc_info=True)
            try:
                self.step += 100/len(flists)
                self.pbar.setValue(self.step)
                # self.pbar.setValue(100)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = mainDlg()
    dlg.show()
    sys.exit(app.exec_())