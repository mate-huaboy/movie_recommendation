# # import GlobalFun
# # r=(1,2,3)
# # conn, cur = GlobalFun.ConnectSql()
# # cur.execute("insert into DBMovieRecommender.offline_recommend_als(userId,recommendId,predictScore) values {}".format(r))
# # conn.commit()
# # GlobalFun.Closesql(conn, cur)
#
# # import numpy as np
# # l1=np.array([1,2,3])
# # print(l1)
# # type(l1)
# #
# # l2=np.array([0,0,3])
# # a=sum(l1*l2)
# # print(a)
# # b=np.linalg.norm(l1)
# # c=np.linalg.norm(l2)
# # print(c)
# # print(a/(b*c))
# import csv
#
# l=[(5, 0.001, 0.5490759292916984),
#    (5, 0.001, 1.4182029295671907),
#    (5, 0.01, 0.5478603801546243),
#    (5, 0.01, 1.1467004584066378),
#    (5, 0.03, 0.554636508827187),
#    (5, 0.03, 1.0208692145996008),
#    (5, 0.06, 0.5714946541137645),
#    (5, 0.06, 0.9550842819740641),
#    (5, 0.1, 0.6016271278744448),
#    (5, 0.1, 0.9178122153351979),
#    (5, 0.3, 0.7896526946845376),
#    (5, 0.3, 0.924728559954077),
#  (10, 0.001, 0.40131452681039315),
# (10, 0.001, 1.4988245867689138),
# (10, 0.01, 0.40000143720889414),
#  (10, 0.01, 1.2427169787678984),
# (10, 0.03, 0.41821583778417076),
# (10, 0.03, 1.0782287454110653),
#  (10, 0.06, 0.45642939365058427),
#  (10, 0.06, 0.9719471589205226),
#  (10, 0.1, 0.5157984791210819),
# (10, 0.1, 0.9197993885454632),
#  (10, 0.3, 0.7873512544327124),
# (10, 0.3, 0.9244941254756188),
#  (15, 0.001, 0.2959257367709646),
#  (15, 0.001, 1.6255227675808066),
#  (15, 0.01, 0.2980746192935047),
#  (15, 0.01, 1.3125388962862479),
#  (15, 0.03, 0.3285016531821458),
# (15, 0.03, 1.09448480445857),
#  (15, 0.06, 0.38651478081438284),
#  (15, 0.06, 0.9685522557168409),
#  (15, 0.1, 0.46956516231763),
#  (15, 0.1, 0.9125100909592265),
#  (15, 0.3, 0.7873643018866795),
#  (15, 0.3, 0.9245077283852186),
# (20, 0.001, 0.222247001419033),
#  (20, 0.001, 1.661673217435731),
#  (20, 0.01, 0.22832588885069596),
#  (20, 0.01, 1.341559531172941),
#  (20, 0.03, 0.26966645279019674),
#  (20, 0.03, 1.0956150846261778),
#  (20, 0.06, 0.34606261833337965),
#  (20, 0.06, 0.9645325942078332),
#  (20, 0.1, 0.44482771945223654),
# (20, 0.1, 0.9127287733069205),
#  (20, 0.3, 0.7866477304847753)
# ]
# l_v=[]
# l_train=[]
# k=0
# for lone in l:
#     if k%2==0:
#         l_train.append(lone)
#     else:
#         l_v.append(lone)
#     k=k+1
#
# f = open('D://.seniorstudy/graduation_project/pra_train.csv', 'w',encoding='utf-8',newline="")
# csv_writer = csv.writer(f)
#
# #  构建列表头
# csv_writer.writerow(["rank", "lamba", "rmse"])
# for rlrow in l_train:
#     csv_writer.writerow(rlrow)
# f.close()
#
# f=open('D://.seniorstudy/graduation_project/pra_Validation.csv', 'w',encoding='utf-8',newline="")
# csv_writer = csv.writer(f)
#
# #  构建列表头
#
# for rlrow in l_v:
#     csv_writer.writerow(rlrow)
# f.close()


# import socks
# import socket
# from urllib import request
# from urllib.error import URLError
#
# socks.set_default_proxy(socks.SOCKS5, 'localhost', 9150)
# socket.socket = socks.socksocket
# try:
#     response = request.urlopen('https://www.cnblogs.com/junrong624/p/5533655.html')
#     print(response.read().decode('utf-8'))
# except URLError as e:
#     print(e.reason)

# import pandas as pd
# df=pd.read_csv("./data/info.csv")
# print(df[df['id']==1]['intro'].values[0])
from PIL import Image

data_stream = './data/poster/' + str(1) + '.jpg'
pil_image = Image.open(data_stream)  # 转成pil格式的图片
w, h = pil_image.size
pil_image.show()