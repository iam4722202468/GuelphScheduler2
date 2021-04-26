import re
import regex  # backwards compatible with re, and provides some additional features
import string
import random
import json

from pymongo import MongoClient
client = MongoClient()

import sys
sys.path.insert(0,'../webserver/schools/Guelph')

db = client['scheduler']
collection = db['cachedData']

# known fixes for pre-requisite parser
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

# known fixes for excemption parser fixes
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
    """
    Generates 8 characters long random string.

    Used as placeholder to break down pre-requisites string into smaller independent chunks.
    Gets replaced by parsed json equivalent.

    Attributes
    ----------
    size: int
        length of output string
    chars: str
        string of characters that can be used to generate output string
    """

    return ''.join(random.choice(chars) for _ in range(size))

def remove_excluding_clause(line):
    """
    Removes substring of the pattern "(excluding <any characters except newline>)"

    Attributes
    ----------
    line: str
        with pattern
    
    Returns
    ----------
    line: str
        with no excluding clause
    """

    # .* match everything except newline character
    # TODO: why not newline?
    fix1 = r'\(excluding .*\)'    
    return regex.sub(fix1, '', line)

def remove_credit_clause(line):
    # TODO: need fix 3000-level? instead of 3000 level?
    # 10.00 credits including 1.50 credits in History at the 3000-level vs 10.00 credits in History at the 3000-level
    creditMatch = r'(\d{1,}\.?\d{0,3})'
    fix2 = creditMatch + r' credits including ' + creditMatch + ' credits'
    fix2Fix = 'including ' + creditMatch + ' credits '
    
    found = regex.match(fix2, line)
    if found != None:
        line = regex.sub(fix2Fix, '', line)
    return line

def remove_minimum_grade_clause(line):
    fix3 = 'A minimum grade of \d\d% in '  # music stuff
    return regex.sub(fix3, '', line)

def remove_all_phase_clause(line):
    fix4 = 'All Phase \d courses.'
    return regex.sub(fix4, '', line)

def remove_minimum_cumulative_average(line):
    if 'cumulative average' in line:
        fix5 = '[Mm]inimum cumulative average of \d\d%'
        fix6 = '; cumulative average of \d\d%'
        fix7 = 'minimum \d\d% cumulative average'

        line = regex.sub(fix5, '', line)
        line = regex.sub(fix6, '', line)
        line = regex.sub(fix7, '', line)
        return line
    else:
        return line

def remove_recommended(line):
    # TODO: show recommended on UI
    line = line.replace(' is recommended', '')
    line = line.replace(' is str_ongly recommended', '')
    line = line.replace('recommended', '')
    return line

def remove_leadership_experience(line):
    fix8 = ' plus \d{1,3} hours of leadership experience'
    return regex.sub(fix8, '', line)

# TODO: show these as assumptions on UI
def fixString(line):
    """
    Removes contextual information from pre-requisite string

    Attributes
    ----------
    line: str
        original pre-requisite string
    
    Returns
    ----------
    line: str
        modified pre-requisite string
    """

    line = remove_excluding_clause(line)
    line = line.replace('A minimum of ', '')  # TODO: should minimum be represented in symbol? is it not of value?
    line = remove_credit_clause(line)
    line = line.replace('Completion of previous co-op work requirements in ', '')  # for co-op stuff
    line = line.replace('4U Advanced Functions', '')  # for math
    line = line.replace('Completion of ', '')  # music and engg
    line = line.replace('Minimum of ','')  # TODO: should minimum be represented in symbol?
    line = remove_minimum_grade_clause(line)
    line = line.replace('the music core.', '')  # fix patch on Completion of
    line = line.replace('including at least', ',')  # inconsistently removes line # TODO: check against remove_credit_clause
    line = remove_all_phase_clause(line)
    line = remove_minimum_cumulative_average(line)
    line = remove_recommended(line)
    line = line.replace('on piano', '')
    line = line.replace('credit at', 'credits at')
    line = line.replace(' or equivalent', '')
    line = line.replace(' completed;', '')
    line = line.replace('as appropriate to the topic of the course: ', '')
    line = remove_leadership_experience(line)
    line = line.replace(':', '')  # not sure if required

    return line

