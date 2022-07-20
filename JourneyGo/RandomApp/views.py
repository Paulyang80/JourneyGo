from django.shortcuts import render
from django.http import HttpResponse
import pymongo
import random 

client = pymongo.MongoClient('mongodb+srv://Tang:108306058@journeygo.yhfdrry.mongodb.net/?retryWrites=true&w=majority')
#Define Db Name
dbname = client['test']
collection = dbname['test']
# print(collection.find_one({"_id":rec}))
# Test random 
rec = random.randint(0,520)
result = collection.find_one({"_id":rec})
# print(result['name'])

    
# Create your views here.
def index(request):
    return HttpResponse(result['name'])

def SearchPage(request):
    #Define Collection
    collection = dbname['test']
    #Find All
    # detail = collection.find({})

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
    # print(test[0:3], test[3:6], test[6:])
    return render(request, 'SearchPage.html', {'context_list':test,'recN': random.randrange(1, 5)})