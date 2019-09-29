import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt

data = pd.read_csv(r'D:\微信\微信下载\WeChat Files\a13804425960\FileStorage\File\2019-08\ultimate\20170703.csv',header = None )
data = data.sort_values(by=[3] )
Car_Num = data.iloc[:, [2]] # 获取csv文件全部车牌号

CarPlate = Car_Num.values #把DataFrame转换为数组
Car_Plate = np.unique(CarPlate) # 去除相同车辆
print( Car_Plate )

CarPlateNum =0 #初始化车牌号数目

for car in Car_Plate:
    print('--------------------------------------------')
    car =str(car) #转换为字符串
    print (car)
    #Car= (car[2:-2])
    info=data.loc[data[2] == car ] # 提取data数据(筛选条件: 2列中指定车牌所在的行数据)
    infoArray = info.values  # 把DataFrame转换为数组
    info = pd.DataFrame(infoArray)
    print(info)  #同一车不同时间段的信息
    Passenger = info.iloc[:, [7]] # 获取同一车不同时间乘客是否在车上
    #print (Passenger)
    PassengerArray = Passenger.values  # 把DataFrame转换为数组
    Passenger = pd.DataFrame(PassengerArray)
    #print(Passenger)  #
    #print(PassengerArray)  #
    try:
        for i in range(len(PassengerArray)):
            print(PassengerArray[i])
            if (PassengerArray[i] == [0]) & (PassengerArray[i+1] == [1]):#由0变1，上车  0为上车
                df = info.iloc[[i,i+1], [ 4, 5, 6]]
                dfArray = df.values
                a = np.mean(dfArray, 0)
                #df = pd.DataFrame(a).T
                info.iat[i,4] = a[0]
                info.iat[i, 5] = a[1]
                info.iat[i, 6] = a[2]
                #info.iat[i, 7] = a[3]
                df = info.iloc[[i],[2,3,4,5,6,7]]
                print(df)
                #df.to_csv('D:\\坐标20170709.csv', mode='a', sep=',', header=False, index=False)
                print(')))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))')
            if (PassengerArray[i] == [1]) & (PassengerArray[i+1] == [0]):#由1变0，下车  1为下车
                df = info.iloc[[i, i + 1], [4, 5, 6]]
                dfArray = df.values
                a = np.mean(dfArray, 0)
                #df = pd.DataFrame(a).T
                info.iat[i, 4] = a[0]
                info.iat[i, 5] = a[1]
                info.iat[i, 6] = a[2]
                # info.iat[i, 7] = a[3]
                df = info.iloc[[i], [2, 3, 4, 5, 6, 7]]
                print(df)
                #df.to_csv('D:\\坐标20170709.csv', mode='a', sep=',', header=False, index=False)
                print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    except IndexError:
        print('此辆车在此时间段无乘客')
    except IOError:
        print('写不了')

    CarPlateNum = CarPlateNum + 1
    print(str(CarPlateNum)+'辆车')
    print ('*******************************************')