def group_extraction(line, code):
    """
    Identifies highest level of the recursive groups

    Identifies the highest level of recursive groups in pre-requisites of the form (...info...) or [...info...] or 
    a nested / recursive combination of them.

    Attributes
    ----------
    line: str
        original pre-requisite string
    code: str
        course code for e.g. ACCT*3330
    silent: bool
        silent if True, print otherwise
    """

    matchObj = {}

    line = fixString(line)  # pre parse 
    line = line.strip()

    matches = regex.finditer(r'([\(\[]([^()[\]]|(?R))*[)\]])', line)
    if matches != None:
        for x in matches:  # x -> regex.Match object 
            id = genId() # generate random id
            matchObj[id] = x.group()  # {'id': 'string of the identified group'}
            line = line.replace(x.group().strip(), id)  # replace group substring with id in line
    
    return matchObj, line

def get_and_count(line):
    return line.count('and ')

def get_or_count(line):
    return line.count('or ')

def get_and_or(line):
    andCount = get_and_count(line)
    orCount = get_or_count(line)

    if (andCount > 1 or orCount > 1):
        print('ERROR', code, matchObj, str_)
        exit()
        
    if orCount > 0:
        return 'CHOOSE'
    else:
        return 'AND'

def choose_n_from_course_list(line, codeList, codeMatch):
    """
    Parse string of type "n of course code, course code, ... or course code" where course code 
    is used interchangbly with placeholder #ids

    Attributes
    ---------
    line: str
        pre-requisite string
    codeList: str
        used in regex expression to find a list of course codes
    codeMatch: str
        used in regex expression to find course code / placeholder #ids
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'CHOOSE',
                'count': count of courses to choose,
                'groups': list of courses to choose from
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """

    matchObj = {}
    matches = re.finditer(r"\d( )?of " + codeList + '( or '+ codeMatch + ')?', line)
    if matches != None:
        for x in matches:
            count = x.group()[0]  # 1st char is number -> \d
            codes = []
            tmp = re.finditer(codeMatch, x.group())  # iterate through all codes in the string
            for y in tmp:
                addGroup = y.group().strip()
                if addGroup in matchObj:
                    addGroup = matchObj[addGroup]
                else:
                    addGroup = [addGroup]

                codes += addGroup  # list concatenation

            id = genId()
            matchObj[id] = [{
                'type': 'CHOOSE',
                'count': int(count),
                'groups': codes
            }]
            line = line.replace(x.group(), id)  # replace group in pre-requisite string with placeholder id

    return matchObj, line

def credits_in_subject_Including(line, creditsInIncluding):
    """
    Parse string of type "x credits in subject including course code" where course code 
    is used interchangbly with placeholder #ids

    Attributes
    ---------
    line: str
        pre-requisite string
    creditsInIncluding: str
        used in regex expression to find if "credits in subject including course code" pattern is matched
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'AND',
                'groups': [
                    {
                        'type': 'CREDITS',
                        'count': (float) number of credits to complete,
                        'subject': (str) subject to have the completed credits in
                    },
                    (str) code of the course to have completed, including the subject credits mentioned
                ]
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """
    
    matchObj = {}
    matches = re.finditer(creditsInIncluding, line)
    if matches != None:
        for x in matches:
            spl = regex.split(r' credits in |,? including ', x.group())
            if len(spl) != 3:
                print('ERROR creditsInIncluding', matchObj, line)
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
            line = line.replace(x.group(), id)  # replace group substring with placeholder id

    return matchObj, line

def credits_including_X_or_Y(line, creditsIncludingXorY):
    """
    Parse string of type "x credits including course code or course code" where course code 
    is used interchangbly with placeholder #ids

    Attributes
    ---------
    line: str
        pre-requisite string
    creditsIncludingXorY: str
        used in regex expression to find if "x credits course code or course code" pattern is matched
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'AND',
                'groups': [
                    {
                        'type': 'CREDITS',
                        'count': (float) number of completed credits,
                        'subject': 'any'
                    },
                    {
                        'type': 'CHOOSE',
                        'choose': 1,
                        'groups': [(str) codeX,  (str) codeY]
                    }
                ]
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """

    matchObj = {}
    matches = re.finditer(creditsIncludingXorY, line)
    if matches != None:
        for x in matches:
            spl = regex.split(r' credits including | or ', x.group())
            if len(spl) != 3:
                print('ERROR creditsInIncludingXorY', code, matchObj, line)
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
            line = line.replace(x.group(), id)  # replace group substring with placeholder id

    return matchObj, line

