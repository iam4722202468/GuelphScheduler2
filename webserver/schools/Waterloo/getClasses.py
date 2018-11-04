#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser
import json
import requests
from time import sleep
import re

from pymongo import MongoClient
client = MongoClient()

db = client['scheduler']
collection = db['cachedData']

from subprocess import call

yearRange = '1819'

def getData():
    #call(["wget", "-O", "UG_Course_Chapter.pdf", "http://www.ucalendar.uwaterloo.ca/" + yearRange + "/COURSE/pdfs/UG_Course_Chapter.pdf"])
    #call(["pdftotext", "UG_Course_Chapter.pdf"])
    
    a = open("UG_Course_Chapter.txt").read().replace("\n","").splitlines()
    
    currentObject = {}
    currentSections = []
    
    onLine = 0
    inBlock = False
    Description = ""
    
    for x in a:
        
        splitx = x.split(" ")
        if len(splitx) == 4 and splitx[0].upper() == splitx[0] and splitx[2].upper() == splitx[2] and len(splitx[1]) < 5 : #find course title
            sectionInfo = splitx[2].split(",") #get section types to make sure we have a valid line
            
            isValid = True
            sectionTypes = ['DIS','LEC','RDG','LAB','SEM','PRJ','TUT','WSP','TST','FLD','PRA','STU','CLN']
            
            currentSections = []
            
            for w in sectionInfo:
                if w not in sectionTypes:
                    isValid = False
                    break
                else:
                    currentSections.append(w)
            
            if not isValid:
                continue
            
            Code = splitx[0] + "*" + splitx[1]
            Level = str(int(re.sub("[^0-9]", "", splitx[1]))/100*100) + 's'
            Num_Credits = splitx[3]
            
            if 'Code' in currentObject:
                currentObject['Description'] = Description
                Description = ""
                
                baseCode = currentObject['Code'].split("*")
                
                for sectionType in currentSections:
                    newCode = baseCode[0] + "_" + sectionType + "*" + baseCode[1]
                    print newCode
                    found = collection.find_one({'Code': newCode, 'School':'Waterloo'})
                    if found == None:
                        currentObject['Code'] = newCode
                        
                        if '_id' in currentObject:
                            del currentObject['_id']
                            
                        collection.insert_one(currentObject)
                
                currentObject = {}
            
            currentObject["School"] = "Waterloo"
            currentObject["Campus"] = "Main campus"
            currentObject['Code'] = Code
            currentObject['Num_Credits'] = Num_Credits
            currentObject['Level'] = Level
            
            onLine = 0
            
        elif x != "" and x.find('Course ID') == -1:
            onLine += 1
            
            if onLine == 1:
                currentObject['Name'] = x
                inBlock = True
            elif onLine >= 2:
                if inBlock:
                    if x.find('Offered at ') != -1:
                        place = x.find('Offered at ')
                        currentObject['Campus'] = x[place:].replace(']', '')
                        
                    elif x.find('Prereq: ') != -1:
                        currentObject['Prerequisites'] = x[len('Prereq: '):]
                    elif x.find('Antireq: ') != -1:
                        currentObject['Exclusions'] = x[len('Antireq: '):]
                    else:
                        Description += x + '\n'
        else:
            inBlock = False
    
    #get the last one
    if (currentObject != {}):
        baseCode = currentObject['Code'].split("*")
        for sectionType in currentSections:
            newCode = baseCode[0] + "_" + sectionType + "*" + baseCode[1]
            
            found = collection.find_one({'Code': newCode, 'School':'Waterloo'})
            if found == None:
                currentObject['Code'] = newCode
                
                if '_id' in currentObject:
                    del currentObject['_id']
                    
                collection.insert_one(currentObject)
        
getData()
