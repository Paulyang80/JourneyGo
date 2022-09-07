# from cgi import test
# import collections
# from gc import collect
# from hashlib import new
# from ipaddress import collapse_addresses
# from multiprocessing import context
# from operator import truediv
# from os import remove
# from unicodedata import name
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
import time

# Make MongoDB connection with Pymongo
cluster = MongoClient("mongodb+srv://Tang:108306058@journeygo.yhfdrry.mongodb.net/?retryWrites=true&w=majority")
db = cluster['JourneyGo_DB']

# Views

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
                        "hashtag": "", "pic": "", "friendList": [], "intro": ""}
                    collection.insert_one(post)
                else:
                    post = {"_id": int(collection.count()), "firstName": user.first_name, "lastName": user.last_name, "email": user.email, "password": user.password,
                        "hashtag": "", "pic": "", "friendList": [], "intro": ""}
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
    travel_duration = ["半天", "一天", "兩天一夜", "三天兩夜"]
    selected_time = None
    if request.method == "POST":
        selected_time = request.POST.get("duration")

    # 交通工具
    transportations = ["機車", "汽車", "腳踏車", "大眾運輸"]
    selected_trans = None
    if request.method == "POST":
        selected_trans = request.POST.get("trans")

    # SAVE ROOM_RECORDS
    collection = cluster["JourneyGo_DB"]["Room_spec"]
    dt = datetime.now()
    ts = datetime.timestamp(dt)

    # create post
    post = {"build_time": dt, 
            "member_limitation": selected_num, 
            "duration": selected_time, 
            "transportation": selected_trans, 
            "members": [], 
            "vote_results": [],
            "recommendations": [],
    }
    if selected_num and selected_time and selected_trans:
        collection.insert_one(post)
        return redirect('room2')


    context = {
        'nums': num_options,
        'selected_num': selected_num,
        'travel_duration': travel_duration,
        'selected_time': selected_time,
        'transportations': transportations,
        'selected_trans': selected_trans,
    }
    return render(request, 'start.html', context)

# room 
def room(request):
    context = {
       
    }
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

def basic_rec(memberList, time, prefList):
    collection = db['User_account']
    userPref = []
    for mem in memberList:
        new_pref = collection.find({"firstName": mem})[0]['balPref']
        userPref.extend(new_pref)
    collection = db['Taipei_gov']
    demon = collection.find({"categories" : { "$in" : userPref}}) #all spots
    demon = list(demon)
    angel = random.choices(demon, k=5)
    return angel

def spotvote(request):
    print("SPOTVOTE!")
    # Reccomandation Computing
    collection = db['Room_spec']

    latest_room = collection.find().sort('_id',-1).limit(1)
    members = latest_room[0]['members']
    duration = latest_room[0]['duration']
    transportation = latest_room[0]['transportation']

    # 取得group member喜好
    pref_list = []
    collection = db['User_account']
    for member in members:
        personal_pref_list = collection.find({"firstName": member})[0]['balPref']
        for cat in personal_pref_list:
            pref_list.append(cat)

    # 取得推薦景點
    recs = basic_rec(members, duration, pref_list)

    # 儲存推薦景點
    collection = db['Room_spec']
    #collection.update({"_id": latest_room[0]['_id']}, {"$set": {"recommendations": []}})
    for rec in recs:
        print("推薦的景點: ", rec['_id'])
        collection.update({"_id": latest_room[0]['_id']}, {"$push": {"recommendations": rec['_id']}}) # save recs

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
        mem_vote = request.POST.getlist("mem_vote[]")
        collection = db['Room_spec']
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
    print(new_vote_arr)

    # 投票加總
    sum_list = np.sum(new_vote_arr, axis = 0).tolist()
    print("Sum of arr(axis = 0) : ", sum_list)

    # 擇三高
    highest_three = []
    while len(highest_three) < 3:   
        max_value = max(sum_list)
        max_index = sum_list.index(max_value)
        sum_list[max_index] = -1
        highest_three.append(max_index)
    print(highest_three)

    # 取得推薦景點
    rec_ids = latest_room[0]['recommendations']
    print("儲存的景點: ", rec_ids)

    # 按找票數用id抓景點
    recs = []
    for i in highest_three:
        spot_id = rec_ids[i]
        recs.append(db['Taipei_gov'].find({"_id": spot_id}))

    # 抓景點名稱
    docs = [] # 只有景點名稱的list
    for rec in recs:
        for doc in rec: # rec is a curosr with one doc
            docs.append(doc)
            #print("景點:", doc['name'])
    return docs

def map(request):

# get voting result
    docs = calculate_vote()
    tourist_list = []
    for doc in docs:
        #print(doc['name'])
        tourist_list.append(doc['name'])

# 景點排序
    docs = [docs[i] for i in route_by_name(tourist_list)]
    for doc in docs:
        #print(doc['name'])

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
        for res_id in find_near_by_res(doc['name']):
            nearby_res_list.append(df_res.iloc[res_id]['name'])
        for lod_id in find_near_by_lod(doc['name']):
            nearby_lod_list.append(df_lod.iloc[lod_id]['name'])
        res_list.append(nearby_res_list)
        lod_list.append(nearby_lod_list)

    context = {
        'tourist_info': zip(docs, res_list, lod_list),
    }
    return render(request, 'map.html', context)

