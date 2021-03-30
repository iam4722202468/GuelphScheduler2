import json

from pymongo import MongoClient
import itertools
import pprint
import copy

client = MongoClient()

db = client['scheduler']
collection = db['cachedData']

path = './parsed/all.json'

with open(path, "r") as read_file:
    data = json.load(read_file)

dependsObj = {}

def checkValid(group, selectSet):
    count = 0
    resDep = []

    if isinstance(group, str):
        if group in selectSet:
            resDep.append(group)
            count += 1

    elif isinstance(group, list):
        for x in group:
            res = checkValid(x, selectSet)
            count += res[0]
            resDep += res[1]
    elif isinstance(group, object) and group['type'] in ['AND', 'CHOOSE']:
        res = checkValid(group['groups'], selectSet)
        sum = res[0]

        # print('Sum for group',group)

        if group['type'] == 'AND':
            # print('Needs', len(group['groups']), 'Has', sum)
            if sum == len(group['groups']):
                count = 1
                resDep = res[1]
        elif group['type'] == 'CHOOSE':
            # print('Needs', group['count'], 'Has', sum)
            if sum >= group['count']:
                count = 1
                resDep = res[1]

    return [count, resDep]


def printRecursive(code, group, data, neededChoices, selectSet, res):
    if code not in res:
        res[code] = []

    if isinstance(group, str):
        res[code].append(code)
        printRecursive(code, data[code], data, neededChoices, selectSet, res)

    elif isinstance(group, list):
        for x in group:
            if isinstance(x, str):
                res[code].append(x)
                selectSet.add(x)
                # print('Adding', x, 'for', code)
                printRecursive(x, data[x], data, neededChoices, selectSet, res)
            elif x['type'] == 'AND' or x['type'] == 'CHOOSE':
                printRecursive(code, x, data, neededChoices, selectSet, res)

    else:
        if group['type'] == 'AND':
            printRecursive(code, group['groups'], data, neededChoices, selectSet, res)
        elif group['type'] == 'CHOOSE':
            res2 = checkValid(group, selectSet)
            isValid = res2[0]
            resCourses = res2[1]

            # print('Checkvalid for', code, isValid)
            # print()
            # print(group)

            if code not in neededChoices:
                neededChoices[code] = []

            if isValid == 0:
                if group not in neededChoices[code]:
                    neededChoices[code].append(group)
            else:
              # printRecursive(code, group['groups'], data, neededChoices, selectSet, res)

              newObj = {'courses': resCourses, 'count': group['count']}
              res[code].append(newObj)

def canAssign(data, assigned):
    validCount = 0
    courses = set()

    for val in data:
        if isinstance(val, str):
            if val in assigned:
                validCount += 1
                courses.add(val)
        else:
            newCourses, count = canAssign(val['courses'], assigned)
            if count >= val['count']:
                validCount += 1
                courses = courses.union(newCourses)
                
    
    return courses, validCount


def convertMapping(mapping):
    newMapping = {}

    for x in mapping:
        newMapping[x] = list(mapping[x])

    return newMapping


def createGroups(sets, ordering, extraData, scheduleOverrides, alreadyTaken, semesterLimit):
    semesters = ['W', 'S', 'F']
    currentYear = 21
    currentSemester = 2

    assignments = {}
    assigned = set(alreadyTaken)

    courseMapping = {}

    while len(assigned) != len(ordering) + len(alreadyTaken):
        semesterCode = semesters[currentSemester] + str(currentYear)
        assignments[semesterCode] = []
        toAdd = set()

        for x in ordering:
            courses, count = canAssign(sets[x], assigned)

            if x not in assigned and count == len(sets[x]):
                possibleSemesters = extraData[x]

                barrierSemester = currentSemester
                barrierYear = currentYear

                if x in scheduleOverrides:
                    barrierSemester = semesters.index(scheduleOverrides[x][0])
                    barrierYear = int(scheduleOverrides[x][1:])

                barrier = False

                if barrierYear > currentYear:
                    barrier = True

                if barrierYear == currentYear and barrierSemester < currentSemester:
                    barrier = True

                if len(assignments[semesterCode]) >= semesterLimit:
                    barrier = True

                allUnknownSemesters = len(set(['F','W','S']) - set(possibleSemesters)) == 3

                if (semesters[currentSemester] in possibleSemesters or allUnknownSemesters) and not barrier:
                    assignments[semesterCode].append(x)
                    toAdd.add(x)
                    courseMapping[x] = courses

        assigned = assigned.union(toAdd)

        currentSemester += 1
        if currentSemester > 2:
            currentSemester = 0
            currentYear += 1

    return courseMapping, assignments

def lookupContains(curr, code):
    contains = False

    for x in curr:
        if isinstance(x, str):
            if x == code:
                contains = True
        else:
            contains = contains or lookupContains(x['courses'], code)

    return contains
    

# returns the number of course a single course is required by
def reverseReqLookup(sets, code):
    count = 0

    for x in sets:
        if lookupContains(sets[x], code):
            count += reverseReqLookup(sets, x)
            count += 1

    return count


# sort based on how many course a course is required by
def getSortedReqs(sets, taken):
    res = []
    for x in sets:
        count = reverseReqLookup(sets, x)
        res.append({'count':count, 'code':x})

    res.sort(key=lambda x: x['count'], reverse=True)

    resFix = []

    for x in res:
        if x['code'] not in taken:
            resFix.append(x['code'])

    return resFix


if __name__ == '__main__':
    selectSet = set(json.loads(input()))
    alreadyTaken = set(json.loads(input()))
    semesterLimit = int(input())

    scheduleOverrides = {}

    #selectSet = set(["CIS*1910", "MATH*1200", "MATH*2000", "ECON*1050", "CIS*4780", "CIS*4520", "CIS*3150", "CIS*2750", "CIS*2030", "CIS*3110", "MATH*2210", "CIS*4650", "MATH*3160", "MATH*2200", "CIS*3090", "MATH*1160", "CIS*2520", "SPAN*1100", "CIS*2430", "PHIL*2110", "CIS*3760", "CIS*3120", "MATH*2130", "CIS*2910", "CIS*3210", "STAT*2040", "CIS*3490", "CIS*3750", "CIS*4010", "CIS*2500", "MATH*1080", "MATH*1210", "CIS*1300", "PHIL*1050"])
    #alreadyTaken = set()
    #semesterLimit = 5

    combinedSet = selectSet.union(alreadyTaken)

    res = {}
    neededChoices = {}
    extraData = {}

    for x in list(combinedSet):
        printRecursive(x, data['prerequisites'][x], data['prerequisites'], neededChoices, combinedSet, res)

    for code in combinedSet:
        found = collection.find_one({'School': 'Guelph', 'Code': code})
        extraData[code] = found['Offered']

    #print(res)
    #print(neededChoices)

    courseMapping, scheduled = createGroups(res, getSortedReqs(res, alreadyTaken), extraData, scheduleOverrides, alreadyTaken, semesterLimit)

    print(json.dumps([list((combinedSet - alreadyTaken).union(selectSet)), neededChoices, scheduled, convertMapping(courseMapping)]))
