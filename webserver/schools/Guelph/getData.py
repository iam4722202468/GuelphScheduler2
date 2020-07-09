#!/usr/bin/python3

from bs4 import BeautifulSoup
from html.parser import HTMLParser
import json

from functools import reduce
import requests

from pymongo import MongoClient
client = MongoClient()

db = client['scheduler']
collection = db['cachedData']

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
        cookie[x.split('=')[0]] = "".join(x.split('=')[1:])

    return cookie

def getDescription(Code, Level):
    return collection.find_one({'Code': Code})

def findIndex(courseObject, toFind):
    for i,x in enumerate(courseObject):
        if x['Course']['Course'] == toFind:
            return i
    return -1

professorCache = {}

def fixOverlaps(courses):
    for courseNumber in range(len(courses)):
        newSections = []

        for index in range(len(courses[courseNumber]['Course']['Sections'])):
            #if there is a choice of labs then the labs will overlap perfectly

            cachedTimes = []
            conflicts = {}

            x = courses[courseNumber]['Course']['Sections'][index]

            noConflicts = {}
            newArrayOfferings = []

            for y in x['Offerings']:
                combination = y['Time_Start'] + " " + y['Day']

                if combination in cachedTimes:
                    if not combination in conflicts:
                        conflicts[combination] = []
                        conflicts[combination].append(noConflicts[combination])
                        del noConflicts[combination]

                    conflicts[combination].append(y)

                else:
                    noConflicts[combination] = y
                    cachedTimes.append(combination)

            combineArray = []

            for y in conflicts.keys():
                locationArray = []

                for z in conflicts[y]:
                    locationArray.append(z['Location'])

                if len(conflicts[y]) > 0:
                    conflicts[y][0]['Location'] = " or ".join(locationArray)
                    combineArray.append(conflicts[y][0])

            for y in noConflicts.keys():
                newArrayOfferings.append(noConflicts[y])

            tempNewArray = newArrayOfferings[:]
            tempNewArray += combineArray

            newObject = {}
            newObject['Meeting_Section'] = x['Meeting_Section']
            newObject['Enrollment'] = x['Enrollment']
            newObject['Instructors'] = x['Instructors']
            newObject['Course'] = x['Course']
            newObject['Semester'] = x['Semester']
            newObject['Instructors_Rating'] = x['Instructors_Rating']
            newObject['Instructors_URL'] = x['Instructors_URL']
            newObject['Size'] = x['Size']
            newObject['Offerings'] = tempNewArray

            newSections.append(newObject)


        courses[courseNumber]['Course']['Sections'] = newSections

    return courses

def getInstructorRating(instructors):
    urlArray = []
    ratingArray = []

    if instructors.find("TBA") > -1:
        return ["TBA", 0]

    for x in instructors.split(", "):
        if x in professorCache:
            urlArray.append(professorCache[x][0])
            ratingArray.append(professorCache[x][1])

        else:
            oldX = x
            x = "+".join(x.replace(".", "").split(" "))

            requestURL = "https://solr-aws-elb-production.ratemyprofessors.com//solr/rmp/select/?solrformat=true&rows=20&wt=json&json.wrf=noCB&callback=noCB&q=" + x + "+AND+schoolid_s:1426&defType=edismax&qf=teacherfirstname_t^2000+teacherlastname_t^2000+teacherfullname_t^2000+autosuggest&bf=pow(total_number_of_ratings_i,2.1)&sort=total_number_of_ratings_i+desc&siteName=rmp&rows=20&start=0&fl=pk_id+teacherfirstname_t+teacherlastname_t+total_number_of_ratings_i+averageratingscore_rf+schoolid_s&fq="

            response = requests.get(requestURL)
            html = response.text
            try:
                teacherObject = json.loads(html[5:-1])
                found = False

                teacherRating = float(teacherObject['response']['docs'][0]['averageratingscore_rf'])
                teacherUrl = "https://www.ratemyprofessors.com/ShowRatings.jsp?tid=" + str(teacherObject['response']['docs'][0]['pk_id'])
            except:
                teacherUrl = "NULL"
                teacherRating = 0

            urlArray.append(teacherUrl)
            ratingArray.append(teacherRating)

            professorCache[oldX] = [teacherUrl, teacherRating]

    return [' '.join(urlArray), reduce(lambda x, y: x + y, ratingArray) / len(ratingArray)]

