import re
import regex
import string
import random
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
    'ECON*4400': 'ECON*2310, 12.0 credits',
  #  'CHEM*2060': 'CHEM*1050, MATH*1210, (1 of PHYS*1010, PHYS*1070, PHYS*1300)',
  #  'CHEM*7940': 'CHEM*7840',
  #  'CHEM*7840': 'CHEM*7940',
  #  'MGMT*4000': 'MGMT*3320, [ECON*3460, ECON*3560, (1 of ECON*2560 or FIN*2000)], (1 of FARE*3310, HTM*3120, REAL*3890)',
  #  'MGMT*6500': 'MGMT*6100, MGMT*6200',
    'ENVS*3290': '1 of ENVS*2080, ENVS*2320, [MBG*2040, (BIOL*2060 or MICR*2420)]',
  #  'ECON*2740': 'ECON*1100, (ECON*1050 or FARE*1040), (1 of MATH*1000, MATH*1030, MATH*1050, MATH*1080, MATH*1200)',
    'SPAN*3800': '(HISP*3220 or SPAN*3220), (HISP*3230 or SPAN*3230), SPAN*3080',
    'SPAN*3810': '(HISP*3220 or SPAN*3220), (HISP*3230 or SPAN*3230), SPAN*3080',
  #  'ARTH*4350': '',
    'ARTH*4600': '',
  #  'ARTH*4800': '',
  #  'ASCI*3700': '9.0 credits',
    'EURO*4740': '(EURO*1100 or EURO*1200), EURO*2200, EURO*3000, EURO*3300',
    'FARE*4290': 'FARE*2700 or ECON*2310',
    'HIST*2100': '2.0 credits',
    'HIST*2450': '2.0 credits',
    'HIST*3480': '7.50 credits',
    'HIST*4200': '10.00 credits',
    'NUTR*4040': '14.50 credits, [1 of BIOM*2000, (BIOM*3100 or BIOM*3110), BIOM*3200], (NUTR*3040 or NUTR*3090)',
  #  'POLS*4140': 'POLS*2300, 1.0 credits',
    'POLS*4250': 'POLS*2250, 1.0 credits',
  #  'POLS*4710': 'POLS*2080 or POLS*2100, 1.0 credits',
    'POLS*4720': 'POLS*2200, 1.00 credits',
  #  'SART*3900': 'SART*3800, 3.50 credits in Studio Art',
    'ECON*2720': 'ECON*1050, (ECON*1100 or 1.50 credits in history)',
    'ENGG*3100': '6.00 credits in ENGG, ENGG*2100',
    'ENGG*4400': '6.00 credits in ENGG, ENGG*3150, ENGG*3170',
  #  'FRHD*4200': 'FRHD*1020, FRHD*2100, 1.00 credit',
    'HIST*2600': '2.00 credits',
    'HIST*4450': '10.00 credits including HIST*2450',
    'MATH*4440': '3.0 credits in MATH',
  #  'POLS*4030': 'POLS*2000, 1.00 credits',
  #  'POLS*4160': 'POLS*2000, 1.00 credits',
  #  'POLS*4200': '(1 of POLS*2080, POLS*2100, POLS*2200), 1.00 credits',
    'POLS*4740': '(POLS*3130 or POLS*3210), 1.00 credits',
    'POLS*4900': '14.00 credits',
  #  'PSYC*4580': '14.00 credits, PSYC*2040 or PSYC*3290',
    'NUTR*4210': 'NUTR*3210, (1 of BIOM*3200, HK*3810)',
    'TRMH*6310': 'TRMH*6100, (1 of TRMH*6290, MCS*6050, SOC*6130, PSYC*6060)',
    'TRMH*6400': 'TRMH*6100, TRMH*6200, TRMH*6310, (1 of TRMH*6290, MCS*6050, SOC*6130, PSYC*6060), (1 of ANTH*6140, MCS*6080, FRAN*6020, SOC*6140)',
    'BIOC*4540': 'BIOC*3570',
    'TOX*3300': 'CHEM*2480, BIOC*2580',
    'BUS*6810': '',
    'CHEM*7940': '',
    'FRAN*6010': '',
    'STAT*2040': 'MATH*1080',
    'MATH*1200': '',
    'ENGG*4110': '',
    'ENGG*4120': '',
    'ENGG*4130': '',
    'ENGG*4140': '',
    'ENGG*4150': '',
    'ENGG*4160': '',
    'ENGG*4170': 'ENGG*4000',
    'ENGG*4180': '',
    'GEOG*3610': '1 of GEOG*2000, GEOG*2110',
    'FARE*4310': '1 of FARE*2700, ECON*2310, ECON*2100',
    'HTM*4080': '14.00 credits',
    'MATH*3160': 'MATH*1160 or MATH*2160',
    'MCB*4600': 'MBG*3350',
    'SART*4750': '',
    'PHIL*3040': '1.50 credits in Philosophy, 7.50 credits or PHIL*2120',
    'POLS*4100': '2 of POLS*2250, POLS*2300, POLS*3250',
    'PSYC*4780': '(1 of PSYC*2040 or PSYC*3290) or STAT*2050',
    'MGMT*3140': '9.00 credits including (1 of MATH*1030, MATH*1080, MATH*1200), (1 of ECON*2740, PSYC*1010, STAT*2040, STAT*2060)',
    'SOC*4900': '15.00 credits including SOC*3310, SOAN*3070, SOAN*3120',
