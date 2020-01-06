import SimpleITK as sitk
import os
path = 'D:\\PyProjects\\feature_extract\\data\\test'
dirs = os.listdir(path)
result = open('D:\\PyProjects\\feature_extract\\data\\result.txt','w') #目标文件
for f in dirs:
    dir_path = (os.path.join(path,f))
    print(f)
    reader = sitk.ImageSeriesReader()
    # dicom_files = reader.GetGDCMSeriesFileNames('data/1.3.12.2.1107.5.1.4.65018.30000012021100095432800012743')
    dicom_files = reader.GetGDCMSeriesFileNames(dir_path)
    reader.SetFileNames(dicom_files)
    itkImage = reader.Execute()
    spacing_x, spacing_y, spacing_z = itkImage.GetSpacing()
    print(spacing_z)
    result.write(f + ',' + str(spacing_z) + '\n')


