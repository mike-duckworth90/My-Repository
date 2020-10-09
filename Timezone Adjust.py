import os
import sys
import re
from datetime import datetime, timedelta

logPath = 'C:\\Users\\Mike_\\OneDrive\\My Media\\Media to Sort\\Rename Logs\\'

scriptPath = os.path.dirname(sys.argv[0])
#scriptPath = 'C:\\Users\\Mike_\\OneDrive\\Documents\\My Projects\\Project Big Media Database\\Rename Testing\\testing'

os.chdir(scriptPath)
cwd = os.getcwd()
files = os.listdir(cwd)

roll = input('How many hours do you want to roll forward (negative number for roll back): ')

while not (roll.lstrip('-+')).isnumeric():
    roll = input(
        'How many hours do you want to roll forward (negative number for roll back): ')


for f in files:
    f_core = os.path.splitext(f)[0]
    f_ext = os.path.splitext(f)[1]
    if re.search(
            r'20[0-9]{2}-[0-1][0-9]-[0-3][0-9] [0-2][0-9].[0-5][0-9].[0-5][0-9]', f[:19]):
        prise_de_vue = str(datetime.strptime(f[:19], '%Y-%m-%d %H.%M.%S') + timedelta(hours=int(roll))).replace(':', '.')
        
        if len(f) < 20:
            f = f + '.extension'

        f_new = prise_de_vue + ' ' + f[20::]
        os.rename(f, f_new)