#    'FOOD*3090': 'AGR*1110, CHEM*1040, (1 of BIOL*1050, BIOL*1070, BIOL*1080)',
#    'PSYC*3000': 'PSYC*2070, PSYC*2360, (2 of PSYC*2020, PSYC*2310, PSYC*2450, PSYC*2740), (2 of PSYC*2330, PSYC*2390, PSYC*2410, PSYC*2650)',
    'PSYC*4310': '14.00 credits including [PSYC*2310, PSYC*3250, (PSYC*2040 or PSYC*3290), 0.50 credits in Psychology at the 3000 level]',
    'PSYC*4460': '14.00 credits including [PSYC*3250, (PSYC*2020 or PSYC*3390), (PSYC*2450 or PSYC*2740), (PSYC*2040 or PSYC*3290), 0.50 credits in Psychology at the 3000 level]',
    'PHYS*3080': '(IPS*1500 or PHYS*1080), (1 of MATH*1000, MATH*1080, MATH*1200), (1 of IPS*1510, PHYS*1010, PHYS*1070, PHYS*1130, PHYS*1300)',
    'PSYC*4240': '14.00 credits including [(PSYC*2040 or PSYC*3290), 1.00 credits in Psychology at the 3000 level]',
    'MUSC*2500': 'MUSC*1180 or MUSC*2180',
    'FRHD*4200': 'FRHD*1020, FRHD*2100 and 1.00 credits',
    'CHEM*1040': 'CHEM*1060',
    'IPS*1500': 'PHYS*1020, PHYS*1300',
    'STAT*2060': '',
 #   'FREN*1300': '',
    'MATH*4600': '1.00 credits in Mathematics at the 3000 level',
    'PHYS*1070': 'PHYS*1020',
    'ANSC*4610': '13.00 credits and 2.00 credits in ANSC',
    'CIS*3190': 'CIS*2500',
    'LAT*2000': 'LAT*1110',
    'ECON*3710': 'ECON*2310, (ECON*2770 or MATH*1210)',
    'STAT*2080': '',
    'FOOD*4220': '14.00 credits',
    'FREN*1200': 'FREN*1150',
 #   'GEOG*2420': '0.50 credits in geography',
    'LAT*1110': 'LAT*1100',
    'MCB*4500': 'MBG*3350',
    'MCB*4510': 'MCB*4500',
    'MCS*2600': 'MCS*1000, (1 of BUS*2090, HROB*2090, HROB*2100, PSYC*1000, PSYC*1200)',
    'MUSC*4460': 'MUSC*3510',
    'PHIL*2280': '0.50 credits in Philosophy',
    'POLS*4260': '(2 of POLS*2250, POLS*2300, POLS*3250), 1.00 credits in the Public Policy',
    'STAT*4600': '1.00 credits in Statistics at the 3000 level',
    'VETM*4900': '',
    'FOOD*4070': '7.00 credits in science',
    'GERM*2490': 'GERM*1110',
    'GREK*1110': 'GREK*1100',
    'PHYS*1080': '1 of PHYS*1020, PHYS*1300',
    'PHYS*1130': '',
    'MATH*1080': '',
    'CHEM*4900': '3 of CHEM*3430, CHEM*3640, CHEM*3650, CHEM*3750, CHEM*3760, CHEM*3870',
    'MATH*1160': '',
    'PHYS*1010': '',
    'ENGG*3650': '(ENGG*2230 or MET*2030), (MATH*1210 or MATH*2080), (STAT*2120 or STAT*2040)',
    'ENGG*3150': '4.00 credits in ENGG, ENGG*1210',
 #   'PHYS*2030': '1.00 credits in physics',
    'BIOL*3450': 'BIOL*1070, CHEM*1050, ZOO*2700',
    'POLS*4050': '0.5 credits in Political Law',
  #  'POLS*4730': '1.00 credit at the 3000 level in the Comparative Politics',
    'TOX*4100': 'PATH*3610',
    'NANO*1000': '',
    'POLS*3850': '8.00 credits and 2.00 credits in Political Science',
