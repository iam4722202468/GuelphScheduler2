#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser
import json
import time
import requests

from pymongo import MongoClient
client = MongoClient()

db = client['scheduler']
collection = db['cachedData']

SEMESTER = '1181'

def convertTime(x):
    splitx = x.replace(":","").split("-")
    
    if int(splitx[0]) < 830:
        splitx[0] = str(int(splitx[0]) + 1200)
    if int(splitx[1]) < 830:
        splitx[1] = str(int(splitx[1]) + 1200)
    
    return splitx[0], splitx[1]
    

'''

[
0    <td align="center">5701 </td>, 
1    <td align="center">LEC 001 </td>, 
2    <td align="center">UW    U         </td>, 
3    <td align="center">1 </td>, 
4    <td>&nbsp;</td>, 
5    <td>&nbsp;</td>, 
6    <td align="center">80  </td>, 
7    <td align="center">44  </td>, 
8    <td align="center">0   </td>, 
9    <td align="center">0   </td>, 
10   <td align="center">09:30-10:20MWF</td>, 
11   <td align="center">RCH   105</td>, 
12   <td align="center">Schonlau,Matthias             </td>
]

0 - section
1 - type
2 - campus
3 - unimportant
4 - unimportant
5 - unimportant
6 - positions
7 - filled positions
8 - unimportant
9 - unimportant
10 - times
11 - room
12 - instructor
'''

'''
    "Course":"GLIT*110",
    "Enrollment":"1",
    "Instructors":"Unknown",
    "Instructors_Rating":0,
    "Instructors_URL":"NULL",
    "Meeting_Section":"GBC",
    "Offerings":[
        {
            "Course":"GLIT*110",
            "Day":"Wed",
            "Location":"North - Building J 138",
            "Section_Type":"Classroom Instruction",
            "Time_End":"1040",
            "Time_Start":"0855"
        },
        {
            "Course":"GLIT*110",
            "Day":"Fri",
            "Location":"North - Building J 138",
            "Section_Type":"Classroom Instruction",
            "Time_End":"1040",
            "Time_Start":"0855"
        }
    ],
    "Semester":"S18",
    "Size":"1"
'''

def convertDay(days):
    dayArray = []
    
    if days.find('Th') != -1:
        dayArray.append('Thur')
        days.replace('Th','')
    if days.find('T') != -1:
        dayArray.append('Tues')
        days.replace('T','')
    if days.find('M') != -1:
        dayArray.append('Mon')
        days.replace('M','')
    if days.find('W') != -1:
        dayArray.append('Wed')
        days.replace('W','')
    if days.find('F') != -1:
        dayArray.append('Fri')
        days.replace('F','')
    
    return dayArray

def getInfo(Code):
    found = collection.find_one({'Code': Code, 'School':'Waterloo'})
    return found

def generateSection(allData, sectionType, Code):
    #sectionTypes = ['DIS','LEC','RDG','LAB','SEM','PRJ','TUT','WSP','TST','FLD','PRA','STU','CLN']
    #days = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri']
    
    courseBase = getInfo(Code)
    if courseBase == None:
        return []
    
    del courseBase['_id']
    
    collectedSections = []
    
    for x in allData:
        sections = x.findAll('td')
        
        if len(sections) <= 7 or sections[0].text == "&nbsp;":
            continue
        
        if sections[1].text.split(" ")[0] == sectionType:
            thisObject = {}
            
            thisObject['Course'] = Code
            thisObject['Enrollment'] = sections[7].text
            thisObject['Size'] = sections[8].text
            thisObject['Instructors'] = sections[12].text
            thisObject['Meeting_Section'] = sections[0].text
            thisObject['Instructors_Rating'] = "0"
            thisObject['Instructors_URL'] = "NULL"
            thisObject['Semester'] = SEMESTER
            thisObject['Offerings'] = []
            
            times = sections[10].text[:11]
            days = sections[10].text[11:]
            
            if times.find("TBA") != -1 or days.find("TBA") != -1:
                continue
            
            dayArray = convertDay(days)
            StartTime, EndTime = convertTime(times)
            
            for day in dayArray:
                thisOffering = {}
                thisOffering['Course'] = Code
                thisOffering['Location'] = sections[11].text
                thisOffering['Section_Type'] = sectionType
                thisOffering['Time_End'] = EndTime
                thisOffering['Time_Start'] = StartTime
                thisOffering['Day'] = day
                thisObject['Offerings'].append(thisOffering)
            
            collectedSections.append(thisObject)
    
    courseBase['Sections'] = collectedSections
    
    return {"Course":courseBase}

def getData(dataToSend):
    sectionType = dataToSend[0][0].split("_")[1]
    dataToSend[0][0] = dataToSend[0][0].split("_")[0]
    
    Code = dataToSend[0][0] + "*" + dataToSend[0][1]
    
    getURL = "http://www.adm.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?level=under&sess=" + SEMESTER + "&subject=" + dataToSend[0][0] + "&cournum=" + dataToSend[0][1]
    
    r = requests.get(getURL)
    
    if r.text.find("no matches") != -1:
        return []
    
    soup = BeautifulSoup(r.text)
    
    table = soup.find('table', attrs={'border':2})
    rows = table.findAll('tr')
    
    justFound = False
    courseObjects = []
    
    for x in rows:
        foundAll = x.findAll('td')
        if len(foundAll) == 4: #inside title
            justFound = True
            Code = foundAll[0].text + "_" + sectionType + "*" + foundAll[1].text
        elif justFound and len(foundAll) > 1:
            justFound = False
            courseObjects.append(generateSection(foundAll[1].findAll('tr'), sectionType, Code))
    
    return courseObjects

if __name__ == '__main__':
    import json
    print json.dumps(getData([["AE_LEC","224"]]), indent=2, sort_keys=True)
