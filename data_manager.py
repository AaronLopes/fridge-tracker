import gspread
import itertools
import numpy as np
import schedule
import threading
import time

from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

num_uploads = 0

scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file',
             'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)


def parse_temp(date, data_type, num_channels):
    """
    Parses values over given interval. Creates datetime array, values array, and identifies
    channels missing data.
    :param date: date in format 'yy-mm-dd' corresponding to log folders
    :param data_type: the file type of values to be parsed (T, K, P, etc.), should be in format ' X '
    :return: datetime objects corresponding to values parsed, values, and missing channels
    :rtype: lists
    """
    datetimes = [[], [], [], [], [], []]
    values = [[], [], [], [], [], []]
    missing_channels = []
    global num_uploads

    print('gathering data for upload number ' + str(num_uploads))
    for i in range(num_channels):
        try:
            data = np.loadtxt('./logs/' + date + '/CH' + str(i + 1)
                              + data_type + date + '.log', dtype=str, delimiter=',')
            n = len(data)
            for j in range(n):
                year = int(data[j][0][7:9]) + 2000
                month = int(data[j][0][4:6])
                day = int(data[j][0][1:3])
                hour = int(data[j][1][0:2])
                minute = int(data[j][1][3:5])
                second = int(data[j][1][6:8])
                dt = datetime(year, month, day, hour, minute, second)
                #interval = datetime.now() - timedelta(minutes=10)
                interval = datetime(17, 2, 28, 23, 49, 22)
                if dt >= interval:
                    datetimes[i] += [dt]
                    values[i] += [data[j][2]]
        except Exception as e:
            print('Error: ' + str(e))
            print('No data for channel ' + str(i + 1) + ' on ' + date)
            missing_channels += [i]
    num_uploads += 1
    return datetimes, values, missing_channels

def parse_maxigauge(date):
    """
    Parses maxigauge files and returns channels 
    :param date: date in format 'yy-mm-dd' corresponding to log folders
    :param data_type: the file type of values to be parsed (T, K, P, etc.), should be in format ' X '
    :return: datetime objects corresponding to values parsed, values, and missing channels
    :rtype: List
    """
    datetimes = [[], [], [], [], [], []]
    values = [[], [], [], [], [], []]
    missing_channels = []
    try:
        data = np.loadtxt('./logs/' + date + '/maxigauge ' + date +'.log', dtype=str, delimiter=',')
        for i in range(len(data)):
            time = data[i][1]
            for j in range(6):
                try:
                    year = int(date[0:2]) + 2000
                    month = int(date[3:5])
                    day = int(date[6:9]) 
                    hour = int(time[0:2])
                    minute = int(time[3:5])
                    second = int(time[6:9])
                    dt = datetime(year, month, day, hour, minute, second)
                    interval = datetime(17, 2, 28, 23, 49, 22)
                    if dt > interval:
                        values[j] += [data[i][j + 5*(j + 1)]]
                        datetimes[j] += [dt]
                except Exception as e:
                    print('Exception: ' + str(e))
                    print('data missing on CH ' + j + 'at time' + time)
                    if j not in missing_channels:
                        missing_channels += [j]
    except Exception as e:
        print('Error: ' + str(e))
        print('Maxigauge file missing for date: ' + date)
    return datetimes, values, missing_channels


def restructure_data(datetimes, values, missing_ch):
    date_val_ch = [[], [], [], [], [], []]

    dts = [[], [], [], [], [], []]
    vls = [[], [], [], [], [], []]

    if len(missing_ch) != 6:
        for i in range(6):
            dts[i] += datetimes[i]
            vls[i] += values[i]

    # reformat data, fills in 0 gaps in data
    for i in range(6):
        for j in range(1, len(values[i])):
            if float(values[i][j]) == 0.0 and float(values[i][j - 1]) != 0.0:
                vls[i][j] = values[i][j - 1]

    flat_datetimes = sorted(list(set(itertools.chain(*datetimes))))
    """
        upload_struct = {
            datetime.datetime(0,0,0,0,0,0) = [CH1 T, CH2 T, ..., CH6 T]
            .
            .
            datetime.datetime(0,0,0,0,0,0) = [CH1 T, CH2 T, ..., CH6 T]
        } 
    """

    for i in range(6):
        if i not in missing_ch:
            date_val = np.array([datetimes[i], values[i]])
            date_val = date_val.transpose()
            date_val_ch[i] = date_val

    print('dimensions: ')
    if len(date_val_ch) != 0:
        print(len(date_val_ch), len(date_val_ch[0]), len(date_val_ch[0][0]))
    else:
        print('no available data')

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


def upload_protocol(sheet_no, date, data_type):
    """

    :param sheet_no: sheet object corresponding to ustruct data (T, P, R, etc.)
    :param date: the current date to parse data
    :param type: the data type to parse (i.e. T = temperature, etc.)
    :return: boolean
    """
    client = gspread.authorize(creds)
    sheet = client.open('Fridge Data Testing').get_worksheet(sheet_no)
    
    if(data_type == ' T '):
        type_datetimes, type_values, type_missing_ch = parse_temp(date, data_type)    
    if(data_type == ' P '):
        type_datetimes, type_values, type_missing_ch = parse_maxigauge(date, data_type)    

    type_struct = restructure_data(type_datetimes, type_values, type_missing_ch) 
    # pressure_sheet = client.open('Fridge Data').get_worksheet(1)
    # resistance_sheet = client.open('Fridge Data').get_worksheet(2)

    print('uploading...')
    for key, val in type_struct.items():
        time.sleep(10)
        d = key.strftime('%m/%d/%y')
        t = key.strftime('%H:%M:%S')
        data = [d, t]
        data = data + val
        try:
            sheet.insert_row(data, 2)
        except gspread.exceptions as e:
            print('Error: ' + str(e))
            return False
    print('upload complete')
    return True


def main():
    # datetime.now().strftime('%y-%m-%d'), date = '17-02-28' for testing
    # maxigague contains all info for pressue values
    date = datetime.now().strftime('%y-%m-%d')
    # type param should be of format ' X '
    upload_threads = []
    types = [' T ', ' P ']
    num_processes = len(types)
    # add thread processes to thread list

    for i in range(num_processes):
        upload_threads += [threading.Thread(target=upload_protocol, args=(i, date, types[i], ))]
    # start threads
    for i in range(len(upload_threads)):
        upload_threads[i].start()

    # join threads
    for i in range(len(upload_threads)):
        upload_threads[i].join()


main()


# comment out scheduling block for testing
schedule.every(10).minutes.do(main)
while True:
    schedule.run_pending()
    time.sleep(1)
