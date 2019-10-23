import gspread
import itertools
import numpy as np
import schedule
import time

from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

num_uploads = 0


def parse_file(date, type, interval):
    """
    Parses values over given interval. Creates datetime array, values array, and identifies
    channels missing data.   
    :param date: date in format 'yy-mm-dd' corresponding to log folders
    :param type: the file type of values to be parsed (T, K, P, etc.), should be in format ' X '
    :param interval:
    :return: datetime objects corresponding to values parsed, values, and missing channels
    :rtype: lists
    """
    datetimes = [[], [], [], [], [], []]
    values = [[], [], [], [], [], []]
    missing_channels = []
    global num_uploads

    print('gathering data for upload number ' + str(num_uploads))
    for i in range(6):
        try:
            data = np.loadtxt('./logs/' + date + '/CH' + str(i + 1)
                              + type + date + '.log', dtype=str, delimiter=',')
            n = len(data)
            for j in range(n):
                year = int(data[j][0][7:9]) + 2000
                month = int(data[j][0][4:6])
                day = int(data[j][0][1:3])
                hour = int(data[j][1][0:2])
                minute = int(data[j][1][3:5])
                second = int(data[j][1][6:8])
                dt = datetime(year, month, day, hour, minute, second)
                interval = datetime.now() - timedelta(minutes=interval)
                if dt >= interval:
                    datetimes[i] += [dt]
                    values[i] += [data[j][2]]
        except Exception as e:
            print('Error: ' + str(e))
            print('No data for channel ' + str(i + 1) + ' on ' + date)
            missing_channels += [i]
    num_uploads += 1
    return datetimes, values, missing_channels


def restruct_data(datetimes, values, missing_ch):
    date_val_ch = [[], [], [], [], [], []]

    dts = [[], [], [], [], [], []]
    vls = [[], [], [], [], [], []]

    if len(missing_ch) is not 6:
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


def upload_protocol(ustruct, sheet_no):
    """
    Given the proper upload data structure and sheet number, parses through values
    and uploads them to corresponding Google Sheets. Visit https://tinyurl.com/y6ppy543 to view.
    :param ustruct: dictionary of properly formatted values and datetimes
    :param sheet_no: sheet object corresponding to ustruct data (T, K, P, etc.)
    :return: boolean
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file',
             'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('Fridge Data').get_worksheet(sheet_no)

    # pressure_sheet = client.open('Fridge Data').get_worksheet(1)
    # resistance_sheet = client.open('Fridge Data').get_worksheet(2)

    print('uploading...')
    for key, val in ustruct.items():
        time.sleep(2)
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
    # datetime.now().strftime('%y-%m-%d'), date for testing
    date = datetime.now().strftime('%y-%m-%d')

    temp_datetimes, temp_values, temp_missing_ch = parse_file(date, ' T ', 10)
    pres_datetimes, pres_values, pres_missing_ch = parse_file(date, ' P ', 10)

    temp_struct = restruct_data(temp_datetimes, temp_values, temp_missing_ch)
    pres_struct = restruct_data(pres_datetimes, pres_values, pres_missing_ch)

    # temporary, multithreading must be implemented for simultaneous uploading
    if not upload_protocol(temp_struct, 0):
        print('error uploading temperature values')
    if not upload_protocol(pres_struct, 1):
        print('error uploading pressure values')


main()

# comment out scheduling block for testing
schedule.every(10).minutes.do(main)
while True:
    schedule.run_pending()
    time.sleep(1)
