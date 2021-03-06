#!/usr/bin/python3

from bs4 import BeautifulSoup
from html.parser import HTMLParser
from html import unescape
import json

import requests

from pymongo import MongoClient
client = MongoClient()

db = client['scheduler']
collection = db['cachedData']

#define semester
SEMESTER = 'W21'

def getKeys(header):
    """
    A function to get LASTTOKEN from the url header

    Attributes
    ----------
    header : dictionary
        a dictionary of HTTP headers
    
    Returns
    ----------
    cookie : 
        Set-Cookie header as a dictionary
    """
    cookie = {}
    
    keySections = header['Set-Cookie'].split(", ")
    
    for x in keySections:
        cookie[x.split('=')[0]] = x.split('=')[1]
        
    return cookie

def getDescription(courseInfo, silent=False):
    """
    Gets course description from WebAdvisor.
    Checks if course info present in database. If not, updates it.

    Attributes
    ----------
    courseInfo : dictionary
        of course info labels - code, level, offered etc.
    silent : boolean
        to print or not to is the question
    """

    Code = courseInfo['Code']
    Level = courseInfo['Level']

    if not silent:
        print(Code)
    
    found = collection.find_one({'Code': Code, 'School':'Guelph'})

    if found == None or 'Offered' not in found:
        if Level == "Undergraduate Guelph-Humber":
            Level = "guelphhumber"
        
        # open information about the course # TODO: only gets undergraduate courses
        infoURL = 'https://www.uoguelph.ca/registrar/calendars/' + Level.lower() + '/current/courses/' + Code.replace('*', '').lower() + '.shtml'
        
        r = requests.get(infoURL)
        soup = BeautifulSoup(r.text, features="lxml")
        
        try:
            a = soup.find("table")
            a = a.findAll('tr')
            
            #weird school formatting thing TODO: replace with regex
            Description = a[1].contents[1].getText().replace("\n                  ", " ").replace("        ", " ").replace('\n        ', '')
            
            courseInfo['Description'] = Description

            # a[0] text -> '\nCode Name_of_Course Offered Hours [Credits]\n' (hours may be absent)
            # Check if undergrad course
            if int(int(Code.split('*')[1])/1000)*100 <= 400:  # <= 400 means undergrad, has hours
              courseInfo['Offered'] = a[0].getText().split(" ")[-3].split(',')
            else:
                # breaks coop 5000
                courseInfo['Offered'] = a[0].getText().split(" ")[-2].split(',')  # 400, for 6000 level graduate courses, no hours
            
            courseInfo['Num_Credits'] = a[0].getText().split(" ")[-1][1:-2]
            
            newName = " ".join(a[0].getText().split(" ")[1:-3])  # TODO: requires -2 for graduate courses
            
            courseInfo['Name'] = newName
            
            # TODO: replace with regex
            for x in a[2:]:
                if x.find('th').contents[0] == 'Corequisite(s):':
                    courseInfo['Corequisites'] = ''.join(x.find('td').findAll(text=True)).replace('\n               ', '')
                if x.find('th').contents[0] == 'Prerequisite(s):':
                    courseInfo['Prerequisites'] = ''.join(x.find('td').findAll(text=True)).replace('\n               ', '')
                if x.find('th').contents[0] == 'Equate(s):':
                    courseInfo['Equates'] = ''.join(x.find('td').findAll(text=True)).replace('\n               ', '')
                if x.find('th').contents[0] == 'Restriction(s):':
                    courseInfo['Exclusions'] = ''.join(x.find('td').findAll(text=True)).replace('\n               ', '')
                if x.find('th').contents[0] == 'Offering(s):':
                    courseInfo['Offerings'] = ''.join(x.find('td').findAll(text=True)).replace('\n               ', '')
        except Exception as e:
            print(e)
            courseInfo['Description'] = "Description not available"
            courseInfo['Offered'] = [SEMESTER[0]]
        

        courseInfo['School'] = "Guelph"
        print(courseInfo)
        # print(courseInfo['Code'], courseInfo['Offered'])
        
        collection.replace_one({'Code': courseInfo['Code']}, courseInfo, upsert=True)
        

