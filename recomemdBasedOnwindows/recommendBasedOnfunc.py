"""
功能：根据不同界面提出的推荐请求，结合当前的用户状态，电影的状态，综合推荐策略
关键词：冷启动，综合推荐策略，去重
难点：冷启动问题，策略之间的综合
分析：冷启动问题：对用户而言，当用户为新用户时，由于评分量过少，所以协同过滤和基于内容的得到的用户画像往往不够准确，因而需要判断用户的状态，给出适当的推荐组合
对于电影而言，当一部新电影入驻，为其评分的电影人数又很少了，此时协同过滤得到的电影画像又没有太多参考价值，另一方面，又希望刚刚上新的电影能够快速传播开来，
对于新电影，可以根据基于内容的推荐算法一步步快速推荐给用户，使其传播量达到一定程度，便可以又综合使用协同过滤的推荐了。
以上问题难点：对电影和用户状态的评估以及状态转换的规则--可能用到的知识：马尔科夫链
"""
import math
import time

import GlobalFun
from recomemdBasedOnwindows.adjust import adjust

#这里直接和数据库交互得到想要的推荐列表，而不是调用推荐算法--在线推荐除外
from recommendationAlogrithm.hotRecommendation import hotRecommendation
from recommendationAlogrithm.recommendOnline import recomendOnline


