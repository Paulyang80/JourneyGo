from cgi import test
from django.shortcuts import render
from pymongo import MongoClient
import datetime
import random
from datetime import datetime

# Make MongoDB connection with Pymongo
cluster = MongoClient("mongodb+srv://Tang:108306058@journeygo.yhfdrry.mongodb.net/?retryWrites=true&w=majority")
db = cluster['JourneyGo_DB']

# Views

# login
def login(request):
    input_name = None
    input_email = None
    input_pwd = None
    if request.method == 'POST':
        input_name = request.POST["username"]
        input_email = request.POST["user-email"]
        input_pwd = request.POST["password"]
    
    db = cluster['test']
    collection = db['signup']
    user = collection.find_one({"user_first_name": input_name})

    context = {
        'user': user,
        'username': input_name,
        'user_email': input_email,
        'password': input_pwd,
    }

    return render(request, 'login.html', context)

# sign up
def signup(request):
    context = {}
    if request.method == 'POST':
        context = {
            'user_first_name': request.POST["user-fname"],
            'user_last_name': request.POST["user-lname"],
            'user_email': request.POST["user-email"],
            'password': request.POST["password"],
        }  

    db = cluster['test'] # 要記得改回去
    collection = db['signup']
    collection.insert_one(context)

    return render(request, 'signup.html', context)

# index: home page 
def index(request):
    context = {}
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
    context = {

    }
    return render(request, 'room2.html', context)


def confirmPage(request):
    context = {

    }
    return render(request, 'confirmPage.html', context)

def spotvote(request):
    context = {

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
        # 'ig_pic': api
    }
    return render(request, 'friends.html', context)

def searchRec(request):
    collection = db['Taipei_gov']

    # Random Reccomendation
    ran_list = []
    while len(ran_list)<3:
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





def setting(request):
    collection = db['User_account']
    user = collection.find_one({"_id": 0})

    context = {
        'user': user
    }
    return render(request, 'setting.html', context)




