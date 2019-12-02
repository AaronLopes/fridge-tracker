import gspread
#import schedule
import threading
import time

from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from parser import Parser


num_uploads = 0

scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file',
             'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)


def upload_protocol(sheet_no, data_struct):
    """
    thread function which parses through data dictionary of datetime-value pairs and uploads 
    values to Google Sheets
    :param sheet_no: sheet object corresponding to ustruct data (T, P, R, etc.)
    :param date: the current date to parse data
    :param type: the data type to parse (i.e. T = temperature, etc.)
    :return: boolean
    """
    global num_uploads
    client = gspread.authorize(creds)
    sheet = client.open('Fridge Data Testing').get_worksheet(sheet_no)
    
    print('uploading...')
    for key, val in data_struct.items():
        time.sleep(7)
        d = key.strftime('%m/%d/%y')
        t = key.strftime('%H:%M:%S')
        data = [d, t]
        data += val
        try:
            sheet.insert_row(data, 2, value_input_option='USER_ENTERED')
        except gspread.exceptions as e:
            print('Exception: ' + str(e))
            return False
    print('upload number ' + num_uploads + ' completed')
    return True

def main():
    # datetime.now().strftime('%y-%m-%d'), date = '17-02-28' for testing
    # maxigague contains all info for pressue values
    #date = datetime.now().strftime('%y-%m-%d')
    date = '17-02-28'
    upload_threads = []
    p = Parser(date)
    data_structs = [p.temperature, p.pressue, p.flow]
    
    # add thread processes to thread list

    for i in range(len(data_structs)):
        upload_threads += [threading.Thread(target=upload_protocol, args=(i, data_structs[i], ))]
    # start threads
    for i in range(len(upload_threads)):
        upload_threads[i].start()

    # join threads
    for i in range(len(upload_threads)):
        upload_threads[i].join()

main()
# comment out scheduling block for testing
"""
schedule.every(10).minutes.do(main)
while True:
    schedule.run_pending()
    time.sleep(1)
"""