def credits_including_X(line, creditsIncludingX):
    """
    Parse string of type "x credits including course code" where course code 
    is used interchangbly with placeholder #ids

    Attributes
    ---------
    line: str
        pre-requisite string
    creditsIncludingX: str
        used in regex expression to find if "x credits including course code" pattern is matched
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'AND',
                'groups': [
                    {
                        'type': 'CREDITS',
                        'count': (float) number of completed credits
                    },
                    (str) code of the course to have completed 
                ]
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """
    
    matchObj = {}
    matches = re.finditer(creditsIncludingX, line)
    if matches != None:
        for x in matches:
            spl = regex.split(r' credits,? including |, ', x.group())
            if len(spl) < 2:
                print('ERROR creditsIncludingX', matchObj, line)
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
            line = line.replace(x.group(), id)  # replace group substring with placeholder id

    return matchObj, line

def credit_match(line, creditMatch):
    """
    Parse string of type "x credits" where subject must NOT be specified through 
    links like "credits in", "credits at" or "credits of"

    Attributes
    ---------
    line: str
        pre-requisite string
    creditMatch: str
        used in regex expression to find if "x credits" pattern is matched independent of a subject
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'CREDITS',
                'count': (float) number of completed credits,
                'subject': 'any'
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """

    matchObj = {}
    matches = re.finditer(creditMatch, line)
    if matches != None:
        for x in matches:
            obj = {
                'type': 'CREDITS',
                'count': x.group().split(' ')[0],
                'subject': 'any'
            }

            id = genId()
            matchObj[id] = [obj]
            line = line.replace(x.group(), id)  # replace group substring with placeholder id

    return matchObj, line

def credits_in_subject(line, creditsInMatch):
    """
    Parse string of type "x credits in/at/of subject"

    Attributes
    ---------
    line: str
        pre-requisite string
    creditMatch: str
        used in regex expression to find if "x credits in/at/of subject" pattern is matched
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'CREDITS',
                'count': (float) number of completed credits,
                'subject': (str) subject to have the completed credits in
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """

    matchObj = {}
    matches = re.finditer(creditsInMatch, line)
    if matches != None:
        for x in matches:
            spl = regex.split(r' credits in | credits at | credits of ', x.group())
            if len(spl) != 2:
                print('ERROR credits in', matchObj, line)
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
            line = line.replace(x.group(), id)  # replace group substring with placeholder id

    return matchObj, line

def implied_and(line, codeList, codeMatch):
    """
    Parse string of type "course code, course code, course code ..." where course code 
    is used interchangbly with placeholder #ids. The , implies
    "course code and course code and course code ..."

    Attributes
    ---------
    line: str
        pre-requisite string
    codeList: str
        used in regex expression to find a list of course codes
    codeMatch: str
        used in regex expression to find course code / placeholder #ids
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'AND',
                'groups': [(str) code, (str) code, ...]
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """

    matchObj = {}
    matches = re.finditer(r'^' + codeList, line)
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
                line = line.replace(x.group(), id)  # replace group substring with placeholder id
    
    return matchObj, line

def explicit_and(line, listAnd):
    """
    Parse string of type "course code and course code and course code ..." where course code 
    is used interchangbly with placeholder #ids

    Attributes
    ---------
    line: str
        pre-requisite string
    listAnd: str
        used in regex expression to check if course codes are explicitly joined by "and"
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'AND',
                'groups': [(str) code, (str) code, ...]
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """

    matchObj = {}
    matches = regex.finditer(listAnd, line)
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
            line = line.replace(x.group(), id)  # replace group substring with placeholder id

    return matchObj, line

def explicit_or(line, listOr):
    """
    Parse string of type "course code or course code or course code ..." where course code 
    is used interchangbly with placeholder #ids

    Attributes
    ---------
    line: str
        pre-requisite string
    listOr: str
        used in regex expression to check if course codes are explicitly joined by "or"
    
    Returns
    ----------
    matchObj: dict
        dictionary with id as key and parsed json array as value as 
        {'id': [{
                'type': 'CHOOSE',
                'count': 1,
                'groups': [(str) code, (str) code, ...]
            }]
        }
    line: str
        modified pre-requisite string with group replaced by #id
    """

    matchObj = {}
    matches = regex.finditer(listOr, line)
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
            line = line.replace(x.group(), id)  # replace group substring with placeholder id

    return matchObj, line

