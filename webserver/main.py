#!/usr/bin/python

import getData
import sys

from pymongo import MongoClient
client = MongoClient()

splitText = sys.argv[2].split("*")

queryArray = [[splitText[0], splitText[1]], ["",""], ["",""], ["",""], ["",""]]

db = client['scheduler']
collection = db['userData']

foundDB = collection.find_one({"sessionID" : sys.argv[1]})

if foundDB != None:
    
    isFound = False
    
    for x in foundDB["Data"]:
        if sys.argv[2] == x["Course"]["Course"]:
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
    newOutput["Data"] = output;
    newOutput["sessionID"] = sys.argv[1];

    if foundDB == None:
        collection.insert_one(newOutput)
        print "Created"
    else:
        if len(output) == 0:
            print "Error: No sections"
            print "1"
        else:
            collection.update({"sessionID" : sys.argv[1]}, {'$push': {'Data': output[0]}}, True)
            print "Updated"

    print "0"
