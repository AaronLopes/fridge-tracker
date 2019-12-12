import itertools
import numpy as np


from datetime import datetime, timedelta

class Reader:

    def __init__(self, dt):
        self.date = dt
        self.temperature = self.parse_temp(dt)
        self.pressue = self.parse_pres(dt)
        self.flow = self.parse_flow(dt)

    def parse_flow(self, date):
        """
        Parses Flowmeter file 
        :param date:
        :return:
        """
        flow_struct = {}
        try:
            data = np.loadtxt('./blue_fors_logs/' + date + '/Flowmeter ' + date +'.log', dtype=str, delimiter=',')
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
                    flow_struct[dt] = [data[j][2]]
        except Exception as e:
                print('Exception: ' + str(e))
                print('Flowmeter file missing on ' + date)

        return flow_struct

    def parse_temp(self, date):
        """
        Parses T (temperature, interchangeable with R/P) files and returns temperature values 
        for channels 1 - 6
        :param date: date in format 'yy-mm-dd' corresponding to log folders
        :return: datetime objects corresponding to values parsed, values, and missing channels
        :rtype: List
        """
        datetimes = [[], [], [], [], [], []]
        values = [[], [], [], [], [], []]
        missing_channels = []

        for i in range(6):
            try:
                data = np.loadtxt('./blue_fors_logs/' + date + '/CH' + str(i + 1)
                                  + ' T ' + date + '.log', dtype=str, delimiter=',')
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
                print('Exception: ' + str(e))
                print('Temperature file missing for CH' + str(i + 1) + ' on ' + date)
                missing_channels += [i]

        return self.restructure_data(datetimes, values, missing_channels)                

    def parse_pres(self, date):
        """
        Parses maxigauge files and returns pressure values for channels 1-6
        :param date: date in format 'yy-mm-dd' corresponding to log folders
        :param data_type: the file type of values to be parsed (T, K, P, etc.), should be in format ' X '
        :return: datetime objects corresponding to values parsed, values, and missing channels
        :rtype: List
        """
        datetimes = [[], [], [], [], [], []]
        values = [[], [], [], [], [], []]
        missing_channels = []
        try:
            data = np.loadtxt('./blue_fors_logs/' + date + '/maxigauge ' + date +'.log', dtype=str, delimiter=',')
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
                        print('encountered Exception: ' + str(e))
                        print('data missing on CH ' + j + 'at time' + time)
                        if j not in missing_channels:
                            missing_channels += [j]
        except Exception as e:
            print('Exception: ' + str(e))
            print('Maxigauge file missing for date: ' + date)

        return self.restructure_data(datetimes, values, missing_channels)                

    def restructure_data(self, datetimes, values, missing_ch):
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

        for i in range(6):
            if i not in missing_ch:
                date_val = np.array([datetimes[i], values[i]])
                date_val = date_val.transpose()
                date_val_ch[i] = date_val

        # create upload struct, put in '' for unavailable data
        upload_struct = dict((i, []) for i in flat_datetimes)
        for i in range(len(date_val_ch)):
            if i in missing_ch:
                #print('adding placeholders for missing CH' + str(i + 1) + '...')
                for k in upload_struct.keys():
                    upload_struct[k] += ['']
            else:
                #print('accessing CH' + str(i + 1))
                for j in range(len(date_val_ch[i])):
                    upload_struct[date_val_ch[i][j][0]] += [date_val_ch[i][j][1]]
                    
        return upload_struct

