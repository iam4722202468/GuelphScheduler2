#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser
import json
import time
import requests

SEMESTER = 'S18'

if __name__ == '__main__':
    password_ = open("./secret","r").read().rstrip()
else:
    password_ = open("./Schools/Humber/secret","r").read().rstrip()
    
dayKey = {
    'M':'Mon',
    'T':'Tues',
    'W':'Wed',
    'R':'Thur',
    'F':'Fri'
}

postFields = {
    "username":"n01168221",
    "password":password_,
    "execution":"e1s1",
    "_eventId":"submit",
    "submit":"LOG+IN"}
    
def getSemesterCode(semester):
    if semester[0] == 'W':
        return '20' + semester[1:] + '30'
    if semester[0] == 'S':
        return '20' + semester[1:] + '50'
    if semester[0] == 'F':
        return '20' + semester[1:] + '70'

semesterCode = getSemesterCode(SEMESTER)

def getInfo(Code):
    getURL = 'https://mediastudies.humber.ca/course.html?code=' + Code.replace("*"," ")
    r = requests.get(getURL)

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
        if x['Course']['Course'] == toFind:
            return i
    return -1

getURL = postURL = 'https://login.humber.ca/cas/login?service=https%3A%2F%2Fsso.humber.ca%2Fssomanager%2Fc%2FSSB'

s = requests.session()
r = s.get(getURL)

soup = BeautifulSoup(r.text)
ltValue = soup.find("input", {"name":"lt"})['value']
postFields['lt'] = ltValue

r = s.post(postURL, data=postFields)

getURL = "https://ssomanager.humber.ca/ssomanager/c/SSB?ret_code="
r = s.get(getURL)

#https://ssb.humber.ca/PROD/bwckschd.p_disp_listcrse?term_in=201770&subj_in=ACAP&crse_in=130&crn_in=7401

postFields = {
    "p_calling_proc" : "P_CrseSearch",
    "p_term" : semesterCode
}

postURL = "https://ssb.humber.ca/PROD/bzckgens.p_proc_term_date"
r = s.post(postURL, data=postFields)

soup = BeautifulSoup(r.text)

table = soup.find('select', attrs={'name':'sel_subj'})
rows = table.findAll('option')

