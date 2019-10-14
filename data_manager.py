import gspread
import itertools
import numpy as np
import time

from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

"""
GSPREAD API REF

spreadsheet data type string 
sheet.insert_row(values, index=1, value_input_option='RAW'),
pushes current content down 
sheet.delete()

"""


def get_date_T(date):
    datetimes = [[], [], [], [], [], []]
    values = [[], [], [], [], [], []]
    missing_channels = []
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
        except Exception as e:
            print('Error: ' + str(e))
            print('No data for channel ' + str(i + 1) + ' on ' + date)
            missing_channels += [i]
    return datetimes, values, missing_channels


def merge_datetimes_temp(datetimes, values, missing_ch):
    date_val_ch = [[], [], [], [], [], []]

    # flatten needs to be fixed, datetimes not ordered
    flat_datetimes = sorted(list(set(itertools.chain(*datetimes))))

    for i in range(6):
        if i not in missing_ch:
            date_val = np.array([datetimes[i], values[i]])
            date_val = date_val.transpose()
            date_val_ch[i] = date_val

    print('dimensions: ')
    print(len(date_val_ch), len(date_val_ch[0]), len(date_val_ch[0][0]))
    """
    upload_struct = {
        datetime.datetime(0,0,0,0,0,0) = [CH1 T, CH2 T, ..., CH6 T]
        .
        .
        datetime.datetime(0,0,0,0,0,0) = [CH1 T, CH2 T, ..., CH6 T]
    } 
    """
    upload_struct = dict((i, []) for i in flat_datetimes)
    for i in range(len(date_val_ch)):
        if i in missing_ch:
            print('adding placeholders for missing CH' + str(i + 1))
            for k in upload_struct.keys():
                upload_struct[k] += ['N/A']
        else:
            print('accessing CH' + str(i + 1))
            for j in range(len(date_val_ch[i])):
                upload_struct[date_val_ch[i][j][0]] += [date_val_ch[i][j][1]]
    return upload_struct


def upload_protocol(ustruct, spreadsheet):
    print('uploading...')
    for key, val in ustruct.items():
        time.sleep(2)
        d = key.strftime('%m/%d/%y')
        t = key.strftime('%H:%M:%S')
        data = [d, t]
        data = data + val
        spreadsheet.insert_row(data, 2)
    print('upload complete')


if __name__ == '__main__':
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file',
             'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('Fridge Data').sheet1

    # get current date
    # datetime.now().strftime('%y-%m-%d'), date for testing
    date = '17-02-28'
    datetimes = [[], [], [], [], [], []]
    values = [[], [], [], [], [], []]

    datetimes_temp, values_temp, missing_channels = get_date_T(date)

    if len(missing_channels) is not 6:
        for i in range(6):
            datetimes[i] += datetimes_temp[i]
            values[i] += values_temp[i]

    # fill in 0s in data
    for i in range(6):
        for j in range(1, len(values[i])):
            if float(values[i][j]) == 0.0 and float(values[i][j - 1]) != 0.0:
                values[i][j] = values[i][j - 1]

    to_upload = merge_datetimes_temp(datetimes, values, missing_channels)
    upload_protocol(to_upload, sheet)