#    'MUSC*3410': 'MUSC*2420 and (2 of MUSC*2530, MUSC*2540, MUSC*2550, MUSC*2560)',
#    'ARTH*4310': '10.00 credits in Art History at the 3000 level',
#    'ARTH*4330': '10.00 credits in Art History at the 3000 level',
    'POLS*4970': '',
#    'FCSS*2020': '3.00 credits including FCSS*1020',
#    'POPM*6290': '',
    'ZOO*3050': 'MBG*2040 and BIOL*2400',
    'PABI*6091': 'PABI*6080 and PABI*6090'
}

excFixes = {
    'MBG*1000': '',
    'THST*4280': '',
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
    'UNIV*1200': '',
    'CHEM*1100': '',
    'UNIV*2410': '',
    'ANSC*6730': 'ANSC*4080 or ANSC*4100',
    'ENVS*6300': 'ENVS*6250',
}

def genId(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def fixParseString(str_):
    return str_.replace(', including', ' including').replace(')', '')

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

def fixString(str_):
    creditMatch = r'(\d{1,}\.?\d{0,3})'

    fix1 = r'\(excluding .*\)'
    str_ = regex.sub(fix1, '', str_)
    str_ = str_.replace('A minimum of ', '')
    
    fix2 = creditMatch + r' credits including ' + creditMatch + ' credits'
    fix2Fix = 'including ' + creditMatch + ' credits '
    found = regex.match(fix2, str_)

    if found != None:
        str_ = regex.sub(fix2Fix, '', str_)

    str_ = str_.replace('Completion of previous co-op work requirements in ', '')
    str_ = str_.replace('4U Advanced Functions', '')
    str_ = str_.replace('Completion of ', '')
    str_ = str_.replace('Minimum of ','')

    fix3 = 'A minimum grade of \d\d% in '
    str_ = regex.sub(fix3, '', str_)

    str_ = str_.replace('the music core.', '')
    str_ = str_.replace('including at least', ',')

    fix4 = 'All Phase \d courses.'
    str_ = regex.sub(fix4, '', str_)

    fix5 = '[Mm]inimum cumulative average of \d\d%'
    str_ = regex.sub(fix5, '', str_)
    fix6 = '; cumulative average of \d\d%'
    str_ = regex.sub(fix6, '', str_)
    fix7 = 'minimum \d\d% cumulative average'
    str_ = regex.sub(fix7, '', str_)


    str_ = str_.replace(' is recommended', '')
    str_ = str_.replace(' is str_ongly recommended', '')
    str_ = str_.replace('recommended', '')
    str_ = str_.replace('on piano', '')
    str_ = str_.replace('credit at', 'credits at')
    str_ = str_.replace(' or equivalent', '')
    str_ = str_.replace(' completed;', '')
    str_ = str_.replace('as appropriate to the topic of the course: ', '')

    fix8 = ' plus \d{1,3} hours of leadership experience'
    str_ = regex.sub(fix8, '', str_)
    str_ = str_.replace(':', '')

    return str_

def parse(str_, code):
    str_ = fixString(str_)
    matchObj = {}

    str_ = str_.strip()

    matches = regex.finditer(r'([\(\[]([^()[\]]|(?R))*[)\]])', str_)
    if matches != None:
        for x in matches:
            id = genId()
            parsed = parse(x.group()[1:-1].strip(), code)
            matchObj[id] = parsed
            str_ = str_.replace(x.group().strip(), id)

    if len(re.findall(r'[\]\[\)\)]', str_)) > 0:
        print('ERROR bracket', code, matchObj, str_)
        exit()

    andCount = str_.count('and ')
    orCount = str_.count('or ')

    if (andCount > 1 or orCount > 1):
        print('ERROR', code, matchObj, str_)
        exit()

    type = 'AND'

    if orCount > 0:
        type = 'CHOOSE'

    numReg = r'(\d{1,}\.?\d{0,3})'
    codeMatch = r'((\w{2,4}\*\d{2,4}(\/2)?)|(([A-Z]|\d){8}))'
    codeList = '(^ )?' + codeMatch + "((\s?,?\s?)" + codeMatch + ")*(?=(,|$|\.|( or )|))(?!( or equivalent))"
    codeListNoEnd = '^' + codeMatch + r"((\s?,?\s?)" + codeMatch + r")*"

    creditMatch = r'(?<!of )' + numReg + ' credits(?!((,? in)|( from)|( of)|( at)))'
    creditsInMatch = numReg + r' credits (in|of|at) .+?((?= or )|(?= from )|(?=,)|$)'
    creditsIncludingX = numReg + ' credits(,)? including ' + codeList
    listAnd = '(^ )?' + codeListNoEnd + ',? and ' + codeMatch + '(?=(,|$|\.| |))'
    listOr = '(^ )?' + codeListNoEnd + ',? or ' + codeMatch + '(?=(,|$|\.| |))'
    creditsIncludingXorY = numReg + ' credits(,)? including ' + codeMatch + ' or ' + codeMatch
    creditsInIncluding = numReg + ' credits in .*,? including ' + codeMatch

    matches = re.finditer(r"\d( )?of " + codeList + '( or ((\w{2,4}\*\d{2,4}(\/2)?)|(([A-Z]|\d){8})))?', str_)
    if matches != None:
        for x in matches:
            count = x.group()[0]
            codes = []
            tmp = re.finditer(codeMatch, x.group())
            for y in tmp:
                addGroup = y.group().strip()
                if addGroup in matchObj:
                    addGroup = matchObj[addGroup]
                else:
                    addGroup = [addGroup]

                codes += addGroup

            id = genId()
            matchObj[id] = [{
                'type': 'CHOOSE',
                'count': int(count),
                'groups': codes
            }]

            str_ = str_.replace(x.group(), id)

    matches = re.finditer(creditsInIncluding, str_)
    if matches != None:
        for x in matches:
            spl = regex.split(r' credits in |,? including ', x.group())
            if len(spl) != 3:
                print('ERROR creditsInIncluding', code, matchObj, str_)
                exit()
    
            count = spl[0]
            subject = spl[1]
            codex = spl[2]

            if codex in matchObj:
                codex = matchObj[codex]
            else:
                codex = [codex]

            obj = {
                'type': 'AND',
                'groups': [
                    {
                        'type': 'CREDITS',
                        'count': count,
                        'subject': subject
                    }
                ] + codex
            }

            id = genId()
            matchObj[id] = [obj]
            str_ = str_.replace(x.group(), id)

    matches = re.finditer(creditsIncludingXorY, str_)
    if matches != None:
        for x in matches:
            spl = regex.split(r' credits including | or ', x.group())
            if len(spl) != 3:
                print('ERROR creditsInIncludingXorY', code, matchObj, str_)
                exit()

            count = spl[0]
            codex = spl[1]
            codey = spl[2]

            if codex in matchObj:
                codex = matchObj[codex]
            else:
                codex = [codex]
            if codey in matchObj:
                codey = matchObj[codey]
            else:
                codey = [codey]

            obj = {
                'type': 'AND',
                'groups': [
                    {
                        'type': 'CREDITS',
                        'count': count,
                        'subject': 'any'
                    },
                    {
                        'type': 'CHOOSE',
                        'count': 1,
                        'groups': codex + codey
                    }
                ]
            }

            id = genId()
            matchObj[id] = [obj]
            str_ = str_.replace(x.group(), id)

    matches = re.finditer(creditsIncludingX, str_)
    if matches != None:
        for x in matches:
            spl = regex.split(r' credits,? including |, ', x.group())
            if len(spl) < 2:
                print('ERROR creditsIncludingX', code, matchObj, str_)
                exit()

            count = spl[0]
            codes = []

            for y in spl[1:]:
                codex = y
                if codex in matchObj:
                    codex = matchObj[codex]
                else:
                    codex = [codex]

                codes += codex

            obj = {
                'type': 'AND',
                'groups': [
                    {
                        'type': 'CREDITS',
                        'count': count
                    }
                ] + codes
            }
            id = genId()
            matchObj[id] = [obj]
            str_ = str_.replace(x.group(), id)

    matches = re.finditer(creditMatch, str_)
    if matches != None:
        for x in matches:
            obj = {
                'type': 'CREDITS',
                'count': x.group().split(' ')[0],
                'subject': 'any'
            }

            id = genId()
            matchObj[id] = [obj]
            str_ = str_.replace(x.group(), id)

    matches = re.finditer(creditsInMatch, str_)
    if matches != None:
        for x in matches:
            spl = regex.split(r' credits in | credits at | credits of ', x.group())
            if len(spl) != 2:
                print('ERROR credits in', code, matchObj, str_)
                exit()

            count = spl[0]
            subject = spl[1]

            obj = {
                'type': 'CREDITS',
                'count': count,
                'subject': subject
            }

            id = genId()
            matchObj[id] = [obj]
            str_ = str_.replace(x.group(), id)

    matches = re.finditer(r'^' + codeList, str_)
    if matches != None:
        for x in matches:
            if len(x.group().split(',')) > 1:
                id = genId()

                codes = []
                tmp = re.finditer(codeMatch, x.group())
                for y in tmp:
                    addGroup = y.group().strip()
                    if addGroup in matchObj:
                        addGroup = matchObj[addGroup]
                    else:
                        addGroup = [addGroup]

                    codes += addGroup

                matchObj[id] = [{ 'type': 'AND', 'groups': codes }]
                str_ = str_.replace(x.group(), id)
    
    matches = regex.finditer(listAnd, str_)
    if matches != None:
        for x in matches:
            spl = regex.split(r' and |, ', x.group())

            codes = []

            for y in spl:
                codex = y
                if codex in matchObj:
                    codex = matchObj[codex]
                else:
                    codex = [codex]

                codes += codex

            obj = {
                'type': 'AND',
                'groups': codes
            }

            id = genId()
            matchObj[id] = [obj]
            str_ = str_.replace(x.group(), id)

    matches = regex.finditer(listOr, str_)
    if matches != None:
        for x in matches:
            spl = regex.split(r' or |, ', x.group())

            codes = []

            for y in spl:
                codex = y
                if codex in matchObj:
                    codex = matchObj[codex]
                else:
                    codex = [codex]

                codes += codex

            obj = {
                'type': 'CHOOSE',
                'count': 1,
                'groups': codes
            }

            id = genId()
            matchObj[id] = [obj]
            str_ = str_.replace(x.group(), id)

    if str_.count(',') == 0 and orCount == 0 and andCount == 0:
        found = None
        count = 0

        for x in matchObj:
            if str_.find(x) > -1:
                found = matchObj[x]
                count += 1

        if count > 1:
            print('ERROR no comma', code, matchObj, str_)
            exit()

    if regex.match(codeMatch + r'[\s.,]*', str_) == None and len(str_) > 8:
        print('ERROR found', code, matchObj, str_)
        exit()

    str_ = str_.strip().replace('.', '')
    spl = str_.split(',')
    codes = []

    for codeAnd in spl:
        codex = codeAnd.strip()
        if codex == '':
            continue
        matches = regex.match('^' + codeMatch + '$', codex)
        if matches == None:
            print('NOTICE no match for code format', code, matchObj, codex)
            continue

        if codex in matchObj:
            codex = matchObj[codex]
        else:
            codex = [codex]

        codes += codex

    obj = [{
        'type': 'AND',
        'groups': codes
    }]

    if len(codes) == 0:
        return []

    if len(codes) == 1 and isinstance(codes[0], dict):
        return [codes[0]]

    return obj


def createJSON(groupName):
    code = re.compile(rf"{groupName}\*", re.I)

    for found in collection.find({'School': 'Guelph', 'Code': { '$regex': code }}):
        pre = found['Prerequisites'] if 'Prerequisites' in found else ""
        exc = found['Exclusions'] if 'Exclusions' in found else ""
        code = found['Code']

        if ('Offered' not in found):
            Level = 'Undergraduate' if int(int(code.split('*')[1])/1000)*100 <= 400 else 'Graduate'
            found = getClasses.getDescription(({'Code': code, 'Level': Level}), False)

        getDescriptions([pre, exc])
        lookedup[code] = found

    courseMapPre = {}
    courseMapExc = {}

    for found in lookedup:
        found = lookedup[found]
        pre = found['Prerequisites'] if 'Prerequisites' in found else ""
        exc = found['Exclusions'] if 'Exclusions' in found else ""

        # print('pre ->', pre)
        if found['Code'] in preFixes:
            pre = preFixes[found['Code']]

        preParsed = parse(pre, found['Code'])
        # print(preParsed)

        courseMapPre[found['Code']] = preParsed

    print(len(courseMapPre), "items found")

    with open('./parsed/all.json', 'w') as outfile:
        json.dump({'prerequisites': courseMapPre, 'restrictions': courseMapExc}, outfile)

if __name__ == '__main__':
    createJSON('')
