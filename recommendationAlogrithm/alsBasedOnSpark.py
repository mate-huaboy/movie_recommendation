"""目标：根据als，保存每个用户的推荐（个数要求和相似度阈值要求）
保存每个电影相似的电影 （个数要求和阈值要求）
"""
import csv

import pandas as pd
from numpy import long
from pyspark import SparkContext as sc
from pyspark import SparkConf
from pyspark.mllib.recommendation import ALS,MatrixFactorizationModel
import os, datetime
import numpy as np
from pyspark.ml.evaluation import RegressionEvaluator
# from pyspark.ml.recommendation import ALS #调参时用
from pyspark.sql import Row

#在程序中添加一以下代码

import sys

from pyspark.shell import spark

import GlobalFun
import GlobalVar

path=['', 'D:\\Python3.8_install\\python38.zip', 'D:\\Python3.8_install\\DLLs', 'D:\\Python3.8_install\\lib', 'D:\\Python3.8_install', 'D:\\Python3.8_install\\lib\\site-packages', 'D:\\Python3.8_install\\lib\\site-packages\\pip-21.0.1-py3.8.egg']
for p in path:
    sys.path.append(p)
import findspark
findspark.init()
# 删除文件夹下面的所有文件(删除文件,删除文件夹)
import os
def del_file(path_data):
    for i in os.listdir(path_data):  # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        file_data = path_data + "/" + i  # 当前文件夹的下面的所有东西的绝对路径
        if os.path.isfile(file_data) == True:  # os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            os.remove(file_data)
        else:
            del_file(file_data)
            os.rmdir(file_data)



