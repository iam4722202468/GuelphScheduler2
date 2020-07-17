import re
import itertools
import json

from pymongo import MongoClient
client = MongoClient()

import sys
sys.path.insert(0,'../webserver/schools/Guelph')

import getClasses

db = client['scheduler']
collection = db['cachedData']

lookedup = {}

preFixes = {
    'CHEM*1040': '1 of 4U Chemistry, equivalent, CHEM*1060',
    'ENGG*3150': '4.00 ENGG credits, ENGG*1210',
    'ECON*4400': 'ECON*2310, 12.0 credits',
    'CHEM*2060': 'CHEM*1050, MATH*1210, (1 of PHYS*1010, PHYS*1070, PHYS*1300)',
    'CHEM*7940': 'CHEM*7840',
    'CHEM*7840': 'CHEM*7940',
    'MGMT*4000': 'MGMT*3320, [ECON*3460, ECON*3560, (1 of ECON*2560 or FIN*2000)], (1 of FARE*3310, HTM*3120, REAL*3890)',
    'MGMT*6500': 'MGMT*6100, MGMT*6200',
    'ENVS*3290': '1 of ENVS*2080, ENVS*2320, [MBG*2040, (BIOL*2060 or MICR*2420)]',
    'ECON*2740': 'ECON*1100, (ECON*1050 or FARE*1040), (1 of MATH*1000, MATH*1030, MATH*1050, MATH*1080, MATH*1200)',
    'SPAN*3800': '(HISP*3220 or SPAN*3220), (HISP*3230 or SPAN*3230), SPAN*3080',
    'SPAN*3810': '(HISP*3220 or SPAN*3220), (HISP*3230 or SPAN*3230), SPAN*3080',
    'ARTH*4350': '',
    'ARTH*4600': '',
    'ARTH*4800': '',
    'ASCI*3700': '9.0 credits',
    'EURO*4740': '(EURO*1100 or EURO*1200), EURO*2200, EURO*3000, EURO*3300',
    'FARE*4290': 'FARE*2700 or ECON*2310',
    'HIST*2100': '2.0 credits',
    'HIST*2450': '2.0 credits',
    'HIST*3480': '7.50 credits',
    'HIST*4200': '10.00 credits',
    'NUTR*4040': '14.50 credits, [1 of BIOM*2000, (BIOM*3100 or BIOM*3110), BIOM*3200], (NUTR*3040 or NUTR*3090)',
    'POLS*4140': 'POLS*2300, 1.0 credits',
    'POLS*4250': 'POLS*2250, 1.0 credits',
    'POLS*4710': 'POLS*2080 or POLS*2100, 1.0 credits',
    'POLS*4720': 'POLS*2200, 1.00 credits',
    'SART*3900': 'SART*3800, 3.50 credits in Studio Art'
}

excFixes = {
    'STAT*2080': '',
    'CIS*1000': 'CIS*1200',
    'CIS*1500': 'CIS*1300',
    'CIS*1300': 'CIS*1500',
    'PHYS*1300': 'SPH 4U, PHYS*1020, PHYS*1070',
    'PHYS*1080': 'IPS*1500, PHYS*1000',
    'STAT*2040': 'STAT*2060, STAT*2080, STAT*2120, STAT*2230',
    'ENGG*3640': '',
    'ENGG*2410': '',
    'ENGG*4110': '',
    'ENGG*4120': '',
    'ENGG*4130': '',
    'ENGG*4150': '',
    'ENGG*4160': '',
    'ENGG*4170': '',
    'ENGG*4180': '',
    'MATH*1030': 'MATH*1080, MATH*1200',
    'MATH*6031': 'MATH*4220 or MATH*6031',
    'MATH*6041': 'MATH*4270 or MATH*6041',
    'CHEM*2480': 'CHEM*2400',
    'CHEM*3430': 'TOX*3300',
    'ACCT*3350': '',
    'ACCT*4220': '',
    'ACCT*4230': '',
    'BUS*4550': 'AGEC*4550, FARE*4550',
    'BUS*4560': 'AGEC*4560, FARE*4560',
    'SOAN*2120': '',
    'FOOD*3230': '',
    'MCS*2600': 'Registration in BCOMM programs',
    'ENGL*1080': '',
    'ENGL*2120': '',
    'ENGL*2130': '',
    'ENGL*3940': '',
    'ENGL*3050': '',
    'ENGL*3960': '',
    'ENGL*3060': 'ENGL*2940',
    'ENVS*2230': '',
    'ENVS*2060': 'AGR*2320',
    'ENVS*4001': '12.00 credits',
    'ENVS*4410': '',
    'ENVS*6040': 'PBIO*4000',
    'PBIO*4000': 'ENVS*6040',
    'BIOL*1500': '',
    'FREN*6020': '',
    'PHYS*1600': '',
    'UNIV*1200': ''
}

