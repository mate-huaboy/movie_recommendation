"""
功能：去重，去掉已读，热门补足等措施，概率保证多样性

"""
import numpy as np

import GlobalFun
from recommendationAlogrithm.hotRecommendation import hotRecommendation


class adjust:
    def __init__(self,userid):
        self.userhavesee=self.getuserhavesee(userid)#用户已经看的电影列表
    def removeAndAddHot(self,prolist_id,num):
        """去掉重复，已读的，不足的热门补足，返回推荐列表"""
        recmlist=[]
        haveseelist=self.userhavesee
        prolist_id=set(prolist_id)-set(haveseelist)#有一点不好，因为去掉了排序特征
        k=0
        for id in prolist_id:
           # if id not in recmlist and id not in haveseelist:
           if id not in recmlist:
                recmlist.append(id)
                k=k+1
                if k==num:
                    return recmlist
        #热门补足：
        hotrec = hotRecommendation()
        hotrecrecmlist = hotrec.gethotmovie(num-k,recmlist)
        recmlist.extend(hotrecrecmlist)
        return recmlist

    def select(self,prolist,num):#但去掉了排序特征
        """以一定概率选取出num个,只返回电影id的列表"""
        #判断prolist长度，如果小于等于num则直接转成目标格式返回
        recmlist = []
        if len(prolist)<=num:
            for p in prolist:
                recmlist.append(p[0])
            return recmlist
        #否则
        r = {}
        s=0
        #得到各个元素的比例
        for p in prolist:
            s=s+p[1]
        s1=0
        for p in prolist:
            s1=s1+p[1] / s
            r[p[0]] = s1
        #产生0到1的随机数选择出num个电影
        count=0
        while True:
            ran=np.random.random()
            for rk in r.keys():
                if r[rk]>ran:
                    recmlist.append(rk)
                    count=count+1
                    break
            if count==num:
                return recmlist#返回即可


    def getuserhavesee(self,userid):
        sql=['SELECT movieid FROM dbmovierecommender.ratings where userid={}'.format(userid)]
        conn, cur = GlobalFun.ConnectSql()
        cur.execute(sql[0])
        userhavesee =[]
        data=cur.fetchall()
        GlobalFun.Closesql(conn, cur)
        for d in data:
            userhavesee.append(d[0])

        return userhavesee

