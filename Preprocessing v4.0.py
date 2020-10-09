# input('importing...') Check that modules are installed in global environment and not just venv
# new to v4.0 againt 3.9: Split the metadata functions

print('Welcome to Michael''s magic pre-processing! The magical tool for renaming all your bull****.\r\n'
      'IMPORTANT! This script will only work for one single timezone and only allows you to input one filename'
      ' for all files\r\n')

# pip install libmagic
# pip install python-magic-bin==0.4.14

import concurrent.futures
import os
import shutil
import sys
import re
from datetime import datetime, timedelta
import time
import pytz
from dateutil.tz import tzlocal
from tzlocal import get_localzone
import PIL.Image
import PIL.ExifTags
import csv
import hashlib
from collections import defaultdict
import subprocess
import magic
from fractions import Fraction

logPath = 'C:\\Users\\Mike_\\OneDrive\\My Media\\Media to Sort\\Rename Logs\\'

scriptPath = os.path.dirname(sys.argv[0])
scriptPath = 'C:\\Users\\Mike_\\OneDrive\\Documents\\My Projects\\Project Big Media Database\\Rename Testing\\Testing'

exe = 'C:\\Program Files\\ExifTool\\exiftool.exe'

os.chdir(scriptPath)
cwd = os.getcwd()

# PART ONE: Welcome and user input

# 01. Choose the name to appear on all media items pre-processed
global suffix
suffix = input(
    "Choose a filename suffix for all media e.g. 'Val Thorens Skiing 2019': ")


# Function 1.1: Build PIL EXIF dictionaries
def generate_exif_dict(f):
    try:
        image = PIL.Image.open(f)

        exif_data = {}
        if image._getexif() is not None:
            image_exif = image._getexif()
            for k, v in PIL.ExifTags.TAGS.items():
                if k in image_exif:
                    value = image_exif[k]
                else:
                    value = None    # returns null rather than skipping the entry

                if len(str(value)) > 64:
                    value = str(value)[:64] + '...'

                exif_data[v] = {"tag": k, "raw": value, "processed": value}
        else:
            exif_data = {}

        image.close()
        #exif_data = _process_exif_dict(exif_data)
#        print(exif_data)
        return exif_data
    except IOError as ioe:
        pass


# Function 2.1: Sorting Hat
def sorting_hat(f):
    global f_house
    f_house = ''
    f_core = os.path.splitext(f)[0]
    f_ext = os.path.splitext(f)[1]
    global u_s
    global f_u_s
    global mime
    mime = ''
        
    # ascertain underscore position (if it exists)
    if '_' in f:
        u_s = f.find('_')
        f_u_s = f[0:u_s]
    else:
        u_s = 0

    # get file type using magic module.
    try:
        mime = magic.from_file(f)
    except:
        mime = ''

    # 1.1 Android regular images
    if f[0:u_s].lower() in ('img', 'vid', 'pano', 'save') and re.search(
            r'2[0-1][0-9]{2}[0-1][0-9][0-3][0-9]\_[0-2][0-9][0-5][0-9][0-5][0-9]', f_core[u_s+1:u_s+16]):
        f_house = 'android-regular'

    # 1.2 Android screenshot images
    elif f[0:u_s].lower() == 'screenshot' and re.search(
            r'2[0-1][0-9]{2}-[0-1][0-9]-[0-3][0-9]-[0-2][0-9]-[0-5][0-9]-[0-5][0-9]', f_core[u_s+1:u_s+23]):
        f_house = 'android-screenshot'

    # 1.3 Facebook [on android] saved file from date created
    elif f[0:3].lower() == 'fb_':
        f_house = 'android-facebook'

    # 1.4 GOOGLE Photos stylised photo only from date created
    elif f[0:7].lower() == 'effects':
        f_house = 'android-effects'

    # 2.1 Dropbox rename: retain prefix and add media, number and suffix
    elif re.search(
            r'20[0-9]{2}-[0-1][0-9]-[0-3][0-9] [0-2][0-9].[0-5][0-9].[0-5][0-9]', f_core[:19]) and len(f_core) == 19:
        f_house = 'dropbox'

    # 3.1 Other: requires PIL or ExifTool
    elif 'image' not in mime[0:30]:
        f_house = 'exiftool'

    elif 'image' in mime[0:30]:
        f_house = 'pillow'

    else:
        f_house = 'other'

    return f_house
 

