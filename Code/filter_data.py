import os
import shutil
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

columns = ['company', 'id', 'card', 'timestamp', 'longitude', 'latitude', 'unknown1', 'status', 'unknown3',
           'direction', 'unknown5']  # 文件中每一列所对应的信息


def merge_data():
    """
    将每天的数据整合进一个csv文件中
    原始数据在data文件夹下
    整合后数据存放在after下，以日期命名

    在后续的处理中发现有不合理的数据，于是修改此函数将其过滤并重新保存为新的文件
    """
    data_folder = './data/'
    save_folder = data_folder + 'after/'
    drop_path = save_folder + 'dropped_data.csv'

    if os.path.exists(save_folder):
        # 删除原有文件
        shutil.rmtree(save_folder)
    os.mkdir(save_folder)

    for date in os.listdir(data_folder)[:-1]:
        data_base_path = data_folder + date + '/'
        df = pd.DataFrame()
        for data in os.listdir(data_base_path):
            # 将每一个该日期的数据文件放入同一个DataFrame中
            sub_df = pd.read_csv(data_base_path + data, header=None, names=columns, parse_dates=['timestamp'])
            # print(sub_df.head()['timestamp'])

            # 筛选出不在当天日期内的数据
            drop_df = sub_df[(sub_df['timestamp'] < datetime.strptime(date, '%Y%m%d')) |
                             (sub_df['timestamp'] > (datetime.strptime(date, '%Y%m%d') + pd.Timedelta('1d')))]
            # print(date, drop_df.head()['timestamp'])
            # 将不符合当天日期的数据存放在./data/after/dropped_data.csv中
            drop_df.to_csv(drop_path, header=False, index=False, mode='a+')
            sub_df = sub_df[(sub_df['timestamp'] > datetime.strptime(date, '%Y%m%d')) &
                            (sub_df['timestamp'] < (datetime.strptime(date, '%Y%m%d') + pd.Timedelta('1d')))]
            df = pd.concat([df, sub_df], axis=0)
        df = df.drop_duplicates().dropna()  # 去除重复记录和无效值
        # print(date, df['timestamp'].max(), df['timestamp'].min())
        # 原始数据：
        # 20170703 2017-07-03 23:25:50 1999-11-30 00:00:00
        # 20170704 2017-07-04 23:24:08 1943-12-01 01:32:22
        # 20170705 2017-07-05 23:18:25 1999-11-30 00:00:00
        # 20170706 2017-07-06 23:23:56 1943-12-01 01:31:52
        # 20170707 2017-07-07 23:25:56 1943-12-01 01:31:52
        # 20170708 2017-07-08 23:21:37 1943-12-01 01:31:52
        # 20170709 2017-07-09 23:13:10 1943-12-01 01:32:52

        df.to_csv(save_folder + date + '.csv', index=False, header=False)  # 保存在指定文件夹中


# def read_data(date):
#     """
#     从经过处理后的指定的日期文件中读取数据
#     :param date: 字符串，想要读取的日期的文件，格式范例为:'20170703'
#     :return: pd.DataFrame对象，包含指定文件中的数据
#     """
#     # df = pd.read_csv('./data/after/' + date + '.csv', header=None, names=columns, index_col='timestamp')
#     df = pd.read_csv('./data/after/' + date + '.csv', header=None, names=columns)
#     # print(df.head()['timestamp'])
#     df['timestamp'] = pd.to_datetime(df['timestamp'])
#     return df