def getData(dataToSend):

    s = requests.session()

    getURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?CONSTITUENCY=WBST&type=P&pid=ST-WESTS12A&TOKENIDX='
    r = s.get(getURL)
    cookie = getKeys(r.headers)

    getURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?CONSTITUENCY=WBST&type=P&pid=ST-WESTS12A&TOKENIDX=' + cookie['LASTTOKEN']
    r = s.get(getURL)

    try:
        cookie = getKeys(r.headers)
    except:
        return "Error: Webadvisor seems to be down"

    # 1 stores class
    # 3 stores course code

    postURL = 'https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor?TOKENIDX=' + cookie['LASTTOKEN'] + '&SS=1&APP=ST&CONSTITUENCY=WBST'
    postfields = {"VAR1":SEMESTER, "VAR10":"", "VAR11":"","VAR12":"", "VAR13":"", "VAR14":"", "VAR15":"", "VAR16":"", "DATE.VAR1":"", "DATE.VAR2":"", "LIST.VAR1_CONTROLLER":"LIST.VAR1", "LIST.VAR1_MEMBERS":"LIST.VAR1*LIST.VAR2*LIST.VAR3*LIST.VAR4", "LIST.VAR1_MAX":"5", "LIST.VAR2_MAX":"5", "LIST.VAR3_MAX":"5", "LIST.VAR4_MAX":"5", "LIST.VAR1_1":dataToSend[0][0], "LIST.VAR2_1":"", "LIST.VAR3_1":dataToSend[0][1], "LIST.VAR4_1":"", "LIST.VAR1_2":"", "LIST.VAR2_2":"", "LIST.VAR3_2":"", "LIST.VAR4_2":"", "LIST.VAR1_3":"", "LIST.VAR2_3":"", "LIST.VAR3_3":"", "LIST.VAR4_3":"", "LIST.VAR1_4":"", "LIST.VAR2_4":"", "LIST.VAR3_4":"", "LIST.VAR4_4":"", "LIST.VAR1_5":"", "LIST.VAR2_5":"", "LIST.VAR3_5":"", "LIST.VAR4_5":"", "VAR7":"", "VAR8":"", "VAR3":"", "VAR6":"", "VAR21":"", "VAR9":"", "SUBMIT_OPTIONS":""}
    
    r = s.post(postURL, data=postfields)

    soup = BeautifulSoup(r.text, features="lxml")
    f = r.text

    if f.find("No available course section(s)") > 0:
        return "Error: Course not found"

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
        Meeting_Section = title.split("*")[2].split(" ")[0]

        #don't include closed courses
        #############################################################
        if spots == '\n' or cols[2].getText() == 'Closed':
            continue
        #############################################################

        courseIndex = findIndex(courseObjects, Code)

        if courseIndex == -1:

            Name = " ".join(title.split(" ")[2:]) #backup if info is not found on course

            Level = cols[10].find('p').contents[0] #level (not really) (Undergraduate / Graduate) (Level not mentioned)

            extraInfo = getDescription(Code, Level)

            Description = extraInfo['Description']

            if 'Prerequisites' in extraInfo:
                Prerequisites = extraInfo['Prerequisites']
            else:
                Prerequisites = ""

            if 'Exclusions' in extraInfo:
                Exclusions = extraInfo['Exclusions']
            else:
                Exclusions = ""

            if 'Offerings' in extraInfo:
                Offerings = extraInfo['Offerings']
            else:
                Offerings = ""

            if len(extraInfo['Name']) > len(Name):
                Name = extraInfo['Name']

            Campus = cols[4].find('p').contents[0] #campus
            Num_Credits = cols[8].find('p').contents[0] #credits

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

        Instructors = cols[6].find('p').contents[0] #prof

        Size = spots.split(' / ')[1]
        Enrollment = spots.split(' / ')[0]

        InstructorInfo = getInstructorRating(Instructors)

        Instructors_URL = InstructorInfo[0]
        Instructors_Rating = InstructorInfo[1]

        Section['Course'] = Code
        Section['Meeting_Section'] = Meeting_Section
        Section['Size'] = Size
        Section['Enrollment'] = Enrollment
        Section['Instructors'] = Instructors
        Section['Instructors_Rating'] = Instructors_Rating
        Section['Instructors_URL'] = Instructors_URL
        Section['Semester'] = SEMESTER

        Offering = []

        Meeting_Info = cols[5].find('p').contents[0]

        if Meeting_Info.find("(more)...") != -1:
            findLink = cols[3].find('a')['onclick']

            startLink = findLink.find('\'')+1
            endLink = findLink.find('\'', startLink)

            findLink = findLink[startLink:endLink]

            getURL = "https://webadvisor.uoguelph.ca/WebAdvisor/WebAdvisor" + findLink
            r = s.get(getURL)

            getURL = getURL.replace("&CLONE=Y&CLONE_PROCESS=Y","&CLONE_PROCESS=Y")
            r = s.get(getURL)

            start = r.text.find('<p id="LIST_VAR12_1">') + 21
            end = r.text.find("</p>", start)

            Meeting_Info = r.text[start:end]

        for x in Meeting_Info.split("\n"): #meeting info
            tempObject = {}

            splitX = x.split(' ')

            if x.find('-', 11) == -1:
                continue
            
            try:
                indexOfHyphon = splitX.index('-')
                
                Section_Type = splitX[1] #session type
                Day = ' '.join(splitX[2:indexOfHyphon-1]) #days
                Location = splitX[-3] + " room " + splitX[-1] # room number
                
                startTime = splitX[indexOfHyphon-1] #start time
                endTime = splitX[indexOfHyphon+1].replace(',', '') #end time
                
                tempObject['Course'] = Code
                tempObject['Section_Type'] = Section_Type
                tempObject['Day'] = Day
                tempObject['Time_Start'] = convertTime(startTime)
                tempObject['Time_End'] = convertTime(endTime)
                tempObject['Location'] = Location
            except:
                tempObject['Course'] = Code
                tempObject['Section_Type'] = "TBA"
                tempObject['Day'] = "TBA"

            if tempObject['Section_Type'] in ["LEC","LAB","SEM"]:
                Offering.append(tempObject)

        Section['Offerings'] = Offering

        if courseIndex == -1:
            courseObjects.append({'Course':Course})
            courseObjects[-1]['Course']['Sections'].append(Section)
        else:
            courseObjects[courseIndex]['Course']['Sections'].append(Section)

    courseObjects = fixOverlaps(courseObjects)

    return courseObjects


if __name__ == '__main__':
    print(getData([["MATH","4240"]]))