def getDescriptions(codeArr):
    for codeStr in codeArr:
        regCodes = re.findall(r'[A-Z]{3,4}\*[0-9]{4}', codeStr)

        for code in regCodes:
            if code not in lookedup:
                Level = 'Undergraduate' if int(int(code.split('*')[1])/1000)*100 <= 400 else 'Graduate'
                found = getClasses.getDescription(({'Code': code, 'Level': Level}), False)
                lookedup[code] = found

                pre = found['Prerequisites'] if 'Prerequisites' in found else ""
                exc = found['Exclusions'] if 'Exclusions' in found else ""

                getDescriptions([pre, exc])

def parseOneOf(str, groups):
    if not str.strip().find('1 of ') == 0:
        return None

    str = str[5:]
    split = re.split(', | or |\. ', str)

    newGroups = []

    for x in split:
        if x.strip() in groups:
            newGroups += groups[x.strip()]['parsed']
        else:
            newGroups.append(x.strip())

    return {
        'type': 'OR',
        'groups': newGroups
    }



def parseTwoOf(str, groups):
    if not str.strip().find('2 of ') == 0:
        return None

    str = str[5:]
    split = re.split(', | or |\. ', str)

    OR = []

    for x in itertools.combinations(split, 2):
        part = []
        for y in x:
            if y.strip() in groups:
                part += groups[y.strip()]['parsed']
            else:
                part.append(y.strip())

        OR.append({
            'type':'AND',
            'groups': part
        })

    return {
        'type': 'OR',
        'groups': OR 
    }

def parseCredits(str, groups):
    # Completion of 4.0 credits including ENGG*1100
    # 14.50 credits including ECON*2310

    str = str.replace('A minimum of ', '')

    if str.find('credit') == -1:
        return None

    if str.find('credits including') != -1:
        str = str.replace('Completion of ', '')
        split = str.split(' credits including ')

        if split[-1] not in groups:
            return [{
                'type': 'AND',
                'groups': [{
                    'type': 'CREDITS',
                    'code': 'anything',
                    'credits': float(split[0])
                },
                    split[-1]
                ]
            }]
        else:
            return [{
                'type': 'AND',
                'groups': [{
                    'type': 'CREDITS',
                    'code': 'anything',
                    'credits': float(split[0])
                }
                ] + groups[split[-1]]['parsed']
            }]

    elif str.find(' credits in') != -1 or str.find(' credit in') != -1:
        split = re.split(' credits in | credit in ', str)
        return [{
            'type': 'CREDITS',
            'code': split[-1],
            'credits': float(split[0])
        }]
    else:
        split = str.replace('Minimum of ', '').split(' ')

        if (len(split) == 2):
            return [{
                'type': 'CREDITS',
                'code': 'anything',
                'credits': float(split[0])
            }]
        else:
            return [{
                'type': 'CREDITS',
                'code': split[1],
                'credits': float(split[0])
            }]