class MoveRecommend(object):
    def __init__(self, model_path, user_path, move_path, app_name="move_recommend", master="local[*]"):
        self.app_name = app_name
        self.master = master
        self.sc = self.create_spark_context()
        self.train_rank = 5  # 稀疏矩阵分解的秩
        self.train_iter = 13  # 迭代次数
        self.train_lambda = 0.16  # 正则化参数(惩罚因子)
        self.user_path = user_path
        self.move_path = move_path
        self.model_path = model_path
        self.model = self.get_model()

    @staticmethod
    def get_time():
        d = datetime.datetime.now()
        return d.strftime('%M:%S')

    def create_spark_context(self):
        conf = SparkConf().setAppName(self.app_name).setMaster(self.master)
        spark_context = sc.getOrCreate(conf)
        return spark_context

    def get_model(self):
        """如果给定的目录没有model，则重新训练model，如果已有model，则直接加载使用"""
        if not os.path.isdir(self.model_path):
            print(f'model not found,start traing at {self.get_time()}')
            return self.train_and_save()
        return MatrixFactorizationModel.load(self.sc, self.model_path)
        # return self.train_and_save()

    def train_and_save(self):
        """只用训练集，训练model并持久化到本地目录"""
        user_rdd = self.sc.textFile("file:///" + self.user_path)
        raw_rating_rdd = user_rdd.map(lambda line: line.split(',')[:3])  # 每行分割后为一个包含4个元素的列表，取前3项即可
        first = raw_rating_rdd.first()
        raw_rating_rdd = raw_rating_rdd.filter(lambda x: x != first)
        rating_rdd = raw_rating_rdd.map(lambda x: (x[0], x[1], x[2]))  # x[0],x[1],x[2]对应用户id，电影id，评分
        model = ALS.train(rating_rdd, self.train_rank, self.train_iter, self.train_lambda)
        model.save(self.sc, self.model_path)
        print(f'model training done at {self.get_time()}')
        return model


    # def get_move_dict(self):
    #     """返回一个字典列表，每个字典存放3个电影详情字段"""
    #     move_info_rdd = self.sc.textFile("file:///" + self.move_path)
    #     move_splited_rdd = move_info_rdd.map(lambda line: line.split("|"))
    #     # 提取3个字段，将转为map类型，name:电影名，url：电影ur
    #     func = lambda a_list: (int(a_list[0]), 'name:%s,url:%s' % (a_list[1], a_list[4]))
    #     move_map_info_rdd = move_splited_rdd.map(func).collectAsMap()  # move_map_info_rdd 已经是字典类
    #     return move_map_info_rdd

    def recommend_product_by_userid(self, user_id, num=5):  # 是基于什么的推荐
        """根据给定用户id，向其推荐top N部电影"""
        result = self.model.recommendProducts(user_id, num)
        #move_dict = self.get_move_dict()
        conn, cur = GlobalFun.ConnectSql()
        for r in result:
            r=(r.user,r.product,r.rating)
            cur.execute("insert into DBMovieRecommender.offline_recommend_als(userId,recommendId,predictScore) values {}".format(r))
        conn.commit()
        GlobalFun.Closesql(conn,cur)
        # return [(r.user, r.product, r.rating) for r in result]

    def recommend_user_by_moveid(self, move_id, num=5):  # 是基于什么的推荐,直接保存吧--推出电影之间的相似度
        """根据给定电影ID，推荐对该电影感兴趣的top N 个用户"""
        result = self.model.recommendUsers(move_id, num)
        conn, cur = GlobalFun.ConnectSql()
        for r in result:
            r=(r.product, r.user, r.rating)
            cur.execute(
                "insert into DBMovieRecommender.movie_similar_als(movieId,similarUserId,similarDegree) values {}".format(
                    r))
        conn.commit()
        GlobalFun.Closesql(conn, cur)
        #return [(r.user, r.product,  r.rating) for r in result]


    def recommend_product_by_movieid(self,movieid,num=5):#暂用内存太大，跑不起来？为啥这么慢---改变思路，先不用
        moviefeature=self.getproductFeature(movieid)
        print(type(moviefeature))
        movie_result={}
        items = pd.read_csv(GlobalVar.pathmovie)["movieId"].values
        items = set(items) - set([movieid])
        for item in items:
            movie_result[item] = self.Cossim(np.array(self.getproductFeature(item)), np.array(moviefeature))  # 获取用户对Item的喜好程度集合
        if num is None:  # 如果前K个不是空
            result = sorted(  # 排序
                movie_result.items(), key=lambda k: k[1], reverse=True
            )
        else:
            result = sorted(
                movie_result.items(), key=lambda k: k[1], reverse=True
            )[:num]
            # 再保存起来
            conn, cur = GlobalFun.ConnectSql()
        for r in result:
            r = (movieid, r[0], r[1])
            cur.execute(
                "insert into DBMovieRecommender.movie_similar_als(movieId,similarId,similarDegree) values {}".format(
                    r))
        conn.commit()
        GlobalFun.Closesql(conn, cur)
        print(result)

    def Cossim(self,feature1,freature2):
        a=sum(feature1*freature2)
        b=np.linalg.norm(feature1)
        c=np.linalg.norm(freature2)
        return a/(b*c)

    def getproductFeature(self,productid):
        """获取电影画像"""
        profs=self.model.productFeatures()
        # prof=profs.filter(lambda x:x[0]==productid)
        prof=profs.lookup(productid)
        # print(p)
        # print(prof.count())
        # print(prof.take(1))
        return prof


    def getuserFeature(self,userid):
        """获取用户画像"""
        usfs=self.model.userFeatures()
        return usfs.lookup(userid)

    def getmodelpath(self):
        """获取模型保存的路劲"""
        return self.model_path

    """ 参数调节"""
    def adjust(self):
        """只用训练集，训练model并持久化到本地目录"""
        ranke=[5]
        lam=[0.1,0.12,0.14,0.16,0.18,0.2,0.22]
        user_rdd = self.sc.textFile("file:///" + self.user_path)
        raw_rating_rdd = user_rdd.map(lambda line: line.split(',')[:3])  # 每行分割后为一个包含4个元素的列表，取前3项即可
        first = raw_rating_rdd.first()
        raw_rating_rdd = raw_rating_rdd.filter(lambda x: x != first)
        rating_rdd = raw_rating_rdd.map(lambda p: Row(userId=int(p[0]), movieId=int(p[1]),
                                     rating=float(p[2])))  # x[0],x[1],x[2]对应用户id，电影id，评分
        df=spark.createDataFrame(rating_rdd)
        (train,vl,test)=df.randomSplit([0.6,0.2,0.2])
        rl=[]
        # rl_train=[]
        rl_test=[]
        for r in ranke:
            for l in lam:

                als = ALS(maxIter=18, regParam=l, userCol="userId", itemCol="movieId", ratingCol="rating",
                          coldStartStrategy="drop",rank=r)
                model=als.fit(train)
                """train最后的误差"""
                # predictions = model.transform(train)
                # evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                #                                 predictionCol="prediction")
                # rmse = evaluator.evaluate(predictions)
                # rl_train.append((r, l, rmse))
                # print("训练集-Root-mean-square error = " + str((r, l, rmse)))

                """验证集"""
                predictions = model.transform(vl)
                evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                                predictionCol="prediction")
                rmse = evaluator.evaluate(predictions)
                rl.append((r,l,rmse))
                print("验证集-Root-mean-square error = " + str((r,l,rmse)))


                """"测试集"""
                predictions = model.transform(test)
                evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                                predictionCol="prediction")
                rmse = evaluator.evaluate(predictions)
                rl_test.append((r, l, rmse))
                print("测试集-Root-mean-square error = " + str((r, l, rmse)))

        # f = open('D://.seniorstudy/graduation_project/pra_train.csv', 'wb')
        # csv_writer = csv.writer(f)
        #
        # #  构建列表头
        # csv_writer.writerow(["rank", "lamba", "rmse"])
        # for rlrow in rl_train:
        #     csv_writer.writerow(rlrow)
        # f.close()

        f=open('D://.seniorstudy/graduation_project/pra_Validation3.csv','w',encoding='utf-8',newline="")
        csv_writer = csv.writer(f)

        #  构建列表头
        csv_writer.writerow(["rank", "lamba", "rmse"])
        for rlrow in rl:
            csv_writer.writerow(rlrow)
        f.close()

        f = open('D://.seniorstudy/graduation_project/pra_test.csv', 'w',encoding='utf-8',newline="")
        csv_writer = csv.writer(f)

        #  构建列表头
        csv_writer.writerow(["rank", "lamba", "rmse"])
        for rlrow in rl_test:
            csv_writer.writerow(rlrow)
        f.close()

    """获取电影相似度矩阵"""

    """获取用户相似度矩阵"""


# m = MoveRecommend(model_path='D://costom_model', user_path='D://1毕设代码jupyter/cf/ml-latest-small/ratings.csv',
#                   move_path='D://1毕设代码jupyter/cf/ml-latest-small/movies.csv')
# #m.recommend_product_by_movieid(1,5)
# m.recommend_product_by_userid(1,5)
# m.recommend_user_by_moveid(1,5)

"""调参"""
# m = MoveRecommend(model_path='D://costom_model', user_path='D://1毕设代码jupyter/cf/ml-latest-small/ratings.csv',
#                   move_path='D://1毕设代码jupyter/cf/ml-latest-small/movies.csv')
# m.adjust()




