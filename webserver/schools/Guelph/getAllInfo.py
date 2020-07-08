#!/usr/bin/python3

from bs4 import BeautifulSoup
from html.parser import HTMLParser
import datetime
import json

import requests

from pymongo import MongoClient
client = MongoClient()

db = client['scheduler']
collection = db['registrationData']

#define semester
SEMESTER = 'F20'

def convertTime(x):
    if(x[-2:] == "AM"):
        return x[:2] + x[-4:-2]
    else:
        if int(x[:2]) == 12:
            return x[:2] + x[-4:-2]
        else:
            return str(int(x[:2])+12) + x[-4:-2]

def getKeys(header):
    cookie = {}
    
    keySections = header['Set-Cookie'].split(", ")
    
    for x in keySections:
        cookie[x.split('=')[0]] = x.split('=')[1]
        
    return cookie

def findIndex(courseObject, toFind):
    for i,x in enumerate(courseObject):
        if x['Code'] == toFind:
            return i
    return -1

spotsCourses = {}

def getData(VAR21):
    getURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?CONSTITUENCY=WBST&type=P&pid=ST-WESTS12A&TOKENIDX='
    r = requests.get(getURL)
    cookie = getKeys(r.headers)
    getURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?CONSTITUENCY=WBST&type=P&pid=ST-WESTS12A&TOKENIDX=' + cookie['LASTTOKEN']
    r = requests.get(getURL, cookies=cookie)
    cookie = getKeys(r.headers)
    
    # 1 stores class
    # 3 stores course code
    
    postURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?TOKENIDX=' + cookie['LASTTOKEN'] + '&SS=1&APP=ST&CONSTITUENCY=WBST'
    postfields = {"VAR1":SEMESTER, "VAR10":"", "VAR11":"","VAR12":"", "VAR13":"", "VAR14":"", "VAR15":"", "VAR16":"", "DATE.VAR1":"", "DATE.VAR2":"", "LIST.VAR1_CONTROLLER":"LIST.VAR1", "LIST.VAR1_MEMBERS":"LIST.VAR1*LIST.VAR2*LIST.VAR3*LIST.VAR4", "LIST.VAR1_MAX":"5", "LIST.VAR2_MAX":"5", "LIST.VAR3_MAX":"5", "LIST.VAR4_MAX":"5", "LIST.VAR1_1":"", "LIST.VAR2_1":"", "LIST.VAR3_1":"", "LIST.VAR4_1":"", "LIST.VAR1_2":"", "LIST.VAR2_2":"", "LIST.VAR3_2":"", "LIST.VAR4_2":"", "LIST.VAR1_3":"", "LIST.VAR2_3":"", "LIST.VAR3_3":"", "LIST.VAR4_3":"", "LIST.VAR1_4":"", "LIST.VAR2_4":"", "LIST.VAR3_4":"", "LIST.VAR4_4":"", "LIST.VAR1_5":"", "LIST.VAR2_5":"", "LIST.VAR3_5":"", "LIST.VAR4_5":"", "VAR7":"", "VAR8":"", "VAR3":"", "VAR6":"", "VAR21":VAR21, "VAR9":"", "SUBMIT_OPTIONS":""}
    
    #dataToSend = [["ENGL",""], ["ECON","3740"], ["",""], ["",""], ["",""]]
    
    #postfields = {"VAR1":SEMESTER, "VAR10":"Y", "VAR11":"Y","VAR12":"Y", "VAR13":"Y", "VAR14":"Y", "VAR15":"Y", "VAR16":"Y", "DATE.VAR1":"", "DATE.VAR2":"", "LIST.VAR1_CONTROLLER":"LIST.VAR1", "LIST.VAR1_MEMBERS":"LIST.VAR1*LIST.VAR2*LIST.VAR3*LIST.VAR4", "LIST.VAR1_MAX":"5", "LIST.VAR2_MAX":"5", "LIST.VAR3_MAX":"5", "LIST.VAR4_MAX":"5", "LIST.VAR1_1":dataToSend[0][0], "LIST.VAR2_1":"", "LIST.VAR3_1":dataToSend[0][1], "LIST.VAR4_1":"", "LIST.VAR1_2":dataToSend[1][0], "LIST.VAR2_2":"", "LIST.VAR3_2":dataToSend[1][1], "LIST.VAR4_2":"", "LIST.VAR1_3":dataToSend[2][0], "LIST.VAR2_3":"", "LIST.VAR3_3":dataToSend[2][1], "LIST.VAR4_3":"", "LIST.VAR1_4":dataToSend[3][0], "LIST.VAR2_4":"", "LIST.VAR3_4":dataToSend[3][1], "LIST.VAR4_4":"", "LIST.VAR1_5":dataToSend[4][0], "LIST.VAR2_5":"", "LIST.VAR3_5":dataToSend[4][1], "LIST.VAR4_5":"", "VAR7":"", "VAR8":"", "VAR3":"", "VAR6":"", "VAR21":"", "VAR9":"", "SUBMIT_OPTIONS":""}

    
    print("Getting data")

    r = requests.post(postURL, data=postfields, cookies=cookie)
    
    print("Data recieved")
        

    f = r.text

    soup = BeautifulSoup(f, features="lxml")
    
    table = soup.find('table', attrs={'class':'mainTable'})
    rows = table.findAll('tr')[5:]
    
    h = HTMLParser()

    courseObjects = []

    for row in rows:
        Course = {}
        Section = {}
        
        cols = row.findAll('td')
        
        title = h.unescape(cols[3].find('a').contents[0])
        
        Code = "*".join(title.split("*")[:2])
        
        spots = cols[7].find('p').contents[0] #spots

        print(Code, spots)

        if not Code in spotsCourses:
            spotsCourses[Code] = { 'Total': 0, 'Remaining': 0, 'Sections': 0 }

        if (len(spots.split(' / ')) == 2):
            spotsCourses[Code]['Remaining'] += int(spots.split(' / ')[0])
            spotsCourses[Code]['Total'] += int(spots.split(' / ')[1])
            spotsCourses[Code]['Sections'] += 1

        Meeting_Section = title.split("*")[2].split(" ")[0]
        
        #don't include closed courses
        #if spots == '\n' or cols[2].getText() == 'Closed':
        #    continue
        
        courseIndex = findIndex(courseObjects, Code)
        
        if courseIndex == -1:

            Name = " ".join(title.split(" ")[2:]) #backup if info is not found on course
            
            Level = cols[10].find('p').contents[0] #level (not really) (Undergraduate / Graduate) (Level not mentioned)
            
            Campus = cols[4].find('p').contents[0] #campus
            Num_Credits = cols[8].find('p').contents[0] #credits
            
            Course['Code'] = Code
            Course['Campus'] = Campus
            Course['Name'] = Name
            Course['Num_Credits'] = Num_Credits
            Course['Level'] = Level
            
            courseObjects.append({'Code':Code})
            
    return

getData('UG')
getData('GR')

spotsCoursesDated = []

for x in spotsCourses:
    toInsert = ({
        'Code': x,
        'Total': spotsCourses[x]['Total'],
        'Remaining': spotsCourses[x]['Remaining'],
        'Sections': spotsCourses[x]['Sections'],
        'Percent': 0 if spotsCourses[x]['Total'] == 0 else 1 - spotsCourses[x]['Remaining']/spotsCourses[x]['Total'],
        'ts': datetime.datetime.utcnow()
    })

    collection.insert_one(toInsert)
