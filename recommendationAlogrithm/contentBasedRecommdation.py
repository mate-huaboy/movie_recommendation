"""根据基于内容的推荐系统，保存阈值要求的电影相似度数据和用户推荐按数据"""
import math
import pandas as pd
import numpy as np

import GlobalFun

rates='D:/1毕设代码jupyter/cf/ml-latest-small/ratings.csv'
movies='D:/1毕设代码jupyter/cf/ml-latest-small/movies.csv'

class cb:
    item_matrix = {}#电影画像字典
    genres_all = []#类型矩阵
    user_matrix = {}#用户画像字典
   # item_sim = []#物品相似度矩阵
    user_sim = []#用户_物品相似度矩阵
    item_dict={}#电影类型字典
    user_rating_dict={}#用户评分字典
    def __init__(self,userK,itemK):
        self.userK=userK
        self.itemK=itemK#需要选出的根据电影推荐电影的数量

    # 为item画像
    def prepare_item_profile(self):
        #获得每个电影的类型字典
        items=pd.read_csv(movies)
        items_ids=set(items["movieId"].values)
        genres_all=list()
        for item in items_ids:
            genres = items[items["movieId"] == item]["genres"].values[0].split("|")
            self.item_dict.setdefault(item,[]).extend(genres)
            genres_all.extend(genres)
            # 获得所有的电影的类型
        self.genres_all=set(genres_all)
        length=len(self.genres_all)
        #获得one-hot编码
        for item in self.item_dict.keys():
            self.item_matrix[item]=[0]*length
            for genre in self.item_dict[item]:
                index=list(set(self.genres_all)).index(genre)
                self.item_matrix[item][index]=1#one -hot编码，由此得到item画像
                #再保存起来

    # 为用户画像
    def user_profile(self):
        users=pd.read_csv(rates)
        users_id=set(users["userId"].values)
        for user in users_id:
            self.user_rating_dict.setdefault(user,{})
        # with open(rates,"r") as fr:
        #     for line in fr.readline():
        for line in range(len(users)):

            # if not line.startswith("userId"):
            user=users["userId"][line]
            item=users["movieId"][line]
            rate=users["rating"][line]
                # (user,item,rate)=line.split(",")[3]
            self.user_rating_dict[user][item]=int(rate)
        for user in self.user_rating_dict.keys():
            score_list=self.user_rating_dict[user].values()
            avg=sum(score_list)/len(score_list)
            self.user_matrix[user]=[]
            for genre in self.genres_all:  # 依次遍历每一个类型
                score_all = 0.0
                score_len = 0
                # 遍历每个item
                for item in self.user_rating_dict[user].keys():  # 遍历 用户1的电影Id列表
                    # 判断类型是否在用户评分过的电影里
                    if genre in self.item_dict[int(item)]:  # 并判断这个电影类型 是否在这个item的描述类型中
                        score_all += (self.user_rating_dict[user][item] - avg)  # 计算用户1对某一电影类型偏好程度公式
                        # 把所有用户看过这个类型的电影 依次评分与平均分相减  和除以评分该类型电影总数
                        score_len += 1
                if score_len == 0:  # 用户无评分该类型电影
                    self.user_matrix[user].append(0.0)
                else:
                    self.user_matrix[user].append(score_all / score_len)  # 把所有用户看过这个类型的电影 依次评分与平均分相减  和除以评分该类型电影总数
                #再保存起来
       # print(self.user_matrix[49])



    # 获得全部相似度矩阵
    #获得所有用户-物品相似度矩阵
    def get_all_usersim(self):
        for user in self.user_matrix.keys():
            for item in self.item_matrix.keys():
               sim=self.cosUI(user,item)
               self.user_sim.append([user,item,sim])
                #再保存起来

    #获得所有物品相似度矩阵
    # def get_all_itemsim(self):
    #

        # 获取用户未进行评分的item列表,后面可能用不到这个函数
    def get_none_score_item(self, user):
            items = pd.read_csv(movies)["movieId"].values
            data = pd.read_csv(rates)
            have_score_items = data[data["userId"] == user]["movieId"].values
            none_score_items = set(items) - set(have_score_items)
            return none_score_items




        # 为特定用户推荐
        # 为用户进行电影推荐
    def recommendbyuser(self, user):
        Ua = math.sqrt(sum([math.pow(one, 2) for one in self.user_matrix[user]]))
        if Ua==0:
            return
        user_result = {}
        item_list = self.get_none_score_item(user)
        for item in item_list:
            user_result[item] = self.cosUI(user, item)  # 获取用户对Item的喜好程度集合
        if self.userK is None:  # 如果前K个不是空
            result = sorted(  # 排序
                user_result.items(), key=lambda k: k[1], reverse=True
            )
        else:
            result = sorted(
                user_result.items(), key=lambda k: k[1], reverse=True
            )[:self.userK]
                #再保存起来
            conn, cur = GlobalFun.ConnectSql()
        for r in result:
            r=(user,r[0],r[1])#有可能为空
            cur.execute("insert into DBMovieRecommender.offline_recommend_cont(userId,recommendId,predictScore) values {}".format(r))
        conn.commit()
        GlobalFun.Closesql(conn,cur)



        #为电影找相似电影
    def recommendbymoive(self,movie):
        Ia = math.sqrt(sum([math.pow(one, 2) for one in self.item_matrix[movie]]))
        if Ia==0:
            return
        movie_result = {}
        items = pd.read_csv(movies)["movieId"].values
        items=set(items)-set([movie])
        movie_feature=self.item_matrix[movie]
        for item in items:
            movie_result[item] = GlobalFun.cosUI(self.item_matrix[item], movie_feature)  # 获取用户对Item的喜好程度集合
        if self.itemK is None:  # 如果前K个不是空
            result = sorted(  # 排序
                movie_result.items(), key=lambda k: k[1], reverse=True
            )
        else:
            result = sorted(
                movie_result.items(), key=lambda k: k[1], reverse=True
            )[:self.itemK]
            # 再保存起来
            conn, cur = GlobalFun.ConnectSql()
        for r in result:
            r = (movie, r[0], r[1])
            cur.execute(
                "insert into DBMovieRecommender.movie_similar_cont(movieId,similarId,similarDegree) values {}".format(
                    r))
        conn.commit()
        GlobalFun.Closesql(conn, cur)


    def cosUI(self,user, item):
        # 通过余弦相似度
        # Uia 分子 Ua（用户对电影的偏好矩阵） Ia（电影类型的特征信息矩阵）电影shi否属于类型a
        Uia = sum(
            np.array(self.user_matrix[user])
            *
            np.array(self.item_matrix[item])
        )
        Ua = math.sqrt(sum([math.pow(one, 2) for one in self.user_matrix[user]]))  # 分母 Ua
        Ia = math.sqrt(sum([math.pow(one, 2) for one in self.item_matrix[item]]))  # 分母 Ia
        return Uia / (Ua * Ia)#有可能返回为nan




    #根据特定物品推荐

    #根据特点标签推荐

def retrain():
    """训练基于内容的推荐算法，使其推荐的list保存到数据库，以便后期直接使用
    必须保存到数据库的内容有：根据用户推荐的电影，根据电影推荐相应电影，以便后期直接从数据库中取出即可
    """
    c=cb(10,10)
    c.prepare_item_profile()#实际上并不需要完全重新训练，这里懒得改了
    c.user_profile()
    users = pd.read_csv(rates)
    users_id = set(users["userId"].values)
    for user in users_id:
        c.recommendbyuser(user)
    items = pd.read_csv(movies)["movieId"].values
    for item in items:
        c.recommendbymoive(item)


#测试
# cbrec=cb(10)
# cbrec.prepare_item_profile()
# cbrec.user_profile()
# cbrec.recommend(1)


# c=cb(10,10)
# c.prepare_item_profile()#实际上并不需要完全重新训练，这里懒得改了
# c.user_profile()
# c.recommendbymoive(1)

# c=cb(10,10)
# c.prepare_item_profile()#实际上并不需要完全重新训练，这里懒得改了
# c.user_profile()
# c.recommendbyuser(49)