postFields = {
    "rsts":"dummy",
    "crn":"dummy",
    "term_in":semesterCode,
    "sel_subj":["dummy"],
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

postFields['sel_subj'].append('dummy')

#sel_crse course number

'''
for i,x in enumerate(rows):
    if i > 10:
        break
    print x['value']
    postFields['sel_subj'].append(x['value'])
'''

def getData(dataToSend):
    
    postFields['sel_subj'].append(dataToSend[0][0])
    postFields['sel_crse'] = dataToSend[0][1]
    
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
            
            ##################################
            if foundAll[10].text == "0":
                continue
            ##################################
            
            tempFound = foundAll[1].find('a')
            
            if tempFound != None:
                Code = foundAll[2].text + "*" + foundAll[3].text
                
                courseIndex = findIndex(courseObjects, Code)
                
                #getURL = 'https://ssb.humber.ca/PROD/bwckschd.p_disp_listcrse?term_in=201770&subj_in=ACAP&crse_in=130&crn_in=7401'
                getURL = 'https://ssb.humber.ca' + tempFound['href']
                pageInfo = s.get(getURL)
                
                infoSoup = BeautifulSoup(pageInfo.text)
                
                infoTable = infoSoup.find('table', attrs={'class':'datadisplaytable'})
                
                start = str(infoTable.contents[4]).find("Levels: </span>") + len("Levels: </span>")
                end = str(infoTable.contents[4]).find("<br />", start) - 1
                Level = str(infoTable.contents[4])[start:end]
                
                start = str(infoTable.contents[4]).find("<br />\n<br />\n") + len("<br />\n<br />\n")
                end = str(infoTable.contents[4]).find("<br />", start) - 1
                Campus = str(infoTable.contents[4])[start:end]
                Campus = Campus.replace("Campus Campus", "Campus")
                
                start = str(infoTable.contents[4]).find("<br />\n       ") + len("<br />\n       ")
                end = str(infoTable.contents[4]).find(" Credits", start)
                
                Num_Credits = str(infoTable.contents[4])[start:end]
                Name = foundAll[7].text
                
                Prerequisites = ""
                Exclusions = ""
                Offerings = ""
                
                a = infoTable.find('table', attrs={'class':'datadisplaytable'}).findAll("tr")[1:]
                
                if courseIndex == -1:
                    Description = getInfo(Code)['Description']
                    
                    Course['Course'] = Code
                    Course['Name'] = Name
                    Course['Description'] = Description
                    Course['Campus'] = Campus
                    Course['Prerequisites'] = Prerequisites
                    Course['Exclusions'] = Exclusions
                    Course['Offerings'] = Offerings
                    Course['Num_Credits'] = Num_Credits
                    Course['Level'] = Level
                    Course['Sections'] = []
                
                Offerings = []
                
                #hack to ignore second half of semester to fix overlaps
                startDate = ""
                
                for w in a:
                    session = w.findAll("td")
                    
                    if startDate == "":
                        startDate = session[4]
                    elif startDate != session[4]:
                        break
                    
                    if session[2].text in dayKey:
                        times = session[1].text.replace   (" ", "").split("-")
                        
                        Time_Start = convertTime(times[0])
                        Time_End = convertTime(times[1])
                        Day = dayKey[session[2].text]
                        Location  = session[3].text
                        
                        tempObject = {}
                        
                        Section_Type = session[5].text
                        
                        tempObject["Time_Start"] = Time_Start
                        tempObject["Section_Type"] = Section_Type
                        tempObject["Time_End"] = Time_End
                        tempObject["Course"] = Code
                        tempObject["Location"] = Location
                        tempObject["Day"] = Day
                        
                        Offerings.append(tempObject)
                
                Section['Offerings'] = Offerings
                Section['Course'] = Code
                Section['Meeting_Section'] = foundAll[4].text
                Section['Size'] = foundAll[10].text
                Section['Enrollment'] = foundAll[10].text
                Section['Instructors'] = "Unknown"
                Section['Instructors_Rating'] = 0
                Section['Instructors_URL'] = "NULL"
                Section['Semester'] = SEMESTER
                
                if courseIndex == -1:
                    courseObjects.append({'Course':Course})
                    courseObjects[-1]['Course']['Sections'].append(Section)
                else:
                    courseObjects[courseIndex]['Course']['Sections'].append(Section)
                    #print courseObjects[courseIndex]['Course']
                    #print "_____________"
    
    return courseObjects

if __name__ == '__main__':
    import json
    print json.dumps(getData([["GLIT","110"]]), indent=2, sort_keys=True)


'''
0   <td class="dddefault">
        <input type="checkbox" name="sel_crn" value="2647 201770" id="action_id225" />
        <label for="action_id225"><span class="fieldlabeltextinvisible">add to worksheet</span></label>
        <input type="hidden" name="assoc_term_in" value="201770" />
    </td>
    
1   <td class="dddefault">
        <a 
            href="/PROD/bwckschd.p_disp_listcrse?term_in=201770&amp;subj_in=ACCT&amp;crse_in=355&amp;crn_in=2647"
            onmouseover="window.status='Detail';  return true" onfocus="window.status='Detail';  return true" onmouseout="window.status='';  return true"
            onblur="window.status='';  return true">2647
        </a>
    </td>
    
2   <td class="dddefault">ACCT</td> code
3   <td class="dddefault">355</td> course
4   <td class="dddefault">505</td> section
5   <td class="dddefault">NO</td>
6   <td class="dddefault">3.000</td>
7   <td class="dddefault">Business Strategies</td>
8   <td class="dddefault">T</td>
9   <td class="dddefault">06:05 pm-10:05 pm</td>
10  <td class="dddefault">29</td>
11  <td class="dddefault">SEP 05-DEC 15</td>
12  <td class="dddefault">NO-F 112</td>
13  <td class="dddefault">Fee Rate Regular Business</td>
'''
