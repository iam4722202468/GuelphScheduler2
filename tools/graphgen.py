import json
import random
from graphviz import Digraph
import graphparse

groupName = ""

graphparse.createJSON(groupName)

path = './parsed/' + groupName + '.json'

def traverse(obj, oldColors):
    colors = oldColors.copy()
    type = obj['type']

    res = []

    if type == 'CREDITS':
        return []

    if type == 'AND' and len(oldColors) == 0:
        color = "#000000"
    else:
        r = hex(int(random.uniform(100,200)))[2:]
        g = hex(int(random.uniform(100,200)))[2:]
        b = hex(int(random.uniform(100,200)))[2:]
        color = "#" + r + g + b

    colors.append(color)

    for subObj in obj['groups']:
        if isinstance(subObj, str):
            res.append([ subObj, colors ])
        else:
            res += traverse(subObj, colors)

    return res
            
def traverseArr(obj, colors):
    res = []
    for x in obj:
        res += traverse(x, colors)

    for x in res:
        if len(x[1]) > 1 and x[1][0] == '#000000':
            # Remove preceding 0's
            nonZero = -1
            for y in range(0, len(x[1])):
                if x[1][y] != "#000000":
                    nonZero = y
                    break

            if nonZero == -1:
                x[1] = [0]
            else:
                x[1] = x[1][y:]

    return res

with open(path, "r") as read_file:
    data = json.load(read_file)

headings = list(data['prerequisites'].keys())
s = len(headings)

edges = [[[] for x in range(s)] for y in range(s)] 

for x in data['prerequisites']:
    res = traverseArr(data['prerequisites'][x], [])
    mainFound = headings.index(x)

    for y in res:
        code = y[0]
        val = y[1]

        try:
            found = headings.index(code)
            edges[mainFound][found] = val
        except:
            None

for x in data['restrictions']:
    res = traverseArr(data['restrictions'][x], [])
    mainFound = headings.index(x)

    for y in res:
        code = y[0]
        val = y[1]

        try:
            found = headings.index(code)

            if edges[found][mainFound] == [] and found != mainFound:
                edges[mainFound][found] = ["#ff0000"]
        except:
            None

dot = Digraph(engine='sfdp')

for i,x in enumerate(edges):
    for j,y in enumerate(x):
        if y != []:
            if (y[0] == "#ff0000"):
                dot.edge(headings[j], headings[i], color="#ff0000", arrowhead="none")
            else:
                dot.edge(headings[j], headings[i], color=":".join(y))

print(dot.source)
dot.render('./generated/all')
