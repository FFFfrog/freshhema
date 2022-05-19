# -*- coding: utf-8 -*-
# @Author  : 袁天琪
import requests


def ExcuteSingleQuery(locationList, currentkey):
    # 1-将locationList中的地址连接成高德地图API能够识别的样子
    locationString = ""  # 当前locationList组成的string
    for location in locationList:
        locationString += location + '|'
    # 2-地理编码查询需要的Url
    output = 'json'  # 查询返回的形式
    batch = 'true'  # 是否支持多个查询
    base = 'https://restapi.amap.com/v3/geocode/geo?'  # 地理编码查询Url的头
    currentUrl = base + "output=" + output + "&batch=" + batch + "&address=" + locationString + "&key=" + currentkey
    # 3-提交请求
    response = requests.get(currentUrl)  # 提交请求
    answer = response.json()  # 接收返回
    # 4-解析Json的内容
    resultList = []  # 用来存放地理编码结果的空序列
    if answer['status'] == '1' and answer['info'] == 'OK':
        # 4.1-请求和返回都成功，则进行解析
        tmpList = answer['geocodes']  # 获取所有结果坐标点
        for i in range(0, len(tmpList)):
            try:
                # 解析','分隔的经纬度
                coordString = tmpList[i]['location']
                coordList = coordString.split(',')
                # 放入结果序列
                resultList.append((float(coordList[0]), float(coordList[1])))
            except:
                # 如果发生错误则存入None
                resultList.append(None)
        return resultList
    elif answer['info'] == 'DAILY_QUERY_OVER_LIMIT':
        # 4.2-当前账号的余额用完了,返回-1
        return -1
    else:
        # 4.3-如果发生其他错误则返回-2
        return -2
