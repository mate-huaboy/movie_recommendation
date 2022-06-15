"""主要功能：一.在适当的时机重新训练als
时机选择：1.避开高峰，评估高峰与低谷，且确定查询粒度。基于历史上的统计信息，统计时段，星期，节假日等自变量及其对应访问量的因变量，推测在某个时段即接下来
时段的访问量，评估当前访问量和接下来一段时间的访问量的走势，要求在当前访问量较低，或者接下来一段时间访问量均较高而找不到合适的几乎重新训练模型的时候而进行模型
训练。
2.尽量使每次运行都效率最高：即1）每次运行之前和运行之后多数用户喜好均有一定的变化，而不至于每次训练而没什么效果。为了不浪费计算资源，要保证每次训练都有他应有
的效果。2）训练数据改变较大，如新增评分数据数量，新增用户数量，新增电影等3）
3.最好综合考虑两者的因素，即能够通过历史记录评估出接下来的用户喜好变化程度和用户流量趋势，以判断在当前是否应该重新训练模型
4.实现要点：
1.评估用户流
2.确定用户喜好变化的变化程度的衡量指标
3.确定训练数据变化程度的衡量指标
4.综合以上因素
5.确定需要评估和训练的的粒度h
6.如何让模型反映重新训练之后的状态的变化呢
5.实现想法：
二.保存推荐结果到mysql以便进一步使用
三，自适应模型，即参数能够实现自动调节--暂不考虑
"""
import os

import GlobalFun
import GlobalVar
from recommendationAlogrithm.alsBasedOnSpark import del_file, MoveRecommend
from recommendationAlogrithm.contentBasedRecommdation import cb


class driver:
    def retrainals(self):
        """重新训练als模型"""
        if os.path.isdir('D://costom_model'):
            del_file('D://costom_model')#删除模型保存的文件夹

            os.rmdir('D://costom_model')
        modelals=MoveRecommend(model_path='D://costom_model', user_path=GlobalVar.pathrating,
                                         move_path=GlobalVar.pathmovie)#重新训练
        sql=['delete from dbmovierecommender.offline_recommend_als',
             'delete from dbmovierecommender.movie_similar_als',
             'SELECT userid FROM dbmovierecommender.ratings group by userid;',
             'SELECT movieid FROM dbmovierecommender.ratings group by movieid']
            # 'SELECT userid FROM dbmovierecommender.users',
            #  'SELECT movieid FROM dbmovierecommender.movies']
        conn, cur = GlobalFun.ConnectSql()
        cur.execute(sql[0])
        cur.execute(sql[1])
        conn.commit()
        cur.execute(sql[2])
        data=cur.fetchall()
        for userid in data:
            modelals.recommend_product_by_userid(userid[0],20)

        #为没部电影都获取推荐列表
        cur.execute(sql[3])
        data = cur.fetchall()
        GlobalFun.Closesql(conn, cur)
        for movieid in data:
            modelals.recommend_user_by_moveid(movieid[0],20)


    def retraincontent(self):
        """重新训练基于内容的推荐算法"""
        c = cb(20, 20)
        c.prepare_item_profile()  # 实际上并不需要完全重新训练，这里懒得改了
        c.user_profile()

        sql = ['delete from dbmovierecommender.offline_recommend_cont',
               'delete from dbmovierecommender.movie_similar_cont',
            #'SELECT userid FROM dbmovierecommender.users',#可能挑出没评分的用户
               'SELECT userid FROM dbmovierecommender.ratings group by userid;',
               'SELECT movieid FROM dbmovierecommender.ratings group by movieid'
               #'SELECT movieid FROM dbmovierecommender.movies'
               ]
        conn, cur = GlobalFun.ConnectSql()

        cur.execute(sql[0])
        cur.execute(sql[1])
        conn.commit()
        cur.execute(sql[2])
        data = cur.fetchall()
        for userid in data:
            # print(type(userid))
            # print(userid)
            # print(userid[0])
            # print(type(userid[0]))
            c.recommendbyuser(userid[0])


        # 为没部电影都获取推荐列表
        cur.execute(sql[3])
        data = cur.fetchall()
        GlobalFun.Closesql(conn, cur)
        for movieid in data:
           c.recommendbymoive(movieid[0])


d=driver()
d.retrainals()
#d.retraincontent()
# sql=['delete from dbmovierecommender.movie_similar_cont',
#      'SELECT movieid FROM dbmovierecommender.ratings group by movieid']
# conn, cur = GlobalFun.ConnectSql()
# cur.execute(sql[0])
#
# conn.commit()
# cur.execute(sql[1])
# sql='SELECT movieid FROM dbmovierecommender.ratings where movieid>190183 group by movieid'
#
# cur.execute(sql)
# data = cur.fetchall()
# c = cb(20, 20)
# c.prepare_item_profile()  # 实际上并不需要完全重新训练，这里懒得改了
# c.user_profile()
# for userid in data:
#     print(userid[0])
#     c.recommendbymoive(userid[0])