# Function 3.1: rename by filename
def rename_by_filename(f, f_house, i):
    f_core = os.path.splitext(f)[0]
    f_ext = os.path.splitext(f)[1]
    f_i = str(i).zfill(4)
    Y = 0
    M = 0
    D = 0
    h = 0
    m = 0
    s = 0
    YMDhms = ''
    device = {'pano': 'ppan', 'screenshot': 'pscr', 'vid': 'pvid', 'img': 'pimg',
              'save': 'psav', 'fb': 'facb', 'effects': 'spfx'}

    if f_house == 'android-regular':
        media = device.get(f_u_s.lower(), "PHON").upper()
        tz_upd = 0
        Y = f[u_s+1:u_s+5]
        M = f[u_s+5:u_s+7]
        D = f[u_s+7:u_s+9]
        h = f[u_s+10:u_s+12]
        m = f[u_s+12:u_s+14]
        s = f[u_s+14:u_s+16]

        prise_de_vue = f'{Y}-{M}-{D} {h}.{m}.{s}'
        f_naive = f'{prise_de_vue} {media}{f_i} {suffix}{f_ext}'

    elif f_house == 'android-screenshot':
        media = 'PSCR'
        tz_upd = 0
        Y = f[u_s+1:u_s+5]
        M = f[u_s+6: u_s+8]
        D = f[u_s+9: u_s+11]
        h = f[u_s+12: u_s+14]
        m = f[u_s+15: u_s+17]
        s = f[u_s+18: u_s+20]

        prise_de_vue = f'{Y}-{M}-{D} {h}.{m}.{s}'
        f_naive = f'{prise_de_vue} {media}{f_i} {f_core[35::]}{f_ext}'

    elif f_house == 'dropbox':
        media = 'DBOX'
        tz_upd = 0

        prise_de_vue = f'{f[:19]}'
        f_naive = f'{prise_de_vue} {media}{f_i} {suffix}{f_ext}'

    return f_naive, prise_de_vue



