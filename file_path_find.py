import os
# [OrderedDict([('ID', 'pengjinhua1-7'), ('Image', 'D:\\PyProjects\\feature_extract\\data\\pengjinhua1-7\\pengjinhua1-7.nii'), ('Mask', 'D:\\PyProjects\\feature_extract\\data\\pengjinhua1-7\\Segmentation-label.nrrd')])]

def walkFile(files):
    flist = []
    for root, dirs, files in os.walk(files):
        dic = {}
        for f in files:
            filepath = os.path.join(root,f)
            id = root[root.rindex('\\') + 1:]
            dic['ID'] = id
            if (filepath.endswith('nii')):
                dic['Image'] = filepath
            if (filepath.endswith('label.nrrd')):
                dic['Mask'] = filepath
        print(dic)
        if (len(dic) != 0):
            flist.append(dic)
        for d in dirs:
            print('dir ' + os.path.join(root,d))
    return flist
def main():
    flist = walkFile("D:\\PyProjects\\feature_extract\\data")
    print(flist)
    for idx, entry in enumerate(flist):
        # print(entry)
        print(entry['Image'])
        print(entry['Mask'])

if __name__ == '__main__':
    # main()
    print(os.path.join(os.getcwd(),'Params_AICC_1.yaml'))
