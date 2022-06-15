"""
在线推荐算法---要求：1.简单快速，能够在较短时间内给出推荐内容
2.能够反映用户当前的偏好，能够对用户当前偏好的改变给出较为灵敏的反映，这要求及时捕捉到用户的反馈，根据反馈给出相应推荐
实现算法：1)设置用户当前的喜好队列，队列元素反映用户的某个偏好，以及偏好强度，和时间
按照以下规则进行出队入队：入队：比对当前要入队元素（喜好偏向）与队内各个喜好偏向进行相似度计算，如果相似度高到一定程度，便与其进行合并，即修正该队内元素
否则就应该入队，入队时有两种情况，一种是队未满，此时直接入队即可，另一种是对满，则应遵循一定的规则进行替换，替换规则可以直接根据偏好强度选择
出队:每隔一段时间就对当前喜好强度减1，如果强度简为0，则出队。
3.能够根据队列给出推荐列表。
推荐算法实现：针对队列中（注意队列为0的情况）的每一个用户偏好给出推荐列表。难点：根据用户喜好怎么能快速搜索出最相似的电影而给出推荐列表。
实现方法：一：快速给出推荐列表的难点是由于可行解空间很大（所有电影均可以），需要全盘遍历，根据当前偏好向量和电影特征向量之间的相似度，找出n个最相似的电影，
这个过程由于选择的离散性（必须选择出与电影对应的画像）和电影的画像分量的连续性，感觉很难利用智能搜索的方法进行搜索，所以提出一下方法：
结合聚类压缩搜索空间，通过多次聚类压缩要搜索的数量，最后以一种类似多路搜索树的方式进行搜索。
二：近似算法：改造2使喜好与电影画像一一对应，即不产生新的画像数据，再根据之前得到的电影相似数据，推荐给用户即可，即对于基于内容的推荐，可实现i2i的算法，
基于协同过滤的算法，可实现i2u2i的推荐。
"""
#需要用到用户的状态？不需要，前面直接给出相应队列的大小
import math
import time
from threading import Thread

import GlobalFun


class recomendOnline:
    def __init__(self,userid,alsqueuemaxnum=20):
        #初入系统时初始化队列--根据userid
        self.alsqueuemaxnum = alsqueuemaxnum  # 队列最大数目
        self.userid = userid
        self.queue = self.loadqueue()  # 队列
        # self.contqueuemaxnum = contqueuemaxnum  # 基于内容的推荐的最大数目
        self.alsqueuenum=len(self.queue);#队列本身的数目，应从数据库中获取
        # self.contqueuenum=0;#队列本身的数目，应从数据库中获取
        self.w_in=2
        self.w_out=1
        self.q=1#单位强度
        self.th=0#出队强度门限
        self.time =20
        # 开启出队线程
        t = Thread(target=self.pop, daemon=True)
        t.start()



    def put(self,movieID,rating):
        """入队--将看过的电影和强度控制入队即可"""
        if movieID in self.queue.keys():
            self.queue[movieID]=self.w_in*self.q*rating+self.queue[movieID]
        else:
            if self.alsqueuenum==self.alsqueuemaxnum:
                self.exchange()
            else:
                self.alsqueuenum=self.alsqueuenum+1
            self.queue[movieID] = self.w_in * self.q * rating

    def pop(self):
        """出队,开启出队线程"""
        while 1:
            time.sleep(self.time)#睡眠
            #不对队列加锁可以吗
            for qu in list(self.queue.keys()):
                self.queue[qu]=self.queue[qu]- self.w_out*self.q
                if self.queue[qu]<=0:
                    self.queue.pop(qu)#出队
                    self.alsqueuenum=self.alsqueuenum-1
                    if self.alsqueuenum==0:
                        return


    # def recommendals(self,num):
    #     """基于als的在线推荐"""
    #
    # def recomendcont(self,num):
    #     """基于内容的在线推荐"""

    def exchange(self):
        """利用合适的规则替换出，队列数此时并不改变"""
        min_queue_key = min(self.queue, key=lambda k: self.queue[k])
        self.queue.pop(min_queue_key)

    def savequeue(self):
        """退出时将当前队列保存到数据库中"""
        #首先删除对应用户的最近队列记录
        conn, cur = GlobalFun.ConnectSql()
        sql='DELETE FROM DBMovieRecommender.online_recommend where userid={}'
        sql=sql.format(self.userid)
        cur.execute(sql)
        insertsql="insert into DBMovieRecommender.online_recommend(userId,movieId,intention) values {}"
        for qu in self.queue.keys():
            data=(self.userid,qu,self.queue[qu])
            cur.execute(insertsql.format(data))
        conn.commit()

        GlobalFun.Closesql(conn, cur)

        

    def loadqueue(self):
        """从数据库中导出队列"""
        conn, cur = GlobalFun.ConnectSql()
        sql="select movieId,intention from dbmovierecommender.online_recommend where userid={} "
        cur.execute(sql.format(self.userid))
        data=cur.fetchall()
        GlobalFun.Closesql(conn, cur)
        dic={}
        for d in data:
            dic[d[0]]=d[1]
        return dic
    def getonlinequeue(self):
        return self.queue



"""测试====="""
# r=recomendOnline(1)
# l=r.getonlinequeue()
# print(l)
# r.put(1,3)
# r.put(10,5)
# time.sleep(20)
# r.savequeue()