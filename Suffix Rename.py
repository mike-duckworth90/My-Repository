# input('importing...') Check that modules are installed in global environment and not just venv
# v3.7: deal with md5 hash duplicates before starting

import hashlib
import csv
import re
import sys
import shutil
import os
from datetime import datetime

print('Welcome to Michael''s suffix rename tool! A simple file to retain the established '
    'date prefix (and file extension), renaming just the suffix of the previously processed files')
    

# pip install libmagic
# pip install python-magic-bin==0.4.14

logPath = 'C:\\Users\\Mike_\\OneDrive\\My Media\\Media to Sort\\Rename Logs\\'

scriptPath = os.path.dirname(sys.argv[0])
scriptPath = 'C:\\Users\\Mike_\\OneDrive\\Documents\\My Projects\\Project Big Media Database\\Rename Testing\\Testing'

os.chdir(scriptPath)
cwd = os.getcwd()
files = os.listdir(cwd)

suffix = input('Choose a new suffix: ')

def suffix_rename(f):
    f_core = os.path.splitext(f)[0]
    f_ext = os.path.splitext(f)[1]

   # 2.1 Previously parsed files of the 2020 format
    if re.search(
        r'20[0-9]{2}-[0-1][0-9]-[0-3][0-9] [0-2][0-9].[0-5][0-9].[0-5][0-9] [A-z]{4}[0-9]{4}', f_core[:28]):
        f_new = f[:28] + ' ' + suffix + f_ext
        #print(f, i, 'suffix rename', f_new, sep='|')
    return f_new


# define some variables for the upcoming ername and logging loop
global f_new
f_new = ''
fullData = []
md5_hash = hashlib.md5()

for f in files:
    f_new = suffix_rename(f)

    with open(f, 'rb') as read_file:
        content = read_file.read()
        # updates md5 hash OBJECT e.g. <md5 HASH object @ 0x01683E20>
        md5_hash.update(content)
    digest = md5_hash.hexdigest()  # creates md5 hash STRING

    # start logging process
    fullDataRow = f + '\t' + f_new + '\t' + digest
    fullData.append(fullDataRow)

    os.rename(f, f_new)


lastSlash = scriptPath[len(scriptPath):1:-1].find('\\')
lastFolder = scriptPath[len(scriptPath)-lastSlash:len(scriptPath):1]

with open(logPath + lastFolder + '-suffix-' +
          str(datetime.date(datetime.now())) + '-' + 'BackupDirList.txt', 'w') as bk:
    for line in fullData:
        bk.write(str(line))
        bk.write('\n')
    bk.write('Pre-processing complete on: ' + str(datetime.today()))

with open(logPath + lastFolder + '-' +
          str(datetime.date(datetime.now())) + '-' + 'csv_backup.csv', 'w', newline='') as csv_backup:

    csv_writer = csv.writer(csv_backup, delimiter=',')
    csv_writer.writerow(['Filename', 'DateMod', 'MD5Hash'])
    for line in fullData:
        csv_writer.writerow(line)

input('Suffix renaming complete. Press any key to continue')