def check_missing_conditions(line, dictionary):
    """
    Checks if there are more than 1 course codes or placeholder ids with no mentioned way to connect them.

    Attributes
    ----------
    line: str
        pre-requisite string
    dictionary: dict
        dictionary of id value pair.
        {'id': 'json parse', ...}
    
    Returns
    ----------
    False if no missing conditions. Exits program otherwise
    """
    # no connectors
    if line.count(',') == 0 and get_or_count(line) == 0 and get_and_count(line) == 0:
        found = None
        count = 0
        # iterate through each id
        for x in dictionary:
            # if the id is a substring of line
            if line.find(x) > -1:
                found = dictionary[x]
                count += 1
        # more than 1 ids with no connector
        if count > 1:
            print('ERROR no comma', dictionary, line)
            exit()
    return False

def check_code_present(line, codeMatch):
    """
    Checks at least 1 course code or id is present in line

    Attributes
    ----------
    line: str
        pre-requisite string
    codeMatch: str
        used in regex to identify course code or placeholder id 
    
    Returns
    ----------
    True if code present. Exits program otherwise
    """

    if regex.match(codeMatch + r'[\s.,]*', line) == None and len(line) > 8:
        print('ERROR found', line)
        exit()
    return True

def cleanup_get_value(line, codeMatch, dictionary):
    """
    Makes final cleanups on parsed pre-requisite for this level (multiple levels due to recursion) and 
    returns the parsed json where groups may still contain placeholder ids.

    Attributes
    ----------
    line: str
        pre-requisite string
    codeMatch: str
        used in regex to identify course code or placeholder id 
    dictionary: dict
        dictionary of id value pair.
        {'id': 'json parse', ...}
    
    Returns
    ----------
    parsed json array [] and (str) describing it
    """

    line = line.strip().replace('.', '')
    spl = line.split(',')  # , remains due to parsing 
    codes = []
    
    for codeAnd in spl:
        codex = codeAnd.strip()
        if codex == '':
            continue
        matches = regex.match('^' + codeMatch + '$', codex)
        if matches == None:
            print('NOTICE no match for code format', dictionary, codex)
            continue

        if codex in dictionary:
            codex = dictionary[codex]
        else:
            codex = [codex]

        codes += codex
    
    obj = [{
        'type': 'AND',
        'groups': codes
    }]

    if len(codes) == 0:
        return [], 'no pre'

    if len(codes) == 1 and isinstance(codes[0], dict):
        return [codes[0]], 'complex pre'

    return obj, 'single pre'

def return_routine(codes, value, dictionary, code):
    """
    Checks if any placeholder id still remain on the parsed codes list.
    If id is present and parsed, replace id with parsed value.
    If id is present and unparsed (str), call parse() to get parsed value
    If no id remain on parsed codes list, return it as final parsed pre-requisite for the course code

    Attributes
    ----------
    codes: list
        parsed json array returned from cleanup_get_value()
    value: str
        (str) returned from cleanup_get_value() describing codes list
    dictionary: dict
        dictionary of id value pair.
        {'id': 'json parse', ...}
    code: str
        original course code the pre-requisite 
    
    Returns
    ----------
    codes: list
        returns original codes list if no further parsing is required
        updated codes list if parsed value for id is present in dictionary
        updated codes list by calling parse() again for the unparsed group / id
    """

    if value == 'no pre' or value == 'single pre':
        return codes  # no checks required, height = 0
    else:
        if 'groups' in codes[0]:
            # iterate through the list of groups
            for index, x in enumerate(codes[0]['groups']):
                if isinstance(x, dict):
                    # nested groups are possible, hence check if group's group has unparsed id
                    codes[0]['groups'][index] = return_routine([x], value, dictionary, code)[0]
                elif x in dictionary:  # x is (str) and is also a key of the dictionary
                    if isinstance(dictionary[codes[0]['groups'][index]], list):  # value for x is parsed json in dictionary
                        codes[0]['groups'][index] = dictionary[codes[0]['groups'][index]][0]
                    else:  # value for x is (str) in dictionary and needs to be parsed
                        codes[0]['groups'][index] = parse(dictionary[codes[0]['groups'][index]][1:-1], code)[0]
                else:
                    pass
        return codes  # everything on this height and height above is parsed

