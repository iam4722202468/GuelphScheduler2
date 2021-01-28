import json

from pymongo import MongoClient
import itertools

client = MongoClient()

db = client['scheduler']
collection = db['cachedData']

path = './parsed/all.json'

with open(path, "r") as read_file:
    data = json.load(read_file)

dependsObj = {}
scheduleOverrides = {'MATH*1080': 'F29'}

def reduceChoices(groups):
    if isinstance(groups, str):
        return [groups]

    if isinstance(groups, list):
        reduced = []
        for x in groups:
            reduced.append(reduceChoices(x))

        return reduced

    if isinstance(groups, object):
        if groups['type'] == 'AND':
            reduced = []
            for x in groups['groups']:
                reduced += reduceChoices(x)

            return reduced

        if groups['type'] == 'CHOOSE':
            reduced = []

            for x in groups['groups']:
                reduced += reduceChoices(x)

            return list(itertools.combinations(reduced, groups['count']))

        

    print(groups)

def printGroup(code, group, data, neededChoices, selectSet):
    if group['type'] == 'AND':
        for x in group['groups']:
            print(group)
            printRecursive(code, x, data, neededChoices, selectSet)

    if group['type'] == 'CHOOSE':
        using = []

        reduced = reduceChoices(group['groups'])

        print('ONE OF')
        print(group)

        for x in reduced:
            diff = set(x) - selectSet

            if len(diff) == 0:
                print('Choose', using)
                return

        print('Select', reduced)
        neededChoices[code] = reduced


def printRecursive(code, group, data, neededChoices, selectSet):
    if isinstance(group, str):
        selectSet.add(group)
        print('Added', group)

        if code not in dependsObj:
            dependsObj[code] = set()

        if group not in dependsObj:
            dependsObj[group] = set()
    
        dependsObj[code].add(group)

        print('New dependency:', code, '->', group)

        printRecursive(group, data[group], data, neededChoices, selectSet)
    else:
        if not isinstance(group, list):
            printGroup(code, group, data, neededChoices, selectSet)
        else:
            for y in group:
                printGroup(code, y, data, neededChoices, selectSet)
    
def getPrerequisites(code, data, neededChoices, selectSet):
    printRecursive(None, code, data, neededChoices, selectSet)

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

def fixNeededChoices(needed, selected, alreadyTaken):
    toRemove = []
    print(selected)

    print(needed)

    for x in needed:
        for y in needed[x]:
            diff = set(y) - selected - alreadyTaken
            if len(diff) == 0:
                toRemove.append(x)
                break

    for x in toRemove:
        del needed[x]


if __name__ == '__main__':
    neededChoices = {}
    selectSet = set(['CIS*3750', 'CIS*1910', 'STAT*2040', 'ACCT*3340', 'ACCT*2220', 'ECON*2770', 'BIOL*1030'])
    alreadyTaken = set(['MATH*1080'])

    print('Running on', 'CIS*4510 and ECON*4640')
    print('Courses for choices', selectSet)
    print()
    
    for x in list(selectSet):
        getPrerequisites(x, data['prerequisites'], neededChoices, selectSet)

    getPrerequisites('CIS*4150', data['prerequisites'], neededChoices, selectSet)
    getPrerequisites('ECON*4640', data['prerequisites'], neededChoices, selectSet)
    getPrerequisites('ACCT*4220', data['prerequisites'], neededChoices, selectSet)
    getPrerequisites('AGR*2350', data['prerequisites'], neededChoices, selectSet)

    fixNeededChoices(neededChoices, selectSet, alreadyTaken)

    if len(neededChoices) > 0:
        print()
        print('Need selection before continuing', neededChoices)
        exit()

    print()
    print('Choices needed', neededChoices)
    print()
    print('Dependency generation complete')
    print()
    print('Needed courses:', selectSet)
    print()
    print('Dependencies:', dependsObj)

    extraData = {}

    for code in selectSet:
        found = collection.find_one({'School': 'Guelph', 'Code': code})
        extraData[code] = found['Offered']

    del dependsObj[None]
    assignments = createGroups(dependsObj, extraData, scheduleOverrides, alreadyTaken)
    print()
    print('Result:', assignments)

    
