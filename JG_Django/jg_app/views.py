# from cgi import test
# import collections
# from gc import collect
# from hashlib import new
# from ipaddress import collapse_addresses
# from multiprocessing import context
# from operator import truediv
# from os import remove
# from unicodedata import name
from email import contentmanager
from multiprocessing import context
from symbol import lambdef_nocond
from turtle import distance
from django.shortcuts import render, redirect
from pymongo import MongoClient
import datetime
import random
from datetime import datetime
import jieba
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as logins
from django.contrib.auth import logout as logouts
from django.contrib.auth import authenticate
from jg_app.forms import RegisterUserForm
from django.contrib import messages
from django.http import HttpResponse
import numpy as np
import pandas as pd
import googlemaps
import requests
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.decomposition import PCA

# Make MongoDB connection with Pymongo
cluster = MongoClient("mongodb+srv://Tang:108306058@journeygo.yhfdrry.mongodb.net/?retryWrites=true&w=majority")
db = cluster['JourneyGo_DB']

collection = db['Taipei_gov']
detail = collection.find({})
df = pd.DataFrame(list(detail))
data = df[['name','intro','categories']]

X = np.array(data.intro)

# 用bert作詞向量 模型二
text_data = X
model = SentenceTransformer('all-mpnet-base-v2')
embeddings = model.encode(text_data, show_progress_bar=True)
embed_data = embeddings

X = np.array(embed_data)

# 計算餘弦向量
cos_sim_data = pd.DataFrame(cosine_similarity(X))

#register
def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, "Thanks for registering. You are now logged in.")
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            logins(request, new_user)
            if request.user.is_authenticated:
                # 新增MongoDB User_account
                user = request.user
                collection = db['User_account']
                if collection.count() == 0:
                    post = {"_id": 0, "firstName": user.first_name, "lastName": user.last_name, "email": user.email, "password": user.password,
                        "hashtag": "new", "pic": "https://en.pimg.jp/062/473/818/1/62473818.jpg", "friendList": [], "intro": ""}
                    collection.insert_one(post)
                else:
                    post = {"_id": int(collection.count()), "firstName": user.first_name, "lastName": user.last_name, "email": user.email, "password": user.password,
                        "hashtag": "new", "pic": "https://en.pimg.jp/062/473/818/1/62473818.jpg", "friendList": [], "intro": ""}
                    #print(collection.count(), user.first_name, user.last_name, user.email, user.password)
                    collection.insert_one(post)
            return redirect('balancegame')
    else:
        form = RegisterUserForm()
    return render(request, 'register.html', {'form': form})

