import tkinter as tk
import threading
import GUI.metaFrame
import GUI.browseFootprints
from GUI import GUIGlobalVar
from recomemdBasedOnwindows.recommendBasedOnfunc import recommendBasedOnfunc
from recommendationAlogrithm.hotRecommendation import hotRecommendation

global Images
import GUI.metaButtons
Images=[]


class Main_window():

    def __init__(self,root,window,movieid,userid):
        self.movieid = movieid
        self.userid = userid
        self.window = window
        self.root = root
        """热门电影推荐器产生"""
        self.hotrec=hotRecommendation()

        navbar_Frame = tk.Frame(self.window, width=800, height=20)#导航栏
        navbar_Frame.pack_propagate(False)
        navbar_Frame.place(x=0,y=0,anchor="nw")
        GUI.metaButtons.NavigationBar(self.root,self.window,navbar_Frame,self.movieid,self.userid,type="M")

        if userid is None:
            tk.Label(self.window,text="RecSystem Failed :(\nPlease login or register first",font=('',20)).place(x=230,y=130,anchor='nw')
            tk.Label(self.window, text='HotMovies').place(x=45, y=250, anchor='nw')
            self.hotmovieFrame = tk.Frame(self.window)
            self.hotmovieFrame.place(x=15, y=270, anchor='nw')  # 放置热门电影
            self.hotmovie()
        else:
            """基于功能的推荐的推荐器产生"""
            if GUIGlobalVar.r is not None:
                GUIGlobalVar.r.quit()#先暂停在线推荐再产生
            GUIGlobalVar.r=recommendBasedOnfunc(self.userid)
            #self.r = recommendBasedOnfunc(self.userid)
            #放置热门电影
            tk.Label(self.window, text='热门电影').place(x=45, y=20, anchor='nw')
            self.hotmovieFrame = tk.Frame(self.window)
            self.hotmovieFrame.place(x=15, y=40, anchor='nw')
            self.hotmovie()

            #放置基于SVD的离线推荐
            tk.Label(self.window, text='猜你喜欢').place(x=45, y=242, anchor='nw')
            self.offline_rec_svdFrame = tk.Frame(self.window,width=800,height=150)
            self.offline_rec_svdFrame.pack_propagate(False)
            self.offline_rec_svdFrame.place(x=15,y=262,anchor='nw')


            #放置基于ALS的离线推荐
            # tk.Label(self.window, text='Offline RecSys Based on ALS').place(x=45, y=441, anchor='nw')
            self.offline_rec_alsFrame = tk.Frame(self.window)
            self.offline_rec_alsFrame.place(x=15, y=461, anchor='nw')

            #放置在线推荐
            # tk.Label(self.window,text="Online RecSys").place(x=45,y=20,anchor='nw')
            self.online_rec_Frame = tk.Frame(self.window)
            self.online_rec_Frame.place(x=15,y=663,anchor='nw')
            self.offline_rec_svd()

    def hotmovie(self):
        # conn,cur = GlobalFun.ConnectSql()
        # cur.execute('select movieid,count(1) from movierecommender.ratings group by movieid order by count(1) desc limit 5;')
        # data = cur.fetchall()#拿到最热门的5部电影
        # GlobalFun.Closesql(conn,cur)

        data=self.hotrec.gethotmovie(5)
        for tup in data:
            t = threading.Thread(target=self.job,args=(self.hotmovieFrame,tup))
            t.start()

        """猜你喜欢"""
    def offline_rec_svd(self):
        # conn, cur = GlobalFun.ConnectSql()
        # cur.execute(
        #     'select recommendid from movierecommender.offline_recommend_svd where userid={} order by predictScore desc limit 5;'.format(self.userid))
        # data = cur.fetchall()  # 拿到离线用户推荐信息
        # GlobalFun.Closesql(conn, cur)
        # print(data)
        # print(len(data))
        #
        # if len(data) == 0:
        #     tk.Label(self.offline_rec_svdFrame,text="Sorry T^T\nI haven't know you a long time\nGive me some time to recommend for you!",font=('',20)).pack(side='bottom')
        # else:
        data=GUIGlobalVar.r.recmguasslike(15)#推荐出15个
        k=0
        for tup in data:
            k=k+1
            if(k<=5):
                t = threading.Thread(target=self.job, args=(self.offline_rec_svdFrame, tup))
                t.start()
            elif k<=10:
                t = threading.Thread(target=self.job, args=(self.offline_rec_alsFrame, tup))
                t.start()
            else:
                t = threading.Thread(target=self.job, args=(self.online_rec_Frame, tup))
                t.start()


    # def offline_rec_als(self):
    #     conn, cur = GlobalFun.ConnectSql()
    #     cur.execute(
    #         'select recommendid from movierecommender.offline_recommend_als where userid={} order by predictScore desc limit 5;'.format(self.userid))
    #     data = cur.fetchall()  # 拿到离线用户推荐信息
    #     GlobalFun.Closesql(conn, cur)
    #     print(data)
    #     print(len(data))
    #     if len(data) > 0:
    #         for tup in data:
    #             t = threading.Thread(target=self.job, args=(self.offline_rec_alsFrame, tup[0]))
    #             t.start()
    #
    # def online_rec(self):
    #     conn, cur = GlobalFun.ConnectSql()
    #     cur.execute(
    #         'select movieid from movierecommender.online_recommend where userid = {} limit 5;'.format(
    #             self.userid))
    #     data = cur.fetchall()  # 拿到离线用户推荐信息
    #     GlobalFun.Closesql(conn, cur)
    #     print(data)
    #     print(len(data))
    #     for tup in data:
    #         t = threading.Thread(target=self.job, args=(self.online_rec_Frame, tup[0]))
    #         t.start()

    def job(self, Frame, movieid):
        temp = GUI.metaFrame.metaFrame(movieid, self.userid, Frame, self.window, self.root)
        Images.append(temp.tk_image)
        temp.frm.pack(side='left')


