import gspread
import matplotlib
import matplotlib.pyplot as pl
import numpy as np
import pprint

from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Fridge Data')

"""
GOOGLE SHEETS API INFO

spreadsheet data are type string 
sheet.insert_row(row, index)
sheet.delete()

"""

def get_date_T(date):
    datetimes = [[], [], [], [], [], []]
    values = [[], [], [], [], [], []]
    working_channels = []
    for i in range(6):
        try:
            data = np.loadtxt('./logs/' + date + '/CH' + str(i+1)
                              + ' T ' + date + '.log', dtype=str, delimiter=',')
            n = len(data)
            for j in range(n):
                year = int(data[j][0][7:9])
                month = int(data[j][0][4:6])
                day = int(data[j][0][1:3])
                hour = int(data[j][1][0:2])
                minute = int(data[j][1][3:5])
                second = int(data[j][1][6:8])
                datetimes[i] += [datetime(year, month, day, hour, minute, second)]
                values[i] += [data[j][2]]
            working_channels += [i]
        except Exception as e:
            print('No data for channel ' + str(i + 1) + ' on ' + date)
            print('Error:' + str(e))

    return datetimes, values, working_channels

# get current date
# datetime.now().strftime('%y-%m-%d'), current date for testing

date = '17-02-28'
datetimes = [[], [], [], [], [], []]
values = [[], [], [], [], [], []]
datetimes_temp, values_temp, working_channels = get_date_T(date)

if len(working_channels) is not 0:
    for i in range(6):
        datetimes[i] += datetimes_temp[i]
        values[i] += values_temp[i]

def merge_datetimes_temp(datetimes, values):
    pass


# fill in 0s in data
for i in range(6):
    print('T CH ' + str(i + 1))
    for j in range(1, len(values[i])):
        if float(values[i][j]) == 0.0 and float(values[i][j - 1]) != 0.0:
            values[i][j] = values[i][j - 1]
    """date_val = np.array([datetimes[i], values[i]])
    date_val = date_val.transpose()
    pprint.pprint('shape before transpose' + str(date_val.shape))
    pprint.pprint(date_val)"""
    print(datetimes[i])
    print(values[i])

if __name__ == 'main':

    """
    schedule inside while True: 
        every 10 minutes,
        get current datetime, parse log files at that date
        update on sheets
    """
    pass