def parse(str_, code):
    """
    Parses pre-requisite string

    Attributes
    ----------
    line: str
        pre-requisite string
    code: str
        original course code the pre-requisite or substring of it

    Returns
    ----------
    output from return_routine
    """

    dictionary = {}  # stores id value pair

    matchObj, str_ = group_extraction(str_, code)
    dictionary.update(matchObj)

    # brackets / groups at the current height are identified as ids in group_extraction
    # if they still remain, there is an error 
    if len(re.findall(r'[\]\[\)\)]', str_)) > 0:
        print('ERROR bracket', code, matchObj, str_)
        exit()

    logic = get_and_or(str_)  # logic to connect ids A and B, A or B?

    # regex list
    numReg = r'(\d{1,}\.?\d{0,3})'  # identify number
    codeMatch = r'((\w{2,4}\*\d{2,4}(\/2)?)|(([A-Z]|\d){8}))'  # identify course code | placeholder id
    codeList = '(^ )?' + codeMatch + "((\s?,?\s?)" + codeMatch + ")*(?=(,|$|\.|( or )|))(?!( or equivalent))"  # identify "list" of codes
    codeListNoEnd = '^' + codeMatch + r"((\s?,?\s?)" + codeMatch + r")*"  # identify "list" of codes with no end - will match everything

    creditMatch = r'(?<!of )' + numReg + ' credits(?!((,? in)|( from)|( of)|( at)))'  # match "n credits" with no "in, from, of, at" after it
    creditsInMatch = numReg + r' credits (in|of|at) .+?((?= or )|(?= from )|(?=,)|$)'  # match "n credits in "
    creditsIncludingX = numReg + ' credits(,)? including ' + codeList  # match "n credits including code, code, ..."
    listAnd = '(^ )?' + codeListNoEnd + ',? and ' + codeMatch + '(?=(,|$|\.| |))'  # match "code and code"
    listOr = '(^ )?' + codeListNoEnd + ',? or ' + codeMatch + '(?=(,|$|\.| |))'  # match "code or code"
    creditsIncludingXorY = numReg + ' credits(,)? including ' + codeMatch + ' or ' + codeMatch  # match "n credits including code or code"
    creditsInIncluding = numReg + ' credits in .*,? including ' + codeMatch  # match "n credits in subject including code"

    matchObj, str_ = choose_n_from_course_list(str_, codeList, codeMatch)
    dictionary.update(matchObj)

    matchObj, str_ = credits_in_subject_Including(str_, creditsInIncluding)
    dictionary.update(matchObj)

    matchObj, str_ = credits_including_X_or_Y(str_, creditsIncludingXorY)
    dictionary.update(matchObj)

    matchObj, str_ = credits_including_X(str_, creditsIncludingX)
    dictionary.update(matchObj)

    matchObj, str_ = credit_match(str_, creditMatch)
    dictionary.update(matchObj)

    matchObj, str_ = credits_in_subject(str_, creditsInMatch)
    dictionary.update(matchObj)

    matchObj, str_ = implied_and(str_, codeList, codeMatch)
    dictionary.update(matchObj)

    matchObj, str_ = explicit_and(str_, listAnd)
    dictionary.update(matchObj)

    matchObj, str_ = explicit_or(str_, listOr)
    dictionary.update(matchObj)

    check_missing_conditions(str_, dictionary)
    check_code_present(str_, codeMatch)

    codes, value = cleanup_get_value(str_, codeMatch, dictionary)
    return return_routine(codes, value, dictionary, code)

def createJSON(groupName):
    """
    Creates JSON file of pre-requisites

    Attributes
    ----------
    groupName: str
        (str) used in regex to match specific course code pattern
        if '' then matches all courses
    """

    # r -> raw, f -> f-strings
    # re.I ignores case
    code = re.compile(rf"{groupName}\*", re.I)

    # find document where school is guelph and code has a * in it, * as a safety check for the parser 
    # TODO: improve safety check by checking the the specific pattern
    # pymongo.cursor.Cursor
    all_courses_iterator = collection.find({'School': 'Guelph', 'Code': { '$regex': code }})
    
    courseMapPre = {}
    courseMapExc = {} # TODO: take restrictions into account
    for course in all_courses_iterator:
        pre = course['Prerequisites'] if 'Prerequisites' in course else ""  # if pre-requisites exist, get them

        # if parsing is known to be incorrect get the fix
        if course['Code'] in preFixes:
            pre = preFixes[course['Code']]
        
        print('course: ', course['Code'])
        courseMapPre[course['Code']] = parse(pre, course['Code'])
        print('parsed: ', courseMapPre[course['Code']])
    
    with open('./parsed/all.json', 'w') as outfile:
        json.dump({'prerequisites': courseMapPre, 'restrictions': courseMapExc}, outfile)

if __name__ == '__main__':
    createJSON('') # iterates through all courses

