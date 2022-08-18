from cgi import test
from multiprocessing import context
from os import remove
from unicodedata import name
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
            return redirect('balancegame')
    else:
        form = RegisterUserForm()
    return render(request, 'register.html', {'form': form})

# login
def login1(request):
    if request.method == 'POST':
        # username = request.POST['username']
        # password = request.POST['password']
        # user = authenticate(request, username=username, password=password)
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
    db = cluster["test"]
    collection = db["records_test"]

    # Getting the current date and time
    dt = datetime.now()
    # getting the timestamp
    ts = datetime.timestamp(dt)

    # create post
    post = {"創建時間": dt, 
            "出遊人數": selected_num, 
            "遊玩天數": selected_time, 
            "交通工具": selected_trans, 
            "成員": None, 
            "投票結果": None,
    }
    if selected_num and selected_time and selected_trans:
        collection.insert_one(post)

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
def room2(request):
    collection = db['User_account']
    #friends = []
    friends_name = []
    friends_pic = []
    friends_hash = []
    for i in range(6):
        #friends.append(collection.find_one({'_id': i}))
        friends_name.append((collection.find_one({'_id': i})['firstName']+" "+collection.find_one({'_id': i})['lastName']))
        friends_pic.append(collection.find_one({'_id': i})['pic'])
        friends_hash.append(collection.find_one({'_id': i})['hashtag'])
    context = {
        #'friends': friends, 
        'friends_name': friends_name, #list
        'friends_pic': friends_pic,   #list
        'friends_hash': friends_hash, #list
    }
    #print(friends_pic) 確認有存到，但js那邊get不到
    return render(request, 'room2.html', context)

def spotvote(request):
    
    # 先隨機抓六張圖
    n = []
    while len(n) <= 6: #推薦幾個景點
        id = random.randrange(0, 550)
        if id not in n: n.append(id)
        else: continue
    print(n)

    collection = db['Taipei_gov']
    spots = []
    for i in n:
        spots.append(collection.find_one({"_id": i}))

    imgList = []
    introList = []
    nameList = []
    for spot in spots:
        imgList.append(spot['images'][0])
        introList.append(spot['intro'])
        nameList.append(spot['name'])

    context = {
        'spots': spots,
        'imgList': imgList,
        'introList': introList,
        'nameList': nameList,
    }
    return render(request, 'spotvote.html', context)

def ready(request):
    context = {

    }
    return render(request, 'ready.html', context)

def decide(request):
    context = {

    }
    return render(request, 'decide.html', context)

def result(request):
    collection = db['Taipei_gov']
    result = collection.find_one({"name": "台北101"})
    #print(result)

    context = {
        'result_name': result['name'], 
        'result_intro': result['intro'], 
        'result_img': result['images'][0]
    }
    return render(request, 'result.html', context)

def friends(request):

    # 先確定使用者
    user = request.user

    
    # 抓好友資料
    db = cluster['JourneyGo_DB']
    collection = db['User_account']
    friends = []
    friendsID = []
    for i in range(6): #num要改
        friends.append(collection.find_one({"_id": i}))
        friendsID.append(friends[i]['_id'])

    # 刪除好友功能

    exf = None
    exl = None
    if request.method == "POST":
        exf = request.POST.get("exf")
        exl = request.POST.get("exl")
        #print( exf, exl)
        # collection.update_one({"_id": 0}, {"$pull": {"friendList": exf}})
        collection.find_one_and_delete({"firstName":exf,"lastName":exl})

    #print(friends[0]['_id'])

    # 新增朋友功能
    context = {
        'friends': friends,
        'friendsID': friendsID,
        'ffid': zip(friends, friendsID),
        'user': user,
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
        'user': user
    }
    return render(request, 'setting.html', context)

def art(request):
    context = {}
    return render(request, 'art.html', context)    

def balancegame(request):
    context = {}
    return render(request, 'balancegame.html', context)

def health(request):
    context = {}
    return render(request, 'health.html', context)

def other(request):
    context = {}
    return render(request, 'other.html', context)

def base1(request):
    context = {}
    return render(request, 'base1.html', context)

def base2(request):
    context = {}
    return render(request, 'base2.html', context)