def result(request):
    
# get voting result
    docs = calculate_vote()
    tourist_list = []
    for doc in docs:
        tourist_list.append(doc['name'])

# 景點排序
    docs = [docs[i] for i in route_by_name(tourist_list)]

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
        for res_id in find_near_by_res(doc['name']):
            nearby_res_list.append(df_res.iloc[res_id]['name'])
        for lod_id in find_near_by_lod(doc['name']):
            nearby_lod_list.append(df_lod.iloc[lod_id]['name'])
        res_list.append(nearby_res_list)
        lod_list.append(nearby_lod_list)

    context = {
        'tourist_info': zip(docs, res_list, lod_list),
    }
    return render(request, 'result.html', context)

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

    # Search Engine
    keywords = None
    cur = None
    if request.method == "POST": # Get input value
        keywords = request.POST.get("keywords") # type: str
        #print(type(fenci(keywords)))
        key_list = fenci(keywords).split()
        cur = collection.find({"splited_words": { "$in": key_list }}) # cur is a list of multiple dictionaries

    
    # Random Reccomendation
    ran_list = []
    while len(ran_list)<6:
        rec = random.randint(0,520)
        if rec not in ran_list:
            ran_list.append(rec)
        else:
            continue

    # Get Random Data by _id 
    spots = collection.find({"_id":{"$in":ran_list}})

    # Render context
    context = {
        'spots':spots, #default rec
        'recN': random.randrange(1, 5),
        'keywords': keywords,
        'cur': cur, #search results
    }

    return render(request, 'searchPage.html', context)


def setting(request):
    collection = db['User_account']
    user = collection.find_one({"_id": 0})

    context = {
    }
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

    context = {
        
    }
    return render(request, 'art.html', context)    

def health(request):
    collection = db['User_account']
    userFirstName = request.user.first_name
    
    # get pref from JS: 
    if request.method == "POST":
        pref = request.POST.getlist("pref[]")
        for p in pref:
            collection.update({"firstName": userFirstName}, {"$push": {"balPref": p}})

    context = {
        
    }
    return render(request, 'health.html', context)

def other(request):
    collection = db['User_account']
    userFirstName = request.user.first_name

    # get pref from JS: 
    if request.method == "POST":
        pref = request.POST.getlist("pref[]")
        for p in pref:
            collection.update({"firstName": userFirstName}, {"$push": {"balPref": p}})

    context = {
        
    }
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
    nearby = []
    # 找相關景點
    for i in range(len(df_res)):
        if (abs(df_res.iloc[i]['lat'] - float(des_lat)) + abs(df_res.iloc[i]['lng'] - float(des_lng)))*1000000 < 5000:
            nearby.append(i)
    name_duplicate = []
    remove_duplicate = []
    # 移除重複
    for i in nearby:
        if df_res.iloc[i]['name'] not in name_duplicate:
            name_duplicate.append(df_res.iloc[i]['name'])
            remove_duplicate.append(i)
    # 沒有重複的餐廳list
    return remove_duplicate

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
    nearby = []
    # 找相關景點
    for i in range(len(df_lod)):
        if (abs(df_lod.iloc[i]['lat'] - float(des_lat)) + abs(df_lod.iloc[i]['lng'] - float(des_lng)))*1000000 < 5000:
            nearby.append(i)
    name_duplicate = []
    remove_duplicate = []
    # 移除重複
    for i in nearby:
        if df_lod.iloc[i]['name'] not in name_duplicate:
            name_duplicate.append(df_lod.iloc[i]['name'])
            remove_duplicate.append(i)
    # 沒有重複的餐廳list
    return remove_duplicate

# 輸入的如果是[數字(在資料庫裡面的順序)]
def route(tourist_list):
    # 重要(我的地圖API Key)
    gmaps = googlemaps.Client(key='AIzaSyBNTyuvWTzW7i8x7_1wRd444Wg1OFCtFFU')
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
    gmaps = googlemaps.Client(key='AIzaSyBNTyuvWTzW7i8x7_1wRd444Wg1OFCtFFU')
    collection = db['Taipei_gov']
    detail = collection.find({})
    df = pd.DataFrame(list(detail))
    location = []

    direction = []
    for i in tourist_list:
        travel = []
        for j in tourist_list:
            directions_result = gmaps.directions(i,j,mode="transit")
            if len(directions_result) != 0:
                travel.append(directions_result[0]['legs'][0]['duration']['value'])
            else:
                travel.append(0)
        direction.append(travel)
#     print(direction)
    k = 0
    for i in range(len(direction)):
        direction[i][k] = 999999
        k += 1
    trip = []
    first_index = direction[0].index(min(direction[0]))
    direction[first_index][0] = 999999
    trip.append(0)
    start = first_index
    trip.append(start)
    for i in range(len(direction)-2):
        end = direction[start].index(min(direction[start]))
        for i in trip:
            direction[end][i] = 999999
        trip.append(end)
        start = end
#     print(direction)
    return trip