# Function 4.1: Pillow or ExifTool heavy lifting
def exif_rename(f, f_house, i):
    # Part 1: define variables
    # f
    f_core = os.path.splitext(f)[0]
    f_ext = os.path.splitext(f)[1]
    f_i = str(i).zfill(4)

    # PIL (Pillow)
    pillow_DateTime = ''            # 'DateTime' (PIL)
    pillow_DateTimeOriginal = ''    # 'DateTimeOriginal' (PIL)
    pillow_DateTimeDigitized = ''   # 'DateTimeDigitized' (PIL)
    f_meta_pillow = {}              # full list of PIL metadata items
    Make = ''

    # ExifTool
    ExifTool_Media_Create_Date = ''      # 'Media Create Date' (ExifTool)
    ExifTool_DateTimeOriginal = ''      # 'Date/Time Original' (ExifTool)
    f_meta_ExifTool = {}            # full list of  ExifTool metadata items
    dict_keys = []                  # list of dictionary keys to be zipped
    dict_values = []                # list of dictionary values to be zipped

    # other/all
    media = ''
    global prise_de_vue
    prise_de_vue = ''               # final date field used after cascading hierarchy (pre tz update)
    os_Modified = ''                # 'mtime' from os
    os_Created = ''                 # 'ctime' from os

    # Part 2: TRY to generate extended metadata using Pillow
    
    if f_house == 'android-facebook':
        media = 'FACB'
        YMDhms = str(os_Created).replace(':', '.')
        tz_upd = 0

        prise_de_vue = f'{YMDhms}'
        f_naive = f'{prise_de_vue} {media}{f_i} {suffix}{f_ext}'
    
    elif f_house == 'pillow' or f_house == 'android-affects':
    # get PIL metadata
        try:
            f_meta_pillow = generate_exif_dict(f)
        except Exception as e:
            pass

        if f_meta_pillow is None:
            f_meta_pillow = {}

        Make = f_meta_pillow.get('Make'.lower(), '')

            # define media
        if 'apple' in Make:
            media = 'APPL'
        elif 'sony' in Make:
            media = 'SONY'
        elif 'nikon' in Make:
            media = 'NIKO'
        elif 'samsung' in Make:
            media = 'SAMS'
        elif 'canon' in Make:
            media = 'CANO'
        elif 'xiaomi' in Make:
            media = 'XIAO'
        elif 'olympus' in Make:
            media = 'OLYM'
        elif 'fujifilm' in Make:
            media = 'FUJI'
        elif 'panasonic' in Make:
            media = 'PANA'
        elif 'go pro' in Make or 'gopro' in Make:
            media = 'GPRO'
        elif f[0:3].lower() == 'dsc':
            media = 'NIKO'
        elif f[0:4].lower() == '_dsc':
            media = 'SONY'
        elif f[0:3].lower() == 'sdc' and len(f) == 12:
            media = 'SAMS'
        elif f[0:2].lower() in ('gs', 'gp', 'gh', 'gx', 'gf', 'gb', 'g0', 'g1', 'g2') or f[0:4].lower() == 'gopr':
            media = 'GPRO'
        elif f_house == 'android-effects':
            media = 'SPFX'
        else:
            media = 'FILE'

        # relegate the renegades to ExifTool
        if 'DateTime' not in f_meta_pillow and 'DateTimeOriginal' not in f_meta_pillow and 'DateTimeDigitized' not in f_meta_pillow:
            f_house = 'exiftool'
    # fi sorting_hat == 'pillow'

    # Part 3: ExifTool
    # Let's TRY and run ExifTool.exe iff PIL did not reveal any info
    if f_house in ('exiftool', 'other'):
        try:
            process = subprocess.Popen(             # subprocess call ExifTool by Phil Harvey
                [exe, f], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            #print('index = ', index, '| m =', m)
            for output in process.stdout:

                # creates unparsed line of metadata
                line = output.strip().split(':', 1)
                # creates messy list of dict keys
                dict_keys_preparse = line[0].strip().splitlines(False)
                # creates messy list of dict values
                if line[1] == '':
                    line[1] = 'NULL'
                dict_values_preparse = line[1].strip().splitlines(False)

                for k in dict_keys_preparse:                        # create tidy list of dict keys
                    dict_keys.append(k)
                for v in dict_values_preparse:                      # create tidy list of dict values
                    dict_values.append(v)

            # zip dict keys and values
            f_meta_ExifTool = dict(zip(dict_keys, dict_values))

        except:     # ExifTool.exe could not be run on the file and no metadata is available
            pass

    # Part 4: combine the best of both worlds
    # Populate as many date fields as possible
    try:
        ExifTool_Media_Create_Date = f_meta_ExifTool.get('Media Create Date', '')
    except:
        pass
    try:
        ExifTool_DateTimeOriginal = f_meta_ExifTool.get('Date/Time Original', '')
    except:
        pass
    try:
        if f_meta_pillow != {}:
            pillow_DateTimeOriginal = f_meta_pillow['DateTimeOriginal']['raw']
    except:
        pass
    try:
        if f_meta_pillow != {}:
            pillow_DateTimeDigitized = f_meta_pillow['DateTimeDigitized']['raw']
    except:
        pass
    try:
        os_Modified = str(datetime.fromtimestamp(
            os.stat(f).st_mtime)).replace('-', ':')[0:19]   # remove milliseconds
    except:
        pass
    try:
        os_Created = str(datetime.fromtimestamp(
            os.stat(f).st_ctime)).replace('-', ':')[0:19]   # remove milliseconds
    except:
        pass

    # Perform cascading flow of date fields
    if pillow_DateTime == '' or pillow_DateTime is None:
        if pillow_DateTimeOriginal == '' or pillow_DateTimeOriginal is None:
            if pillow_DateTimeDigitized == '' or pillow_DateTimeDigitized is None:
                if ExifTool_DateTimeOriginal == '' or ExifTool_DateTimeOriginal is None:
                    if ExifTool_Media_Create_Date == '' or ExifTool_Media_Create_Date is None:
                        if os_Modified == '' or os_Modified is None:
                            if os_Created == '' or os_Created is None:
                                prise_de_vue = '1707:01:01 00:00:00'
                            else:
                                prise_de_vue = os_Created
                        else:
                            prise_de_vue = os_Modified
                    else:
                        prise_de_vue = ExifTool_Media_Create_Date
                else:
                    prise_de_vue = ExifTool_DateTimeOriginal
            else:
                prise_de_vue = pillow_DateTimeDigitized
        else:
            prise_de_vue = pillow_DateTimeOriginal
    else:
        prise_de_vue = pillow_DateTime
        # prise_de_vue = '1707:01:01 01:00:00' # testing for when str-date conversions go awry

    #finally
    f_naive = f'{prise_de_vue} {media}{f_i} {suffix}{f_ext}'

    return f_naive, prise_de_vue


# Preview functionality (new to v3.7)
print('\n!!! PREVIEW !!!\n')
print('Review the first 5 files below and check their current timezone info')
print('Use this sample set to determine how to update their timezones')
print('HINT: look for sunsets, nighttime shots, midday sun etc.\n')

print('\nFilename' + ' '*37 + '||   Current Datestamp')
print('='*67)
files_all = os.listdir(cwd)
for f in files_all[0:5]:
    f_house = sorting_hat(f)
    f_len = len(f)
    f_pad = ' ' * (44 - f_len)
    
    if f_house in ('dropbox', 'android-regular', 'android-screenshot'): 
        _, prise_de_vue = rename_by_filename(f, f_house, 0)
    else:
        _, prise_de_vue = exif_rename(f, f_house, 0)
    

    print(f'{f}{f_pad} ||   {prise_de_vue}')


# 02. Establish any timezones that need to be adjusted for any DSLR and GoPro files.
timezoneCheck = input('\nHow would you like to adjust the timezone data?\n'
        ' - SKIP timezone adjustment: [S]\n'
        ' - ROLL forward (or backward) some hours on camera devices only: [R]\n'
        ' - CALCULATE the adjustment knowing the UTC offsets of the location and the camera''s timezone settings: [C]\n')
while not (timezoneCheck[0:1].lower() == 's' or timezoneCheck[0:1].lower() == 'r' or timezoneCheck[0:1].lower() == 'c'):
    timezoneCheck = input(
        '\nHow would you like to adjust the timezone data?\n'
        ' - SKIP timezone adjustment: [S]\n'
        ' - ROLL forward (or backward) some hours: [R]\n'
        ' - CALCULATE the adjustment knowing the UTC offsets of the location and the camera''s timezone settings: [C]\n')

if timezoneCheck[0:1].lower() == 'c':
    tzDest = input('In which UTC timezone was the trip taken? e.g. for NYC in the summer, type'
                   ' "-4": ')
    while not (tzDest.lstrip('-+')).isnumeric():
        tzDest = input(
            'In which UTC timezone was the trip taken? e.g. for France in the summer, type "2": ')

    systemCheck = input(
        'Are your device''s timezone settings the same as your PC''s current timezone? ')
    while not (systemCheck[0:1].lower() == 'y' or systemCheck[0:1].lower() == 'n'):
        systemCheck = input(
            'Are your device''s timezone settings the same as your current PC''s timezone? ')

    if systemCheck[0:1].lower() == 'n':
        tzDevice = input(
            'What is the UTC timezone of your devices e.g. for Sydney in December, type "11": ')
        while not (tzDevice.lstrip('-+')).isnumeric():
            tzDevice = input(
                'What is the UTC timezone of your devices e.g. for Vancouver in June, type "-7": ')
    else:
        tzDevice = float(str(datetime.now(tzlocal()))
                         [-6::].replace(':', '.'))  # get system tz offset

elif timezoneCheck[0:1].lower() == 'r':
    tzDest = input(
        'How many whole hours would you like to roll forward or back? ')
    while not (tzDest.lstrip('-+')).isnumeric():
        tzDest = input(
            'How many whole hours would you like to roll forward or back? ')
    tzDevice = 0

else:
    tzDest = 0
    tzDevice = 0

# end of user input. Start timer
start = time.time()

# part 3: adjust the timezones. Separated to allow the preview feature
# Function 5.1

def exif_final(f_naive, prise_de_vue, tz_upd):
    if tz_upd == 1:
        tz_update = str(datetime.strptime(f_naive[0:19], '%Y:%m:%d %H:%M:%S') +
                    timedelta(hours=-int(tzDevice) + int(tzDest))).replace(':', '.')
        f_new = tz_update + f_naive[19:]
    elif tz_upd == 0:
        f_new = f_naive
    else:
        print('error with tz_upd: ', tz_upd, sep='')
    return f_new


# Threading: update the user that the script is still running
def updatey():
    time.sleep(5)
    return 'script still running... Truuuust me'


f_delete = ('.thm', 'zz_PreProcessingComplete.py')
for rubbish in files_all:
    if os.path.splitext(rubbish)[1].lower() in f_delete or rubbish in f_delete:
        os.remove(rubbish)

md5_hash = hashlib.md5()
fullData = []
i = 1
print('script running...')


files = [d for d in os.listdir(cwd) if not os.path.isdir(d)]
for f in files:
    f_house = sorting_hat(f)

    if f_house in ('dropbox', 'android-regular', 'android-screenshot'):
        f_naive, prise_de_vue = rename_by_filename(f, f_house, i)
        tz_upd = 0
    else:
        f_naive, prise_de_vue = exif_rename(f, f_house, i)
        tz_upd = 1

    f_new = exif_final(f_naive, prise_de_vue, tz_upd)

    # record MD5 Hash
    with open(f, 'rb') as read_file:
        content = read_file.read()
        # updates md5 hash OBJECT e.g. <md5 HASH object @ 0x01683E20>
        md5_hash.update(content)
    digest = md5_hash.hexdigest()  # creates md5 hash STRING

    # start logging process
    fullDataRow = f + '\t' + f_new + '\t' + digest
    fullData.append(fullDataRow)

    if 'preprocessing' in f.lower():
        os.rename(f, 'zz_PreProcessingComplete.py')
    else:
        os.rename(f, f_new)

#    with concurrent.futures.ThreadPoolExecutor() as executor:
#        f1 = executor.submit(updatey)
#        print(f1.result())

    i += 1

lastSlash = scriptPath[len(scriptPath):1:-1].find('\\')
lastFolder = scriptPath[len(scriptPath)-lastSlash:len(scriptPath):1]

# 04. Take backup of file names and associated Last Modified Dates
with open(logPath + lastFolder + '-' +
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

end = time.time()
input(f'Script completed in {end-start:.1f} seconds. Press any key to continue')
