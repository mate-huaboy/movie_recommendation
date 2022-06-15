import math

import numpy as np
import pymysql

def ConnectSql():
    conn = pymysql.connect(host="localhost",port=3306,user='root',password="a123456")
    cur = conn.cursor()#生成游标对象
    return conn,cur

def Closesql(conn,cur):
    cur.close()
    conn.close()
    return


 # 计算相似度
        # 获取用户对item的喜好程度
def cosUI(user, item):
    # 通过余弦相似度
    # Uia 分子 Ua（用户对电影的偏好矩阵） Ia（电影类型的特征信息矩阵）电影shi否属于类型a
    Uia = sum(
        np.array(user)
        *
        np.array(item)
    )
    Ua = math.sqrt(sum([math.pow(one, 2) for one in user]))  # 分母 Ua
    Ia = math.sqrt(sum([math.pow(one, 2) for one in item]))  # 分母 Ia
    return Uia / (Ua * Ia)