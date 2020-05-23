import os

#entries = os.listdir('.')
#for entry in entries:
#	print(entry)

# List all files in a directory using os.listdir
basepath = '.'
for entry in os.listdir(basepath):
    if os.path.isfile(os.path.join(basepath, entry)):
        print(entry)

for dirpath, dirnames, files in os.walk('.'):
    print(f'Found directory: {dirpath}')
    for file_name in files:
        print(file_name)

os.system('jupyter nbconvert *.ipynb */*.ipynb')