# login
def login1(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            logins(request, user) 
            return redirect('index')  
    else:
        form = AuthenticationForm()
    return render(request, 'login1.html', {'form': form})

def logout(request):
    if request.method == 'POST':
        logouts(request)
        return redirect('index')

def login(request):
    input_name = None
    input_email = None
    input_pwd = None
    if request.method == 'POST':
        input_name = request.POST["user-name"]
        input_email = request.POST["user-email"]
        input_pwd = request.POST["user-pwd"]
    
    db = cluster['test']
    collection = db['signup']
    user = collection.find_one({"user_first_name": input_name})

    context = {
        'user': user,
        'input_name': input_name,
        'input_email': input_email,
        'input_pwd': input_pwd,
    }

    return render(request, 'login.html', context)

# sign up
def signup(request):
    context = {}
    return render(request, 'signup.html', context)

# index: home page 
def index(request):
    user = request.user
    context = {'user': user}

    collection = db['Taipei_gov']
    displayList = []
    for i in range(3):
        ran = random.randrange(0, 550)
        displayList.append(collection.find_one({"spotID": ran}))

    context = {
        'displayList': displayList,
    }
    return render(request, 'index.html', context)

# start
def startDropDown(request):

    # 出遊人數
    max_num = 7
    num_options = []
    for i in range(max_num):
        num_options.append(i+1)
    selected_num = None
    if request.method == "POST":
        selected_num = request.POST.get("numbers")

    # 遊玩時間
    travel_duration = ["Half Day", "One Day", "Two Days", "Three Days", "Four Days"]
    selected_time = None
    if request.method == "POST":
        selected_time = request.POST.get("duration")

    # 交通工具
    # transportations = ["機車", "汽車", "腳踏車", "大眾運輸"]
    # selected_trans = None
    # if request.method == "POST":
    #     selected_trans = request.POST.get("trans")

    # SAVE ROOM_RECORDS
    collection = cluster["JourneyGo_DB"]["Room_spec"]
    dt = datetime.now()
    ts = datetime.timestamp(dt)

    # create post
    post = {"build_time": dt, 
            "member_limitation": selected_num, 
            "duration": selected_time, 
            # "transportation": selected_trans, 
            "members": [], 
            "vote_results": [],
            "recommendations": [],
    }
    if selected_num and selected_time : # and selected_trans
        collection.insert_one(post)
        return redirect('room2')


    context = {
        'nums': num_options,
        'selected_num': selected_num,
        'travel_duration': travel_duration,
        'selected_time': selected_time,
        # 'transportations': transportations,
        # 'selected_trans': selected_trans,
    }
    return render(request, 'start.html', context)

# room 
def room(request):
    context = {}
    return render(request, 'room.html', context)

def room2(request):
    # show login user's friends
    collection = db['User_account']
    userFirstName = request.user.first_name
    userAcc = collection.find_one({"firstName": userFirstName})
    friendList = userAcc['friendList']

    friends_name = []
    friends_pic = []
    friends_hash = []
    for f in friendList:
        friendAcc = collection.find_one({"firstName": f})
        friends_name.append(friendAcc['firstName'] + " " + friendAcc['lastName'])
        friends_pic.append(friendAcc['pic'])
        friends_hash.append(friendAcc['hashtag'])
    
    # get room spec
    collection = cluster['JourneyGo_DB']['Room_spec']
    latest_record = None
    mem_limit = None
    for doc in collection.find().sort('_id',-1).limit(1): # the only doc
        latest_record = doc
        mem_limit = int(doc['member_limitation'])-1

    # save invited friends:
    if request.method == "POST":
        collection.update({"_id": latest_record['_id']}, {"$push": {"members": userFirstName}}) # save myself 
        invited = request.POST.getlist("invited[]")
        for i in invited:
            fn = i.split()[0]
            collection.update({"_id": latest_record['_id']}, {"$push": {"members": fn}}) # save invited friends
        return HttpResponse(status=200)

    context = {
        'friends_name': friends_name,
        'friends_pic': friends_pic,
        'friends_hash': friends_hash,
        'mem_limit': mem_limit,
    }
    return render(request, 'room2.html', context)

def finalRoom(request):

    collection = db['Room_spec']
    latest_room = collection.find().sort('_id',-1).limit(1)
    members = []
    for m in latest_room[0]['members']:
         members.append(db['User_account'].find({'firstName': m})[0])

    context = {
        'members': members,
    }
    return render(request, 'finalRoom.html', context)

## 進階推薦
def give_recommendations(index, print_recommendation = False, print_recommendation_plots= False, print_genres =False):
    index_recomm = cos_sim_data.loc[index].sort_values(ascending=False).index.tolist()[1:11]
    spots_recomm =  data['name'].loc[index_recomm].values
    result = {'Spots':spots_recomm,'Index':index_recomm}
    if print_recommendation==True:
        #print('The visited spot: %s \n'%(data['name'].loc[index]))
        k=1
        for spot in spots_recomm:
            #print('The number %i recommended spot is this one: %s \n'%(k,spot))
            k = k+1
    if print_recommendation_plots==True:
        #print('The plot of the visited spot is this one:\n %s \n'%(data['intro'].loc[index]))
        k=1
        for q in range(len(spots_recomm)):
            plot_q = data['intro'].loc[index_recomm[q]]
            #print('The plot of the number %i recommended spot is this one:\n %s \n'%(k,plot_q))
            k=k+1
    if print_genres==True:
        #print('The categories of the visited spot is this one:\n %s \n'%(data['categories'].loc[index]))
        k=1
        for q in range(len(spots_recomm)):
            plot_q = data['categories'].loc[index_recomm[q]]
            #print('The plot of the number %i recommended spot is this one:\n %s \n'%(k,plot_q))
            k=k+1
    return result

## 基本推薦
def basic_rec(memberList, time, prefList):
    collection = db['User_account']
    userPref = []
    for mem in memberList:
        new_pref = collection.find({"firstName": mem})[0]['balPref']
        userPref.extend(new_pref)
    collection = db['Taipei_gov']
    demon = collection.find({"categories" : { "$in" : userPref}}) #all spots
    demon = list(demon)
    angel = random.choices(demon, k=10)
    return angel

def spotvote(request):

    # 取得房間資訊
    collection = db['Room_spec']
    latest_room = collection.find().sort('_id',-1).limit(1)
    members = latest_room[0]['members']
    duration = latest_room[0]['duration']
    #transportation = latest_room[0]['transportation']

    # 取得group member喜好
    pref_list = []
    collection = db['User_account']
    for member in members:
        personal_pref_list = collection.find({"firstName": member})[0]['balPref']
        for cat in personal_pref_list:
            pref_list.append(cat)
    pref_list = list(dict.fromkeys(pref_list))
    random_category = random.choices(pref_list)

    # # 取得推薦景點
    # recs = basic_rec(members, duration, pref_list)

    # # 儲存推薦景點
    # collection = db['Room_spec']
    
    # if request.method == "GET":
    #     collection.update({"_id": latest_room[0]['_id']}, {"$set": {"recommendations": []}})
    #     for rec in recs:
    #         # print("推薦的景點: ", rec['_id'])
    #         collection.update({"_id": latest_room[0]['_id']}, {"$push": {"recommendations": rec['_id']}}) # save recs

    collection = db['Taipei_gov']
    base_index = collection.find_one({"categories": { "$in": random_category}})['_id']
    recomm_i = give_recommendations(base_index)
    print(recomm_i)
    recomm_list = recomm_i['Index']
    print("New Recommendations: ", recomm_list)

    if request.method == "GET":
        db['Room_spec'].update({"_id": latest_room[0]['_id']}, {"$set": {"recommendations": []}})
        for i in recomm_list:
            db['Room_spec'].update({"_id": latest_room[0]['_id']}, {"$push": {"recommendations": i}}) # save recs

    recs = list(collection.find({"_id" : { "$in" : recomm_list}}))

    # render 
    imgList = []
    introList = []
    nameList = []
    for r in recs:
        imgList.append(r['images'][0])
        introList.append(r['intro'])
        nameList.append(r['name'])

    # 儲存投票結果
    if request.method == "POST":
        collection = db['Room_spec']
        collection.update({"_id": latest_room[0]['_id']}, {"$set": {"vote_results": []}})
        mem_vote = request.POST.getlist("mem_vote[]")
        collection.update({"_id": latest_room[0]['_id']}, {"$push": {"vote_results": mem_vote}})
        return HttpResponse(status=200)

    context = {
        'imgList': imgList,
        'introList': introList,
        'nameList': nameList,
        }
    return render(request, 'spotvote.html', context)

def loading(request):
    context = {}
    return render(request, 'loading.html', context)

def ready(request):
    context = {}
    return render(request, 'ready.html', context)

def calculate_vote():
    # 取得投票紀錄
    collection = db['Room_spec']
    latest_room = collection.find().sort('_id',-1).limit(1)
    vote_arr = latest_room[0]['vote_results']

    # str 轉 int
    new_vote_arr = []
    for l in vote_arr:
        l = [int(x) for x in l]
        new_vote_arr.append(l)
    #print(new_vote_arr)

    # 投票加總
    sum_list = np.sum(new_vote_arr, axis = 0).tolist()
    #print("Sum of arr(axis = 0) : ", sum_list)

    # 決定景點數
    spot_num = 0
    duration = latest_room[0]['duration']
    if duration == "Half Day":
        spot_num = 1
    elif duration == "One Day":
        spot_num = 2
    elif duration == "Two Days":
        spot_num = 4
    elif duration == "Three Days":
        spot_num = 6
    else: # 四天三夜
        spot_num = 8

    # 擇高
    highest = []
    while len(highest) < spot_num:   
        max_value = max(sum_list)
        max_index = sum_list.index(max_value)
        sum_list[max_index] = -1
        highest.append(max_index)
    #print("最高票景點:", highest)

    # 取得推薦景點
    rec_ids = latest_room[0]['recommendations']
    #print("儲存的景點: ", rec_ids)

    # 按找票數用id抓景點
    recs = []
    for i in highest:
        spot_id = rec_ids[i]
        recs.append(db['Taipei_gov'].find({"_id": spot_id}))

    # 抓景點名稱
    docs = [] # 只有景點名稱的list
    for rec in recs:
        for doc in rec: # rec is a curosr with one doc
            docs.append(doc)
            #print("景點:", doc['name'])
    return (docs, spot_num)

def map(request):

# get voting result
    docs = calculate_vote()[0]
    spot_num = calculate_vote()[1]
    tourist_list = []
    for doc in docs:
        #print(doc['name'])
        tourist_list.append(doc['name'])
    #print(tourist_list)

# 景點排序
    docs = [docs[i] for i in route_by_name(tourist_list)[0]]
    new_tourist_list = []
    for doc in docs:
        new_tourist_list.append(doc['name'])
    
    collection = db['Room_spec']
    latest_room = collection.find().sort('_id',-1).limit(1)
    collection.update({"_id": latest_room[0]['_id']}, {"$push": {"new_tourist_list": new_tourist_list}}) # save recs

# find nearby restaurants and logdes
    collection = db['Taipei_gov']
    detail = collection.find({})
    # df 是台北市資料
    df = pd.DataFrame(list(detail))

    collection_res = db['Restaurants']
    detail_res = collection_res.find({})
    # df_res 是餐廳資料

    collection_lod = db['Lodging']
    detail_lod = collection_lod.find({})
    # df_logding 是住宿資料

    df_res = pd.DataFrame(list(detail_res))
    df_lod = pd.DataFrame(list(detail_lod))

    res_list = []
    lod_list = []
    for doc in docs:
        nearby_res_list = []
        nearby_lod_list = []

        for i in range(0,3):
            km_res_list = []
            km_lod_list = []
            for res_id in find_near_by_res(doc['name'])[i]:
                km_res_list.append(df_res.iloc[res_id]['name'])
            for lod_id in find_near_by_lod(doc['name'])[i]:
                km_lod_list.append(df_lod.iloc[lod_id]['name'])
            
            nearby_res_list.append(km_res_list)
            nearby_lod_list.append(km_lod_list)
        
        res_list.append(nearby_res_list)
        lod_list.append(nearby_lod_list)

    ids = range(spot_num)
    #print(ids)

    # 抓交通工具
    collection = db['Room_spec']
    latest_room = collection.find().sort('_id',-1).limit(1)
    # trans = latest_room[0]['transportation']
    duration = latest_room[0]['duration']

    # 抓交通時間(點到點)
    dir = route_by_name(new_tourist_list)[2]
    #print("dir:", dir)

    p2p_times = []
    for i in dir:
        #print("i: ", i)
        hr = i // 3600
        min = (i%3600)//60
        p2p_times.append([hr, min])
    #print("p2p:", p2p_times)

    # 抓交通長度
    p2p_distance = [] 
    for d in route_by_name(new_tourist_list)[1]:
        #print("d: ", d)
        p2p_distance.append(round(d/1000))
    #print("p2p_distance:", p2p_distance)

    km_signs = ["1km", "3km", "5km"]
    rrr = zip(res_list, km_signs)
    lll = zip(lod_list, km_signs)

    context = {
        'tourist_info': zip(docs, res_list, lod_list, ids, p2p_times, p2p_distance),
        'docs': docs,
        # 'trans': trans,
        'duration': duration,
    }
    return render(request, 'map.html', context)

def result(request):
    # get voting result
    docs = calculate_vote()[0]
    spot_num = calculate_vote()[1]
    tourist_list = []
    for doc in docs:
        tourist_list.append(doc['name'])

# 景點排序
    docs = [docs[i] for i in route_by_name(tourist_list)[0]]
    new_tourist_list = []
    for doc in docs:
        new_tourist_list.append(doc['name'])

# find nearby restaurants and logdes
    collection = db['Taipei_gov']
    detail = collection.find({})
    # df 是台北市資料
    df = pd.DataFrame(list(detail))

    collection_res = db['Restaurants']
    detail_res = collection_res.find({})
    # df_res 是餐廳資料

    collection_lod = db['Lodging']
    detail_lod = collection_lod.find({})
    # df_logding 是住宿資料

    df_res = pd.DataFrame(list(detail_res))
    df_lod = pd.DataFrame(list(detail_lod))

    res_list = []
    lod_list = []
    for doc in docs:
        #print(doc['name'])
        nearby_res_list = []
        nearby_lod_list = []

        for i in range(0,3):
            km_res_list = []
            km_lod_list = []
            for res_id in find_near_by_res(doc['name'])[i]:
                km_res_list.append(df_res.iloc[res_id]['name'])
            for lod_id in find_near_by_lod(doc['name'])[i]:
                km_lod_list.append(df_lod.iloc[lod_id]['name'])
            
            nearby_res_list.append(km_res_list)
            nearby_lod_list.append(km_lod_list)
        
        res_list.append(nearby_res_list)
        lod_list.append(nearby_lod_list)

    # 抓交通時間
    dir = route_by_name(new_tourist_list)[2]
    #print(dir)

    p2p_times = []
    total_time = 0

    for i in dir:
        hr = i // 3600
        min = (i%3600)//60
        p2p_times.append([hr, min])
        total_time += int(i)
    total_HM = [total_time//3600, (total_time%3600)//60]


    # 抓交通長度
    length = route_by_name(new_tourist_list)[1]
    #print(length)

    ids =  range(spot_num)
    # 抓 room spec
    collection = db['Room_spec']
    latest_room = collection.find().sort('_id',-1).limit(1)
    # trans = latest_room[0]['transportation']
    duration = latest_room[0]['duration']

    googleMapUrl = dirurl(new_tourist_list)

    weather_imgUrl = weather()

    context = {
        'tourist_info': zip(docs, res_list, lod_list, ids),
        'tf': zip(docs, ids),
        # 'dtd': zip(docs, trans, duration),
        'docs': docs,
        # 'trans': trans,
        'duration': duration,
        'moreInfo': zip(docs, res_list, lod_list),
        'res_list': res_list,
        "lod_list": lod_list,
        'total_HM': total_HM,
        'p2p_times': p2p_times,
        'p2p_distances':length,
        'googleMapUrl': googleMapUrl,
        'weather_imgUrl': weather_imgUrl,
    }
    return render(request, 'result.html', context)

def dirurl(touristList):
    directionURL = 'https://www.google.com.tw/maps/dir/'
    for i in touristList:
        i = i.replace(" ","")
        directionURL = directionURL + i + '/'
    return directionURL

def friends(request): # 大前提： 沒有重複的 first name

    collection = cluster['JourneyGo_DB']['User_account']

    # 先確定使用者
    userFirstName = request.user.first_name
    userLastName = request.user.last_name 
    userAcc = collection.find_one({"firstName": userFirstName})
    
    # 顯示好友資料
    if userAcc['friendList'] is not None:
        friends = userAcc['friendList'] # Type: String in Array
        friendsDocs = []                # Type: User Document
        f_IDs = []
        for f in friends:
            friendsDocs.append(collection.find_one({"firstName": f}))
            f_IDs.append(collection.find_one({"firstName": f})['_id'])

    # 刪除好友
    exf = None  # exf stands for "ex-friend's first name"
    if request.method == "POST":
        exf = request.POST.get("exf") 
        if exf is not None:
            collection.update({"firstName": userAcc['firstName']}, {"$pull": {"friendList": exf}})
            friendsDocs.remove(collection.find_one({"firstName": exf}))

    # 新增朋友
    addedID = None
    if request.method == "POST":
        addedID = request.POST.get("addedID")
        if addedID is not None:
            # add to ['friendList']
            new_friend = collection.find_one({"_id": int(addedID)})
            collection.update({"_id": userAcc['_id']}, {"$push": {"friendList": new_friend['firstName']}})
            # add to friendsDocs
            friendsDocs.append(collection.find_one({"_id": int(addedID)}))
            return redirect('friends')

    context = {
        'userAcc': userAcc,
        'ffid': zip(friendsDocs, f_IDs),
    }
    return render(request, 'friends.html', context)

def fenci(sentence: str)->str:
    words = jieba.lcut_for_search(sentence)
    return ' '.join(words)

def searchRec(request):

    collection = db['Taipei_gov']
    context = {}

    # Search Engine
    keywords = None
    cur = None
    if request.method == "POST": # Get input value
        keywords = request.POST.get("keywords") # type: str
        #print(type(fenci(keywords)))
        key_list = fenci(keywords).split()
        cur = collection.find({"splited_words": { "$in": key_list }}) # cur is a list of multiple dictionaries

    # Personal Recommendation
    if request.user.is_authenticated:
        collection = db['User_account']
        user = request.user.first_name
        user_pref = collection.find({"firstName": user})[0]['balPref']
        print(user_pref)
        collection = db['Taipei_gov']
        demon = collection.find({"categories" : { "$in" : user_pref}}) #all spots
        demon = list(demon)
        recs = random.choices(demon, k=6)

        context = {
            'recs':recs, #default rec
            'recN': random.randrange(1, 5),
            'keywords': keywords,
            'cur': cur, #search results
            'user_pref': user_pref,
        }

    # Random Recommendation
    else:
        ran = random.sample(range(0, 550), 9)
        collection = db['Taipei_gov']
        recs = collection.find({"_id" : { "$in" : ran}})
        recs = list(recs)
        context = {
            'recs': recs,
            'recN': random.randrange(1, 5),
            'keywords': keywords,
            'cur': cur, #search results
        }

    return render(request, 'searchPage.html', context)


def setting(request):
    context = {}
    return render(request, 'setting.html', context)

def balancegame(request):
    context = {}
    return render(request, 'balancegame.html', context)

def art(request):
    collection = db['User_account']
    userFirstName = request.user.first_name

    # get pref from JS: 
    if request.method == "POST":
        pref = request.POST.getlist("pref[]")
        for p in pref:
            collection.update({"firstName": userFirstName}, {"$push": {"balPref": p}})

    context = {}
    return render(request, 'art.html', context)    

def health(request):
    collection = db['User_account']
    userFirstName = request.user.first_name
    
    # get pref from JS: 
    if request.method == "POST":
        pref = request.POST.getlist("pref[]")
        for p in pref:
            collection.update({"firstName": userFirstName}, {"$push": {"balPref": p}})

    context = {}
    return render(request, 'health.html', context)

def other(request):
    collection = db['User_account']
    userFirstName = request.user.first_name

    # get pref from JS: 
    if request.method == "POST":
        pref = request.POST.getlist("pref[]")
        for p in pref:
            collection.update({"firstName": userFirstName}, {"$push": {"balPref": p}})

    context = {}
    return render(request, 'other.html', context)

def base1(request):
    context = {}
    return render(request, 'base1.html', context)

def base2(request):
    context = {}
    return render(request, 'base2.html', context)

def test(request):
    context = {}
    return render(request, 'test.html', context)

def feedback(request):
    collection = db['Room_spec']
    latest_room = collection.find().sort('_id',-1).limit(1)
    spots = latest_room[0]['new_tourist_list']

    img_list = []
    collection = db['Taipei_gov']
    for spot in spots[0]:
        img_list.append(collection.find_one({"name": spot})['images'][0])
    
    print(img_list)

    context = {
        'spots': spots[0],
        'img_list': img_list,
    }
    return render(request, 'feedback.html', context)
        
def find_near_by_res(tourist):
    collection = db['Taipei_gov']
    detail = collection.find({})
    # df 是台北市資料
    df = pd.DataFrame(list(detail))
    collection_res = db['Restaurants']
    detail_res = collection_res.find({})
    # df_res 是餐廳資料
    df_res = pd.DataFrame(list(detail_res))
    # 輸入名稱
    des_lat = 0
    des_lng = 0
    #   找經緯度
    for i in range(len(df)):
        if df.iloc[i]['name'] == tourist:
            des_lat = df.iloc[i]["latitude"]
            des_lng = df.iloc[i]["longitude"]
    nearby1 = []
    nearby2 = []
    nearby3 = []
    # 找相關景點
    for i in range(len(df_res)):
        distance = (abs(df_res.iloc[i]['lat'] - float(des_lat)) + abs(df_res.iloc[i]['lng'] - float(des_lng)))*1000000
        if distance < 1000:
            nearby1.append(i)
        if distance >= 1000 and distance < 3000:
            nearby2.append(i)
        if distance >= 3000 and distance < 5000:
            nearby3.append(i)

    # 移除重複
    name_duplicate1 = []
    remove_duplicate1 = []
    for i in nearby1:
        if df_res.iloc[i]['name'] not in name_duplicate1:
            name_duplicate1.append(df_res.iloc[i]['name'])
            remove_duplicate1.append(i)

    name_duplicate2 = []
    remove_duplicate2 = []
    for i in nearby2:
        if df_res.iloc[i]['name'] not in name_duplicate2:
            name_duplicate2.append(df_res.iloc[i]['name'])
            remove_duplicate2.append(i)

    name_duplicate3 = []
    remove_duplicate3 = []
    for i in nearby3:
        if df_res.iloc[i]['name'] not in name_duplicate3:
            name_duplicate3.append(df_res.iloc[i]['name'])
            remove_duplicate3.append(i)
        
    # 沒有重複的餐廳list
    return [remove_duplicate1, remove_duplicate2, remove_duplicate3]

def find_near_by_lod(tourist):
    collection = db['Taipei_gov']
    detail = collection.find({})
    # df 是台北市資料
    df = pd.DataFrame(list(detail))
    collection_lod = db['Lodging']
    detail_lod = collection_lod.find({})
    # df_res 是餐廳資料
    df_lod = pd.DataFrame(list(detail_lod))
    # 輸入名稱
    des_lat = 0
    des_lng = 0
    #   找經緯度
    for i in range(len(df)):
        if df.iloc[i]['name'] == tourist:
            des_lat = df.iloc[i]["latitude"]
            des_lng = df.iloc[i]["longitude"]
    nearby1 = []
    nearby2 = []
    nearby3 = []
    # 找相關景點
    for i in range(len(df_lod)):
        distance = (abs(df_lod.iloc[i]['lat'] - float(des_lat)) + abs(df_lod.iloc[i]['lng'] - float(des_lng)))*1000000
        if distance < 1000:
            nearby1.append(i)
        if distance >= 1000 and distance < 3000:
            nearby2.append(i)
        if distance >= 3000 and distance < 5000:
            nearby3.append(i)

    # 移除重複
    name_duplicate1 = []
    remove_duplicate1 = [] 
    for i in nearby1:
        if df_lod.iloc[i]['name'] not in name_duplicate1:
            name_duplicate1.append(df_lod.iloc[i]['name'])
            remove_duplicate1.append(i)

    name_duplicate2 = []
    remove_duplicate2 = [] 
    for i in nearby2:
        if df_lod.iloc[i]['name'] not in name_duplicate2:
            name_duplicate2.append(df_lod.iloc[i]['name'])
            remove_duplicate2.append(i)

    name_duplicate3 = []
    remove_duplicate3 = [] 
    for i in nearby3:
        if df_lod.iloc[i]['name'] not in name_duplicate3:
            name_duplicate3.append(df_lod.iloc[i]['name'])
            remove_duplicate3.append(i)
    
    # 沒有重複的餐廳list
    return [remove_duplicate1, remove_duplicate2, remove_duplicate3]

# 輸入的如果是[數字(在資料庫裡面的順序)]
def route(tourist_list):
    # 重要(我的地圖API Key)
    gmaps = googlemaps.Client(key='AIzaSyD1Jg_xEQU9QpopRzjWxyHrpoCYbBjA6gE')
    collection = db['Taipei_gov']
    detail = collection.find({})
    df = pd.DataFrame(list(detail))
    location = []

    for i in range(len(tourist_list)):
        location.append(df.iloc[i]["name"])
    direction = []
    for i in location:
        travel = []
        for j in location:
            directions_result = gmaps.directions(i,j,mode="transit")
            if len(directions_result) != 0:
                travel.append(directions_result[0]['legs'][0]['duration']['value'])
            else:
                travel.append(0)
        direction.append(travel)
    k = 0
    for i in range(len(direction)):
        direction[i][k] = 999999
        k += 1
    trip = []
    # Find the index of the minimum duration from starting line
    first_index = direction[0].index(min(direction[0]))
    # Set the visited place and started place and large number in order to not be selected
    direction[first_index][0] = 999999
    # For traveling sequence
    trip.append(0)

    start = first_index
    trip.append(start)

    # Remove the starting line and the second place which was started from the starting line
    for i in range(len(direction)-2):
        end = direction[start].index(min(direction[start]))
        for i in trip:
            direction[end][i] = 999999
        trip.append(end)
    # Make the last ended place become the next starting line
        start = end
    # The result
    return trip

# 輸入的如果是[景點名稱]
def route_by_name(tourist_list):
    # 重要(我的地圖API Key)
    gmaps = googlemaps.Client(key='AIzaSyD1Jg_xEQU9QpopRzjWxyHrpoCYbBjA6gE')
    collection = db['Taipei_gov']
    detail = collection.find({})
    df = pd.DataFrame(list(detail))
    location = []
    distance =[]
    travel_time = []
    travel_distance = []

    direction = []
    for i in tourist_list:
        travel = []
        length = []
        for j in tourist_list:
            directions_result = gmaps.directions(i,j,mode="transit")
            if len(directions_result) != 0:
                travel.append(directions_result[0]['legs'][0]['duration']['value'])
                length.append(directions_result[0]['legs'][0]['distance']['value'])
            else:
                travel.append(0)
                length.append(0)
        direction.append(travel)
        distance.append(length)
#     print(direction)
    k = 0
    for i in range(len(direction)):
        direction[i][k] = 999999
        k += 1
    trip = []
    first_index = direction[0].index(min(direction[0]))
    travel_time.append(direction[first_index][0])
    travel_distance.append(direction[first_index][0])
    direction[first_index][0] = 999999
    trip.append(0)
    start = first_index
    trip.append(start)
    for i in range(len(direction)-2):
        end = direction[start].index(min(direction[start]))
        for i in trip:
            travel_time.append(direction[end][i])
            travel_distance.append(direction[end][i])
            direction[end][i] = 999999
        trip.append(end)
        start = end
#     print(direction)
    return (trip, travel_distance[:-1],travel_time[:-1])

def weather():
    # api get real time weather
    w = requests.get("https://api.openweathermap.org/data/2.5/weather?q=Taipei&appid=67f257f406fd0a609b06aebb3e9e5814")
    data = w.json()
    print(data)
    icon = data.get('weather')[0].get('icon')
    imageUrl = "http://openweathermap.org/img/w/" + icon + ".png"
    
    return imageUrl