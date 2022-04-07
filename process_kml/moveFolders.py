import os
from shutil import copyfile
from perfectures import perfecture_code, perfecture_romaji

source = 'E:\\afterFIT_intern\\data\\shinrinhou'
# source = 'E:\\afterFIT_intern\\data\\nouchihou'
# source = 'E:\\afterFIT_intern\\data\\農地'
dest = 'E:\\afterFIT_intern\\datacreation'

# get dirs
for root, dirs, _ in os.walk(source):
	if os.path.basename(root) == os.path.basename(source):
		source_dirs = dirs 

# move dirs to each perfectures folder & rename with format [data]_[perfecture]
for folder in source_dirs:
	code = folder.strip('_GML').split('_')[-1]
	perfecture = perfecture_romaji[perfecture_code[code]]
	dest_dir = os.path.join(dest, code + perfecture)
	copyfile(os.path.join(source, folder), dest_dir)
	os.rename(os.path.join(dest_dir, folder), os.path.join(dest_dir, os.path.basename(source) + "_" + perfecture))