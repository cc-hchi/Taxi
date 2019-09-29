import os
import shutil

import numpy as np
import pandas as pd
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
    # print([str(i) for i in df.index])
    # print(df)
    # fig1 = plt.figure()
    # ax = fig1.add_subplot(1, 1, 1)
    # print(df.index)
    # print(plt.xticks())


# num_on_off_day()
# num_on_off_hours()
plot_on()