import numpy as np
import matplotlib.pyplot as pl
import matplotlib
import datetime


def get_date_T(date):
    datetimes = [[], [], [], [], [], []]
    values = [[], [], [], [], [], []]
    working_channels = []
    for i in range(0, 6):
        try:
            data = np.loadtxt('./logs/' + date + '/CH' + str(i + 1)
                              + ' T ' + date + '.log', dtype=str, delimiter=',')
            n = len(data)
            for j in range(n):
                year = int(data[j][0][7:9])
                month = int(data[j][0][4:6])
                day = int(data[j][0][1:3])
                hour = int(data[j][1][0:2])
                minuite = int(data[j][1][3:5])
                second = int(data[j][1][6:8])
                datetimes[i] += [datetime.datetime(year, month, day,
                                                   hour, minuite, second)]
                values[i] += [data[j][2]]
            working_channels += [i]
        except:
            print('No data for channel ' + str(i + 1) + ' on ' + date)
    return datetimes, values, working_channels


def increment_date(date):
    year, month, day = int(date[0:2]), int(date[3:5]), int(date[6:8])
    new_date = (datetime.date(year, month, day)
                + datetime.timedelta(days=1))
    return (str(new_date.year).zfill(2) + '-'
            + str(new_date.month).zfill(2) + '-'
            + str(new_date.day).zfill(2))


date = str(input('Start date (yy-mm-dd): '))
end_date = str(input('End date (same if blank): '))
if (end_date == ''):
    end_date = date

datetimes = [[], [], [], [], [], []]
values = [[], [], [], [], [], []]

datetimes_temp, values_temp, working_channels = get_date_T(date)
if len(working_channels) is not 0:
    for i in range(6):
        datetimes[i] += datetimes_temp[i]
        values[i] += values_temp[i]

miss = 0
while date != end_date and miss < 5:
    datetimes_temp, values_temp, working_channels = get_date_T(date)
    if (len(working_channels) == 0):
        miss += 1
    else:
        for i in range(6):
            datetimes[i] += datetimes_temp[i]
            values[i] += values_temp[i]
        miss = 0
    date = increment_date(date)

for i in range(6):
    for j in range(1, len(values[i])):
        if (float(values[i][j]) == 0.0 and float(values[i][j - 1]) != 0.0):
            values[i][j] = values[i][j - 1]
    date_val = np.array([datetimes[i], values[i]])
    date_val = date_val.transpose()
    print(date_val.shape)
    print('T CH ' + str(i + 1))
    print(date_val)
    pl.plot_date(matplotlib.dates.date2num(datetimes[i]), values[i], '.', label='T CH ' + str(i + 1))

print(min(values[0]), min(values[5]))

pl.xlabel('time (hrs)')
pl.legend()
fig = pl.gcf()
ax = pl.gca()
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d/%m/%Y %H:%M'))
ax.autoscale_view()
fig.autofmt_xdate()
ax.set_yscale("log", nonposy='clip')
fig.set_size_inches(10, 10)
fig.savefig('./plots/' + date + '_all.png', dpi=100)
pl.show()
