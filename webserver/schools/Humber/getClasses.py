#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser
import json
import requests
from time import sleep

from pymongo import MongoClient
client = MongoClient()

db = client['scheduler']
collection = db['cachedData']

SEMESTER = 'S18'
password_ = open("secret","r").read().rstrip()

dayKey = {
    'M':'Mon',
    'T':'Tues',
    'W':'Wed',
    'R':'Thur',
    'F':'Fri'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'
}

def getSemesterCode(semester):
    if semester[0] == 'W':
        return '20' + semester[1:] + '30'
    if semester[0] == 'S':
        return '20' + semester[1:] + '50'
    if semester[0] == 'F':
        return '20' + semester[1:] + '70'

semesterCode = getSemesterCode(SEMESTER)

def getInfo(Code):
    
    getURL = 'https://mediastudies.humber.ca/course.html?code=' + Code.replace("*","%20")
    r = requests.get(getURL, headers=headers)
    
    text = r.text
    
    returnObject = {}
    begin = text.find("<h1>")
    end = text.find("</h1>", begin)

    returnObject['Name'] = text[begin+4:end]

    begin = text.find("<p>", end)
    begin = text.find("<p>", begin+1)
    begin = text.find("<p>", begin+1)
    end = text.find("</p>", begin)

    returnObject['Description'] = text[begin+3:end]
    
    return returnObject

def convertTime(x):
    if len(x) == 6:
        x = "0" + x
    
    if (x[-2:] == "am"):
		return x[:2] + x[-4:-2]
    else:
		if int(x[:2]) == 12:
			return x[:2] + x[-4:-2]
		else:
			return str(int(x[:2])+12) + x[-4:-2]

def findIndex(courseObject, toFind):
    for i,x in enumerate(courseObject):
        if x['Code'] == toFind:
            return i
    return -1

#https://ssb.humber.ca/PROD/bwckschd.p_disp_listcrse?term_in=201770&subj_in=ACAP&crse_in=130&crn_in=7401

postFieldsSemester = {
    "p_calling_proc" : "P_CrseSearch",
    "p_term" : semesterCode
}

postFieldsLogin = {
    "username":"n01168221",
    "password":password_,
    "execution":"e1s1",
    "_eventId":"submit",
    "submit":"LOG+IN"
}
    
postFieldsSend = {
    "rsts":"dummy",
    "crn":"dummy",
    "term_in":semesterCode,
    "sel_subj":[],
    'sel_day':"dummy",
    'sel_schd':["dummy","%"],
    'sel_insm':"dummy",
    'sel_camp':["dummy","%"],
    'sel_levl':["dummy","%"],
    'sel_sess':"dummy",
    'sel_instr':"dummy",
    'sel_ptrm':"dummy",
    'sel_attr':["dummy","%"],
    'sel_crse':"",
    'sel_title':"",
    'sel_from_cred':"",
    'sel_to_cred':"",
    'begin_hh':"0",
    'begin_mi':"0",
    'begin_ap':"a",
    'end_hh':"0",
    'end_mi':"0",
    'end_ap':"a",
    'SUB_BTN':"Section+Search",
    'path':"1"
}

def getData():
    print "Logging In"
    
    getURL = postURL = 'https://login.humber.ca/cas/login?service=https%3A%2F%2Fsso.humber.ca%2Fssomanager%2Fc%2FSSB'
    
    s = requests.session()
    r = s.get(getURL)

    soup = BeautifulSoup(r.text)
    ltValue = soup.find("input", {"name":"lt"})['value']
    postFieldsLogin['lt'] = ltValue
    
    r = s.post(postURL, data=postFieldsLogin)
    
    print "Login Successful"
    
    print "Getting Data"
    getURL = "https://ssomanager.humber.ca/ssomanager/c/SSB?ret_code="
    r = s.get(getURL)
    
    postFields = postFieldsSemester
    
    postURL = "https://ssb.humber.ca/PROD/bzckgens.p_proc_term_date"
    r = s.post(postURL, data=postFields)

    soup = BeautifulSoup(r.text)

    table = soup.find('select', attrs={'name':'sel_subj'})
    rows = table.findAll('option')
    
    postFields = postFieldsSend
    postFields['sel_subj'].append('dummy')
    
    for i,x in enumerate(rows):
        #if i > 1:
        #    break
        postFields['sel_subj'].append(x['value'])
    
    postURL = "https://ssb.humber.ca/PROD/bzskfcls.P_GetCrse_Advanced"
    
    r = s.post(postURL, data=postFields)
    soup = BeautifulSoup(r.text)
    
    table = soup.find('table', attrs={'class':'datadisplaytable'})
    rows = table.findAll('tr')
    
    courseObjects = []
    
    for x in rows:
        foundAll = x.findAll('td')
        
        if len(foundAll) > 1:
            
            Course = {}
            Section = {}
            
            tempFound = foundAll[1].find('a')
            
            if foundAll[8].text != "TBA" and tempFound != None:
                Code = foundAll[2].text + "*" + foundAll[3].text
                
                courseIndex = findIndex(courseObjects, Code)
                
                found = collection.find_one({'Code': Code, 'School':'Humber'})
                
                if courseIndex == -1 and found == None:
                    print Code
                    
                    getURL = 'https://ssb.humber.ca' + tempFound['href']
                    pageInfo = s.get(getURL)
                    
                    infoSoup = BeautifulSoup(pageInfo.text)
                    
                    infoTable = infoSoup.find('table', attrs={'class':'datadisplaytable'})
                    a = infoTable.find('table', attrs={'class':'datadisplaytable'}).findAll("tr")[1:]
                    
                    Prerequisites = ""
                    Exclusions = ""
                    Offerings = ""
                
                    start = str(infoTable.contents[4]).find("Levels: </span>") + len("Levels: </span>")
                    end = str(infoTable.contents[4]).find("<br />", start) - 1
                    Level = str(infoTable.contents[4])[start:end-1]
                    
                    start = str(infoTable.contents[4]).find("<br />\n<br />\n") + len("<br />\n<br />\n")
                    end = str(infoTable.contents[4]).find("<br />", start) - 1
                    Campus = str(infoTable.contents[4])[start:end]
                    
                    start = str(infoTable.contents[4]).find("<br />\n       ") + len("<br />\n       ")
                    end = str(infoTable.contents[4]).find(" Credits", start)
                    
                    Num_Credits = str(infoTable.contents[4])[start:end]
                    Name = foundAll[7].text
                    
                    Description = getInfo(Code)['Description']
                    
                    Campus = Campus.replace("Campus Campus", "Campus")
                    
                    Course['Code'] = Code
                    Course['Name'] = Name
                    Course['Description'] = Description
                    Course['Campus'] = Campus
                    Course['Prerequisites'] = Prerequisites
                    Course['Exclusions'] = Exclusions
                    Course['Offerings'] = Offerings
                    Course['Num_Credits'] = Num_Credits
                    Course['Level'] = Level
                    
                    Course['School'] = "Humber"
                    
                    collection.insert_one(Course).inserted_id
                    
                    courseObjects.append({'Code':Code})

getData()