def read_data(filename):
    """
    由于后续的改进，重写了这个函数
    从经过处理后的指定的日期文件中读取数据
    :param filename: 字符串，想要读取的文件
    :return: pd.DataFrame对象，为指定文件中的数据
    """
    df = pd.read_csv(filename, header=None, names=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def extract_Haidian():
    """
    将after里属于海淀区的数据提取出来，以日期命名放入after2Haidian文件夹中
    """

    # 这里将海淀区的经度范围认为是116°03′—116°23′，纬度范围是39°53′—40°09′
    min_longitude, max_longitude = 116 + 3 / 60.0, 116 + 23 / 60.0
    min_latitude, max_latitude = 39 + 53 / 60.0, 40 + 9 / 60.0
    # print(min_longitude)

    after2Haidian_folder = './data/after2Haidian/'

    if os.path.exists(after2Haidian_folder):
        shutil.rmtree(after2Haidian_folder)
    os.mkdir(after2Haidian_folder)
    for date in os.listdir('./data')[:-2]:
        df = pd.read_csv('./data/after/' + date + '.csv', header=None, names=columns)

        dropped_df = df[(df['longitude'] < min_longitude) | (df['longitude'] > max_longitude) |
                        (df['latitude'] < min_latitude) | (df['latitude'] > max_latitude)]
        dropped_df.to_csv('./data/after2Haidian/dropped_data.csv', header=False, index=False, mode='a+')

        df = df[(df['longitude'] >= min_longitude) & (df['longitude'] <= max_longitude) &
                (df['latitude'] >= min_latitude) & (df['latitude'] <= max_latitude)]
        # print(df['latitude'].max(), df['latitude'].min(), df['longitude'].max(), df['longitude'].min())
        df.to_csv('./data/after2Haidian/' + date + '.csv', header=False, index=False)


def dropped_unchange():
    """
    从after2Haidian的数据里去除全天的经纬度无变化或者载客状态无变化的车辆数据，
    存入./data/ultimate中
    """
    if os.path.exists('./data/ultimate'):
        shutil.rmtree('./data/ultimate')
    os.mkdir('./data/ultimate')
    for file in os.listdir('./data/after')[:-1]:
        dropped_card = []
        df = pd.read_csv('./data/after/' + file, header=None, names=columns)
        # print(df['status'].groupby(df['card']).count())
        for card, series in df['status'].groupby(df['card']):
            # print(card, series)
            series = series.drop_duplicates()
            if len(series) == 1:
                dropped_card.append(card)
        for card, sub_df in df.loc[:, ['longitude', 'latitude']].groupby(df['card']):
            sub_df = sub_df.drop_duplicates()
            if len(sub_df.index) == 1:
                dropped_card.append(card)
        dropped_card = set(dropped_card)
        dropped_df = df[df['card'].apply(lambda x: x in dropped_card)]
        dropped_df.to_csv('./data/ultimate/dropped_data.csv', header=False, index=False, mode='a+')
        df = df[df['card'].apply(lambda x: x not in dropped_card)]
        df.to_csv('./data/ultimate/' + file, header=False, index=False)


def basic_describe():
    for date in os.listdir('./data/ultimate'):
        df = read_data('./data/ultimate/' + date)
        grouped = df.groupby(df['card'])
        count = 0
        for _, __ in grouped:
            count = count + 1
        print(date.split('.')[0], count, df.shape)


# basic_describe()


# def plot_all(df, new_columns):
#     """
#     画出指定的DataFrame的指定列的图形矩阵，存入'./img/当中'
#     :param df: 传入的DataFrame
#     :param new_columns: 想要画的列组成的列表
#     """
#     df = df.iloc[:, [columns.index(x) for x in new_columns]]
#     # print(df.head())
#     plt.show()

# merge_data()

# df = read_data('20170703')
# print(df['latitude'].max(), df['latitude'].min(), df['longitude'].max(), df['longitude'].min())
# # 原始数据：
# # 2147.483648 0.0 2147.483648 0.0
# # extract_Haidian()

# df = read_data('./data/after2Haidian/20170703.csv')
# print(df['status'].max(), df['status'].min(),  df['direction'].max(), df['direction'].min())
# # 1 0 255 0
# status和方向都处在正常范围之内，无需过滤

# df = read_data('./data/after2Haidian/20170703.csv')
# print(df.groupby(by='card').count())

# print(df.__len__())  output: 1919595
# print(df.iloc[1789509])
# print(df[df['timestamp'] == datetime(1999, 11, 30, 0, 0, 0)]['timestamp'])  # index=1789509
# plot_all(df, ['timestamp', 'unknown2'])
# plt.scatter(df['timestamp'], df['unknown2'])
# plt.xticks(pd.date_range(start='20170703', end='20170704', freq='h'))
# plt.show()

# dropped_unchange()
