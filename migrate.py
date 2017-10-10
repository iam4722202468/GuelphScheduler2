from pymongo import MongoClient
client = MongoClient()

db = client['scheduler']
collection = db['userData']
cachedCourses = db['cachedCourses']

z = collection.find({})

for x in z:
    if "Data" in x:
        courseList = x['Data']
        courseArray = []
        
        print x
        
        for courses in courseList:
            newObject = {}
            
            print courses['Course']['Course']
            courseArray.append(courses['Course']['Course'])
            cachedCourses.insert_one(courses['Course'])
        
        sessionID = x['sessionID']
        collection.delete_one({'sessionID': sessionID})
        
        newObject = {}
        newObject['sessionID'] = sessionID
        newObject['Data'] = courseArray
        
        collection.insert_one(newObject)
        
        print courseArray
