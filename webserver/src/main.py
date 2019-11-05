#!/usr/bin/python
import sys

from pymongo import MongoClient
client = MongoClient()
    
splitText = sys.argv[2].split("*")
queryArray = [[splitText[0], splitText[1]]]

db = client['scheduler']
collection = db['userData']
cachedCourses = db['cachedCourses']

foundDB = collection.find_one({"sessionID" : sys.argv[1]})

sys.path.insert(0, "./schools/" + sys.argv[3])
import getData

if foundDB != None:
    isFound = False
    
    for x in foundDB["Data"]:
        if sys.argv[2] == x:
            isFound = True
    
    if isFound:
        print "Error: Found"
        print "1"
        sys.exit()

output = getData.getData(queryArray)

if isinstance(output, basestring):
    print output
    print "2"
else:
    newOutput = {}
    newOutput["Data"] = [sys.argv[2]];
    newOutput["sessionID"] = sys.argv[1];

    if foundDB == None:
        if len(output) == 0:
            print "Error: No sections"
            print "1"
        else:
            print "Created"
            print "0"
            collection.insert_one(newOutput)
            cachedCourses.update(
                { 'Course': sys.argv[2] },
                { 'Course': sys.argv[2], 'Data': output[0]['Course'] },
                True
            )
    else:
        if len(output) == 0:
            print "Error: No sections"
            print "1"
        else:
            collection.update(
                {"sessionID": sys.argv[1]},
                {'$push': {'Data': sys.argv[2]}},
                True
            )
            
            cachedCourses.update(
                {"Course": sys.argv[2]},
                {"Course": sys.argv[2], "Data": output[0]['Course']},
                True
            )
            
            print "Updated"
            print "0"
