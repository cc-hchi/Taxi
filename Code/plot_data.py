import os
import shutil

import numpy as np
import pandas as pd
from dateutil.parser import parse
from pandas.tseries.offsets import Hour
import matplotlib.pyplot as plt


columns = ['company', 'id', 'card', 'timestamp', 'longitude', 'latitude', 'unknown1', 'status', 'unknown3',
           'direction', 'unknown5']  # 文件中每一列所对应的信息
columns2 = ['card', 'timestamp', 'longitude', 'latitude', 'speed', 'is_off']


def num_on_off_day():
    '''
    对每一天的上下车次数进行统计
    :return:
    '''
    res_df = pd.DataFrame(np.zeros([2, 7]), index=['on', 'off'],
                          columns=[str(i) for i in range(20170703, 20170710)])  # 建立一张数值全为0的表格
    # print(res_df)
    for date in os.listdir('./data/坐标/'):
        df = pd.read_csv('./data/坐标/' + date, names=columns2, header=None)
        res_df[date.split('.')[0]]['on'] = len(df[df['is_off'] == 0])
        res_df[date.split('.')[0]]['off'] = len(df[df['is_off'] == 1])
    print(res_df)


def num_on_off_hours():
    '''
    对每一天的每小时的上下车次数进行统计
    :return:
    '''
    root_path = './data/每小时上下车次数统计/'
    if os.path.exists(root_path):
        shutil.rmtree(root_path)
    os.mkdir(root_path)
    for date in os.listdir('./data/坐标'):
        df = pd.read_csv('./data/坐标/' + date, header=None, names=columns2)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        res_df = pd.DataFrame(np.zeros([24, 2]), columns=['on', 'off'])
        for hour in range(24):
            # s1 = pd.Series([ele.hour for ele in df['timestamp']]) == hour
            # s2 = df['is_off'] == 0
            # print(s1 & s2)
            # print(df['is_off'] == 0)
            # print(pd.Series([ele.hour for ele in df['timestamp']]) == hour)
            res_df['on'][hour] = len(df[(df['is_off'] == 0) &
                                     (pd.Series([ele.hour for ele in df['timestamp']]) == hour)])
            res_df['off'][hour] = len(df[(df['is_off'] == 1) &
                                      (pd.Series([ele.hour for ele in df['timestamp']]) == hour)])
        res_df.to_csv(root_path + date)


def plot_on():
    '''
    画出每天的上车次数频率随时间的变化图
    :return:
    '''
    df = pd.DataFrame([], index=pd.timedelta_range('00:00:00', periods=24, freq='1h'))
    for date in os.listdir('./data/每小时上下车次数统计/'):
        sub_df = pd.read_csv('./data/每小时上下车次数统计/' + date)
        # sub_series = pd.Series(sub_df.values,
        #                        index=pd.timedelta_range('00:00:00', periods=24, freq='1h'))
        # sub_df = sub_df.reindex(pd.timedelta_range('00:00:00', periods=24, freq='1h'))
        df[date.split('.')[0]] = sub_df['on'].values
        # print(sub_df)
    df.plot()
    plt.grid(True)
    plt.title('Frequency of Taking on among a day')
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    times = [str(i)+'~'+str(i+1) for i in range(24)]
    plt.xticks([9e13/24*i for i in range(24)], times, rotation=90)
    # plt.savefig('../Taxi/Figures/每天上车次数折线图1.png')
    # print([str(i) for i in df.index])
    # print(df)
    # fig1 = plt.figure()
    # ax = fig1.add_subplot(1, 1, 1)
    # print(df.index)
    # print(plt.xticks())


def plot_off():
    '''
    画出每天的下车次数频率随时间的变化图
    :return:
    '''
    df = pd.DataFrame([], index=pd.timedelta_range('00:00:00', periods=24, freq='1h'))
    for date in os.listdir('./data/每小时上下车次数统计/'):
        sub_df = pd.read_csv('./data/每小时上下车次数统计/' + date)
        df[date.split('.')[0]] = sub_df['off'].values
    df.plot()
    plt.grid(True)
    plt.title('Frequency of Taking off among a day')
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    times = [str(i)+'~'+str(i+1) for i in range(24)]
    plt.xticks([9e13/24*i for i in range(24)], times, rotation=90)


def empty_describe():
    '''
    各时段空驶率统计
    '''
    res_df = pd.DataFrame(np.zeros([24, 7]), columns=[date.split('.')[0] for date in os.listdir('./data/坐标/')])
    for date in os.listdir('./data/坐标/'):
        df = pd.read_csv('./data/坐标/'+date, header=None, names=columns2)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        for hour in range(24):
            empty = pd.to_datetime(0)-pd.to_datetime(0)

            # sum_time = empty
            # for card, time in df['timestamp'].groupby(df['card']):
            #     # print(time)
            #     # print(time.iloc[-1])
            #     # print(time[0].hour)
            #     if hour >= time.iloc[0].hour & hour <= time.iloc[-1].hour:
            #         sum_time += Hour(1)
            #     if hour == time.iloc[0].hour:
            #         sum_time -= time.iloc[0] - parse(str(time.iloc[0]).split(' ')[0] + ' '+str(hour)+':00:00')
            #     if hour == time.iloc[-1].hour:
            #         sum_time -= parse(str(time.iloc[-1]).split(' ')[0]
            #                           + ' '+str(hour)+':00:00') + Hour(1) - time.iloc[-1]

            for it in range(len(df.index)):
                # if ((it == 0) | (df['card'][it] != df['card'][it-1])) & (df['is_off'][it] == 0):
                #     empty = empty + df['timestamp'][it]
                if (df['timestamp'][it].hour == hour) & (df['is_off'][it] == 1):
                    # 在这里认为同一辆车的最后一个乘客下车后便结束运营，于是不计
                    # print(it)
                    # print(df.index)
                    if it < len(df.index)-1:
                        if df['card'][it+1] == df['card'][it]:
                            if df['timestamp'][it+1] != hour:
                                empty = empty + parse(str(df['timestamp'][it]).split(' ')[0]
                                                      + ' '+str(hour)+':00:00') + Hour(1) - df['timestamp'][it]
                            else:
                                empty = empty + df['timestamp'][it+1] - df['timestamp'][it]

            no_empty = pd.to_datetime(0) - pd.to_datetime(0)
            for it in range(len(df.index)):
                if (df['timestamp'][it].hour == hour) & (df['is_off'][it] == 0):
                    if it < len(df.index)-1:
                        if df['card'][it+1] == df['card'][it]:
                            if df['timestamp'][it+1] != hour:
                                no_empty = no_empty + parse(str(df['timestamp'][it]).split(' ')[0]
                                                      + ' '+str(hour)+':00:00') + Hour(1) - df['timestamp'][it]
                            else:
                                no_empty = no_empty + df['timestamp'][it+1] - df['timestamp'][it]
            # print(empty)
            # print(no_empty)
            # print()
            # print(sum_time)
            res_df[date.split('.')[0]][hour] = empty / (empty+no_empty)
    # print(res_df)
    res_df.to_csv('./data/各时段空驶率统计.csv')

# num_on_off_day()
# num_on_off_hours()
# plot_on()
# plot_off()
empty_describe()