def fetchData():
    """
    Fetches all data from UofG WebAdvisor for the given SEMESTER
    
    Returns
    ----------
    response: the response from WebAdvisor
    """

    getURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?CONSTITUENCY=WBST&type=P&pid=ST-WESTS12A&TOKENIDX='
    r = requests.get(getURL)
    cookie = getKeys(r.headers)  # gets Set-Cookie header dictionary
    getURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?CONSTITUENCY=WBST&type=P&pid=ST-WESTS12A&TOKENIDX=' + cookie['LASTTOKEN']
    r = requests.get(getURL, cookies=cookie)
    cookie = getKeys(r.headers)
    
    # 1 stores class
    # 3 stores course code
    
    postURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?TOKENIDX=' + cookie['LASTTOKEN'] + '&SS=1&APP=ST&CONSTITUENCY=WBST'
    
    # dictionary of fields available on WebAdvisor -> {"HTML_element_#id": value}
    postfields = {"VAR1":SEMESTER, "VAR10":"", "VAR11":"","VAR12":"", "VAR13":"", "VAR14":"", "VAR15":"", "VAR16":"", "DATE.VAR1":"", "DATE.VAR2":"", "LIST.VAR1_CONTROLLER":"LIST.VAR1", "LIST.VAR1_MEMBERS":"LIST.VAR1*LIST.VAR2*LIST.VAR3*LIST.VAR4", "LIST.VAR1_MAX":"5", "LIST.VAR2_MAX":"5", "LIST.VAR3_MAX":"5", "LIST.VAR4_MAX":"5", "LIST.VAR1_1":"", "LIST.VAR2_1":"", "LIST.VAR3_1":"", "LIST.VAR4_1":"", "LIST.VAR1_2":"", "LIST.VAR2_2":"", "LIST.VAR3_2":"", "LIST.VAR4_2":"", "LIST.VAR1_3":"", "LIST.VAR2_3":"", "LIST.VAR3_3":"", "LIST.VAR4_3":"", "LIST.VAR1_4":"", "LIST.VAR2_4":"", "LIST.VAR3_4":"", "LIST.VAR4_4":"", "LIST.VAR1_5":"", "LIST.VAR2_5":"", "LIST.VAR3_5":"", "LIST.VAR4_5":"", "VAR7":"", "VAR8":"", "VAR3":"", "VAR6":"", "VAR21":"UG", "VAR9":"", "SUBMIT_OPTIONS":""}
    
    #dataToSend = [["ENGL",""], ["CIS",""], ["",""], ["",""], ["",""]]
    
    #postfields = {"VAR1":SEMESTER, "VAR10":"Y", "VAR11":"Y","VAR12":"Y", "VAR13":"Y", "VAR14":"Y", "VAR15":"Y", "VAR16":"Y", "DATE.VAR1":"", "DATE.VAR2":"", "LIST.VAR1_CONTROLLER":"LIST.VAR1", "LIST.VAR1_MEMBERS":"LIST.VAR1*LIST.VAR2*LIST.VAR3*LIST.VAR4", "LIST.VAR1_MAX":"5", "LIST.VAR2_MAX":"5", "LIST.VAR3_MAX":"5", "LIST.VAR4_MAX":"5", "LIST.VAR1_1":dataToSend[0][0], "LIST.VAR2_1":"", "LIST.VAR3_1":dataToSend[0][1], "LIST.VAR4_1":"", "LIST.VAR1_2":dataToSend[1][0], "LIST.VAR2_2":"", "LIST.VAR3_2":dataToSend[1][1], "LIST.VAR4_2":"", "LIST.VAR1_3":dataToSend[2][0], "LIST.VAR2_3":"", "LIST.VAR3_3":dataToSend[2][1], "LIST.VAR4_3":"", "LIST.VAR1_4":dataToSend[3][0], "LIST.VAR2_4":"", "LIST.VAR3_4":dataToSend[3][1], "LIST.VAR4_4":"", "LIST.VAR1_5":dataToSend[4][0], "LIST.VAR2_5":"", "LIST.VAR3_5":dataToSend[4][1], "LIST.VAR4_5":"", "VAR7":"", "VAR8":"", "VAR3":"", "VAR6":"", "VAR21":"", "VAR9":"", "SUBMIT_OPTIONS":""}

    print("Getting data for ", SEMESTER)
    r = requests.post(postURL, data=postfields, cookies=cookie)

    if r.ok:
        print("Data recieved")
        return r.text
    else:
        print('Error getting data, received ', r)
        return None

def getData(text):
    """
    Parse all data from UofG WebAdvisor.
    Calls getDescription to get description and update info.

    Attributes
    ----------
    text : string
        of html text
    """
    
    if text is None:
        return
    else:        
        soup = BeautifulSoup(text, 'lxml')

        table = soup.find('table', attrs={'class':'mainTable'})

        # first 5 tr to be skipped as they are either empty, need to be traversed further or of non interest region
        # TODO: remove dependence on static number
        rows = table.findAll('tr')[5:]  

        courseObjects = set()

        for row in rows:
            # 10 columns: 0, 9 th column empty / hidden
            
            Course = {}
            
            cols = row.findAll('td')

            # col 3: Section Name and Title
            #   'a' is the link leading to Section Information / Course Information
            # get the full content e.g.: ACCT*1220*0101 (4675) Intro Financial Accounting 
            title = unescape(cols[3].find('a').contents[0])
            
            # split by * and join by *, keeping only code
            # e.g.: ACCT*1220
            Code = "*".join(title.split("*")[:2])

            # col 7: Available / Capacity
            spots = cols[7].find('p').contents[0] #spots
            # class section: 0101 in ACCT*1220*0101
            Meeting_Section = title.split("*")[2].split(" ")[0]
            
            #don't include closed courses
            #if spots == '\n' or cols[2].getText() == 'Closed':
            #    continue
            
            if Code not in courseObjects:
                # string literal name of the course
                Name = " ".join(title.split(" ")[2:]) #backup if info is not found on course
                # col 10: Academic Level
                Level = cols[10].find('p').contents[0] #level (not really) (Undergraduate / Graduate) (Level not mentioned)
                # col 4: Location
                Campus = cols[4].find('p').contents[0] #campus
                # col 8: Credits
                Num_Credits = cols[8].find('p').contents[0] #credits
                
                Course['Code'] = Code  # ACCT*1220
                Course['Campus'] = Campus  # Guelph
                Course['Name'] = Name  # Intro Financial Accounting
                Course['Num_Credits'] = Num_Credits  # 0.50
                Course['Level'] = Level  # Undergraduate 
                
                getDescription(Course)

    return

if __name__ == '__main__':
    text = fetchData()
    getData(text)
