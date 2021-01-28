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
scheduleOverrides = {'MATH*1080': 'F29'}

def checkValid(group, selectSet):
    count = []

    if isinstance(group, str):
        if group in selectSet:
            count.append(group)

    elif isinstance(group, list):
        for x in group:
            count += checkValid(x, selectSet)
    elif isinstance(group, object) and group['type'] in ['AND', 'CHOOSE']:
        found = checkValid(group['groups'], selectSet)

        if group['type'] == 'AND':
            if len(found) == len(group['groups']):
                count = found
        elif group['type'] == 'CHOOSE':
            if len(found) >= group['count']:
                count = found

    return count


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
                printRecursive(code, data[x], data, neededChoices, selectSet, res)
            elif x['type'] == 'AND' or x['type'] == 'CHOOSE':
                printRecursive(code, x, data, neededChoices, selectSet, res)

    else:
        if group['type'] == 'AND':
            printRecursive(code, group['groups'], data, neededChoices, selectSet, res)
        elif group['type'] == 'CHOOSE':
            validCount = []
            for x in group['groups']:
                validCount += checkValid(x, selectSet)

            if code not in neededChoices:
                neededChoices[code] = []

            if len(validCount) == 0:
                neededChoices[code].append(group)
            else:
                res[code] = res[code].union(validCount)

    
if __name__ == '__main__':
    selectSet = set(json.loads(input()))
    alreadyTaken = set(json.loads(input()))

    # selectSet = set(['CIS*3760', 'CIS*1910', 'STAT*2040', 'ACCT*3340', 'ACCT*2220', 'ECON*2770', 'AGR*2350', 'NUTR*4040'])
    # alreadyTaken = set(['MATH*1080', 'BIOL*1030'])

    combinedSet = selectSet.union(alreadyTaken)

    res = {}
    neededChoices = {}

    for x in list(combinedSet):
        printRecursive(x, data['prerequisites'][x], data['prerequisites'], neededChoices, combinedSet, res)

    print(res)
    print(neededChoices)