def parseAll(parseStr):
    groups = {}
    groupsSecond = {}
    
    # Doesn't support recursion
    closeStr = parseStr.split(']')
    for x in closeStr:
        start = x.find('[')
        if start > -1:
            groupsSecond['GROUP' + str(len(groups.keys())+len(groupsSecond.keys()))] = {
                    'replaced': x[start+1:],
                    'parsed': parseAll(x[start+1:])
                }

    for groupName in groupsSecond:
        parseStr = parseStr.replace('[' + groupsSecond[groupName]['replaced'] + ']', groupName)

    # Doesn't support recursion
    closeStr = parseStr.split(')')
    for x in closeStr:
        start = x.find('(')
        if start > -1:
            groups['GROUP' + str(len(groups.keys())+len(groupsSecond.keys()))] = {
                    'replaced': x[start+1:],
                    'parsed': parseAll(x[start+1:])
                }

    for groupName in groups:
        parseStr = parseStr.replace('(' + groups[groupName]['replaced'] + ')', groupName)

    groups.update(groupsSecond)

    # Parse '1 of'
    parsed = parseOneOf(parseStr, groups) or parseTwoOf(parseStr, groups)
    parsedGroups = []

    if parsed != None:
        parsedGroups.append(parsed)
    else:
        # Safe to split on or now that parse 1 of is gone
        parseArr = parseStr.split(' or ')
        OR = []

        for parseStrCur in parseArr:
            parseSub = re.split(', |\. ', parseStrCur)
            AND = []

            for parseSubStr in parseSub:
                if len(parseSubStr) < 3:
                    continue

                parsed = parseCredits(parseSubStr, groups)

                if parsed != None:
                    OR += parsed
                else:
                    if parseSubStr.strip() in groups:
                        AND += groups[parseSubStr.strip()]['parsed']
                    else:
                        AND.append(parseSubStr.strip())

            if len(AND) > 0:
                if not isinstance(AND, str) and len(AND) == 1 and not isinstance(AND[0], str):
                    OR.append(AND[0])
                else:
                    OR.append({'type': 'AND', 'groups': AND})

        acc = []
        for reduc in OR:
            if reduc['type'] == 'AND' and len(reduc['groups']) == 1:
                acc += reduc['groups']
            else:
                acc = None
                break

        if len(OR) == 0:
            None
        elif len(OR) == 1:
            parsedGroups = [OR[0]]
        elif acc != None:
            parsedGroups.append({'type': 'OR', 'groups': acc})
        else:
            parsedGroups.append({'type': 'OR', 'groups': OR})

    return parsedGroups

def createJSON(groupName):
    code = re.compile(rf"{groupName}\*", re.I)

    for found in collection.find({'School': 'Guelph', 'Code': { '$regex': code }}):
        pre = found['Prerequisites'] if 'Prerequisites' in found else ""
        exc = found['Exclusions'] if 'Exclusions' in found else ""
        code = found['Code']

        getDescriptions([pre, exc])
        lookedup[code] = found

    courseMapPre = {}
    courseMapExc = {}

    for found in lookedup:
        found = lookedup[found]
        pre = found['Prerequisites'] if 'Prerequisites' in found else ""
        exc = found['Exclusions'] if 'Exclusions' in found else ""

        print(found['Code'])
        print('pre ->', pre)
        if found['Code'] in preFixes:
            preParsed = parseAll(preFixes[found['Code']])
        else:
            preParsed = parseAll(pre.split('. ')[0].replace('This is a Priority Access Course', ''))

        print('exc->', exc)
        print()
        if found['Code'] in excFixes:
            excParsed = parseAll(excFixes[found['Code']])
        else:
            if exc.find('May') == 0:
                excParsed = []
            else:
                excParsed = parseAll(
                        exc
                            .split('. ')[0]
                            .replace('This is a Priority Access Course', '')
                            .split('Restricted to students')[0]
                            .split('Not available to')[0])

        courseMapPre[found['Code']] = preParsed
        courseMapExc[found['Code']] = excParsed
        # print(preParsed)
        # print('Exc', exc, '->', parseAll(exc))
        # print(printArrStr(preParsed))
        # print()

    # Connection
    '''
        {
            'type': '<EXCLUSION>'
            'color': 0xRRGGBB
            '
        }
    '''

    with open('./parsed/all.json', 'w') as outfile:
        json.dump({'prerequisites': courseMapPre, 'restrictions': courseMapExc}, outfile)
