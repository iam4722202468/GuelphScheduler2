import json

from pymongo import MongoClient
import itertools
import pprint

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
        res[code] = set()

    if isinstance(group, str):
        res[code].add(code)
        printRecursive(code, data[code], data, neededChoices, selectSet, res)

    elif isinstance(group, list):
        for x in group:
            if isinstance(x, str):
                res[code].add(x)
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
                neededChoices[code].append(group)
            else:
              # printRecursive(code, group['groups'], data, neededChoices, selectSet, res)
              res[code] = res[code].union(resCourses)

def createGroups(sets, extraData, scheduleOverrides, alreadyTaken):
    semesters = ['W', 'S', 'F']
    currentYear = 21
    currentSemester = 2

    assignments = {}

    for x in alreadyTaken:
        if x in sets:
            del sets[x]

        for y in sets:
            if x in sets[y]:
                sets[y].remove(x)

    while len(sets) > 0:
        semesterCode = semesters[currentSemester] + str(currentYear)
        assignments[semesterCode] = []
        markRemoval = []

        for x in sets:
            if len(sets[x]) == 0:
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

                if semesters[currentSemester] in possibleSemesters and not barrier:
                    assignments[semesterCode].append(x)
                    markRemoval.append(x)

        for x in markRemoval:
            del sets[x]

            for y in sets:
                if x in sets[y]:
                    sets[y].remove(x)

        currentSemester += 1
        if currentSemester > 2:
            currentSemester = 0
            currentYear += 1

    return assignments
    
if __name__ == '__main__':
    selectSet = set(json.loads(input()))
    alreadyTaken = set(json.loads(input()))
    scheduleOverrides = {}

    # selectSet = set(['ECON*4640', 'STAT*2040'])
    # alreadyTaken = set([])

    combinedSet = selectSet.union(alreadyTaken)

    res = {}
    neededChoices = {}
    extraData = {}

    for x in list(combinedSet):
        printRecursive(x, data['prerequisites'][x], data['prerequisites'], neededChoices, combinedSet, res)

    for code in combinedSet:
        found = collection.find_one({'School': 'Guelph', 'Code': code})
        extraData[code] = found['Offered']

    # print(res)
    # print(neededChoices)
    scheduled = createGroups(res, extraData, scheduleOverrides, alreadyTaken)

    print(json.dumps([list((combinedSet - alreadyTaken).union(selectSet)), neededChoices, scheduled]))
