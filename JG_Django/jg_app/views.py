from cgi import test
from django.shortcuts import render
from pymongo import MongoClient
import datetime
import random
import math



# Make MongoDB connection with Pymongo
cluster = MongoClient("mongodb+srv://Tang:108306058@journeygo.yhfdrry.mongodb.net/?retryWrites=true&w=majority")
db = cluster['JourneyGo_DB']


# Create your views

def index(request):
    collection = db['Taipei_gov']
    test = collection.find_one({"_id": 3})
    return render(request, 'index.html', {'current_time': str(datetime.datetime.now()), 'spot1': test['name'], 'intro1': test['intro']})

def result(request):
    collection = db['Taipei_gov']
    result = collection.find_one({"name": "台北101"})
    #print(result)
    return render(request, 'result.html', {'result_name': result['name'], 'result_intro': result['intro'], 'result_img': result['images'][0]})

def friends(request):
    collection = db['User_account']
    friends = []
    for i in range(6):
        friends.append(collection.find_one({"_id": i}))    
    
    # user_id = "https://www.instagram.com/cy.tang/?__a=1"
    # api = "https://i.instagram.com/api/v1/users/"+user_id+"/info/"

    context = {
        'friends': friends,
        'rows': range(math.ceil(len(friends)/3))
        # 'ig_pic': api
    }
    return render(request, 'friends.html', context)

def searchRec(request):
    collection = db['Taipei_gov']

    # Random Reccomendation
    ran_list = []
    while len(ran_list)<9:
        rec = random.randint(0,520)
        if rec not in ran_list:
            ran_list.append(rec)
        else:
            continue

    # Get Random Data by _id 
    test = collection.find({"_id":{"$in":ran_list}})

    # return render(request, 'searchPage.html', {'context_list1':test[0:3],
    # 'context_list2':test[3:6], 'context_list3':test[6:], 'recN': random.randrange(1, 5)})

    return render(request, 'searchPage.html', {'context_list':test,'recN': random.randrange(1, 5)})


def startDropDown(request):

    # 出遊人數
    max_num = 7
    num_options = []
    for i in range(max_num):
        num_options.append(i+1)
    selected_num = None
    if request.method == "POST":
        selected_num = request.POST.get("numbers")
        n = selected_num

    # 遊玩時間
    travel_duration = ["半天", "一天", "兩天一夜", "三天兩夜"]
    selected_time = None
    if request.method == "POST":
        selected_time = request.POST.get("duration")
        t = selected_time

    # 交通工具
    transportations = ["機車", "汽車", "腳踏車", "大眾運輸"]
    selected_trans = None
    if request.method == "POST":
        selected_trans = request.POST.get("trans")
        tr = selected_trans


    # SAVE ROOM_RECORDS
    db = cluster["test"]
    collection = db["records_test"]

    from datetime import datetime

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


def setting(request):
    collection = db['User_account']
    user = collection.find_one({"_id": 0})

    context = {
        'user': user
    }
    return render(request, 'setting.html', context)