class recommendBasedOnfunc:

    def __init__(self,userid):
        self.userid=userid
        self.adjust=adjust(userid)
        self.r1_offline = 0.25
        self.r1_als = 0.75
        self.sagma = 20
        self.rec_online = recomendOnline(self.userid, 20)
        print('产生基于功能的推荐')

    def recmguasslike(self,num):#直接返回只含有电影id的list吧
        """ 猜你喜欢的推荐，综合所有--离线和在线推荐和"""
        #首先确定用户评分的次数
        sql=['use dbmovierecommender',
             'SELECT usercount FROM dbmovierecommender.users where userid={}']
        conn, cur = GlobalFun.ConnectSql()
        cur.execute(sql[0])
        cur.execute(sql[1].format(self.userid))
        d=cur.fetchall()
        GlobalFun.Closesql(conn, cur)
        #确定比例
        r=self.getratio(self.sagma,d[0][0],self.r1_offline)

        #在线推荐

        reclist_online=self.recommend_online(math.ceil(1.5*num*r[1]))#直接返回只含有电影id的list

        #离线推荐--als和基于内容的推荐就用稳定时的推荐比例
        reclist_offline=[]
        for l in self.getalsoffline(math.ceil(1.5*num*r[0]*self.r1_als)):#直接返回只含有电影id的list，考虑到要去重所以多要求返回了一些
            reclist_offline.append(l)

        for l in self.getcontoffline(math.ceil(1.5*num*r[0]*(1-self.r1_als))):
            reclist_offline.append(l)#两者相似度量纲并不统一怎么办？？？


        #去重and补足没有看过的热门电影

        reclist=reclist_online
        reclist.extend(reclist_offline)
        #返回结果
        finalresult=self.adjust.removeAndAddHot(reclist, num)
        print("猜你喜欢电影id:"+str(finalresult))
        return finalresult


    def recmProduct(self,productid,num):
        """物品界面相应推荐，综合协同过滤以及基于内容的推荐"""
        # 先假定拿到2*num的物品再从中选择
        num=2*num#和基于在线推荐的向对映，由于架构有些许混乱，所以这里有点不和理
        #首先获得该电影被评价数
        sql=['use dbmovierecommender',
            'select times FROM dbmovierecommender.movie_score_info where movieId={}']
        conn, cur = GlobalFun.ConnectSql()
        cur.execute(sql[0])
        cur.execute(sql[1].format(productid))
        d=cur.fetchall()#获得电影被评分数量
        tu=self.getratio(self.sagma,d[0][0],self.r1_als)
        #直接从数据库中选择推荐列表
        #基于als的要特殊处理
        sql1=[
            'SELECT similarUserId,similarDegree FROM dbmovierecommender.movie_similar_als  where movieid={} order by similarDegree desc limit {}' ,
            'SELECT similarId,similarDegree FROM dbmovierecommender.movie_similar_cont where movieid={} order by similarDegree desc limit {}',
            'SELECT recommendId,predictScore FROM dbmovierecommender.offline_recommend_als where userId={} order by predictScore desc limit {}'

        ]
        cur.execute(sql1[0].format(productid,math.ceil(num*tu[0])))
        alstu=cur.fetchall()
        recmlist = []
        for a in alstu:#这里先假定每个用户再生成一个电影（无比例问题）
            cur.execute(sql1[2].format(a[0],1))
            # print(cur.fetchall())
            recmlist.extend(cur.fetchall())
        #再从中选一半的出来
        finallist=self.adjust.select(recmlist,math.ceil(num*tu[0]/1.5))
        cur.execute(sql1[1].format(productid,math.ceil(num*tu[1])))#基于内容的推荐
        data=cur.fetchall()
        GlobalFun.Closesql(conn, cur)
        recmlist = []
        for d in data:
            recmlist.append(d)
        #再从中选一半的出来
        finallist.extend(self.adjust.select(recmlist,math.ceil(num*tu[1]/1.5)))#加入
        #再去重和再热门补足
        #print(finallist)
        finalresult=self.adjust.removeAndAddHot(finallist,math.ceil(num/2))
        print("物品推荐id："+str(finalresult))
        return finalresult

    def recm_new_movie(self,num):
        """上新页面推荐"""
        recmlist=[]
        return recmlist
    def hot_movie(self,num):
        """热门电影推荐--直接推荐num个还没观看过的电影"""
        hotrec = hotRecommendation()
        recmlist = hotrec.gethotmovie(num)
        return recmlist#返回list

    def getratio(self,sagma,num,r1):
        """确定比例,r1为稳定时第一分量的值"""
        currentr1=r1*num/(num+sagma)
        currentr2=1-currentr1
        return (currentr1,currentr2)

    def getalsoffline(self,num):
        # 先假定拿到2*num的物品再从中选择
        num=num*2
        sql=['SELECT recommendId,predictScore FROM dbmovierecommender.offline_recommend_als where userId={} order by predictScore desc limit {}']
        conn, cur = GlobalFun.ConnectSql()
        cur.execute(sql[0].format(self.userid,num))
        data=cur.fetchall()
        GlobalFun.Closesql(conn, cur)
        reclist=[]
        for d in data:
            reclist.append(d)
        #再选择一半出来

        return self.adjust.select(reclist,math.ceil(num/2))

    def getcontoffline(self,num):
        # 先假定拿到2*num的物品再从中选择
        num = num * 2
        sql = [
            'SELECT recommendId,predictScore FROM dbmovierecommender.offline_recommend_cont where userId={} order by predictScore desc limit {}']
        conn, cur = GlobalFun.ConnectSql()
        cur.execute(sql[0].format(self.userid, num))
        data = cur.fetchall()
        GlobalFun.Closesql(conn, cur)
        reclist = []
        for d in data:
            reclist.append(d)

        # 再选择一半出来

        return self.adjust.select(reclist, math.ceil(num/2))

    """给出在线推荐，主要是根据强度确定每一项目的推荐比例,总共给出num个左右的推荐，调用基于项目的推荐"""

    def recommend_online(self, num):
        # 确定每一偏好的推荐比例问题
        queue=self.rec_online.getonlinequeue()#浅复制
        s = sum(queue.values())
        r = {}
        for k in queue.keys():
            r[k] = queue[k] / s
        # 为每一元素进行推荐anddef加上推荐比例
        reclist = []
        queuelist=queue.keys()
        for qu in queuelist:
            reclist.extend(self.recmProduct(qu, math.ceil(num * r[qu])))
        return reclist

    def quit(self):#退出或更新前需要保存改变的队列入数据库
        print('保存队列')
        self.rec_online.savequeue()

    def newrating(self,moiveid,rate):
        self.rec_online.put(moiveid,rate)#入队

"""测试========"""
# while 1:
# r=recommendBasedOnfunc(2)
# print(r.recmguasslike(20))
# print(r.recmProduct(2,10))
# time.sleep(20)
# r.quit()
# print(str([1,2,3]))
#
