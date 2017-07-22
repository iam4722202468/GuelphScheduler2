var express = require('express');
var router = express.Router();
var ejs = require('ejs');
var fs = require('fs');
var PythonShell = require('python-shell');

var baseFilePath = '/../html/'

var mongodb = require('mongodb'),
    MongoClient = mongodb.MongoClient,
    url = 'mongodb://localhost:27017/scheduler';

var exec = require('child_process').execFile;

function generateHash()
{
	var hash = "";
	for(var x = 0; x <= 9; x++)
	{
		currentChar = Math.floor(Math.random() * 36);
		if(currentChar > 9)
		{
			hash += String.fromCharCode(currentChar + 55);
		} else {
			hash += currentChar;
		}
		
		if(x == 9)
			return hash;
	}
}

function checkDatabase(checkFor, callback_)
{
    if (checkFor !== undefined && typeof checkFor == "string")
    {
        MongoClient.connect(url, function (err, db) {
            if (err)
                console.log('Unable to connect to the mongoDB server. Error:', err);
            else {
                var collection = db.collection('cachedData');
                
                // 80% sure this is safe
                collection.find({"Code": checkFor.toUpperCase()}).limit(2).toArray(function(err, docs){
                    if (docs.length == 2 || docs.length == 0)
                    {
                        db.close();
                        callback_(null);
                    } else {
                        db.close();
                        callback_(docs[0]);
                    }
                });
            }
        });
    } else {
        callback_(null);
    }
}

function addBlock(blockString, sessionID, callback_)
{
    //add block and delete it after every use instead of modifying it
    MongoClient.connect(url, function (err, db) {
        if (err)
            console.log('Unable to connect to the mongoDB server. Error:', err);
        else {
            var collection = db.collection('blockedTimes');
            
            blockString = JSON.parse(blockString);
            blockString['sessionID'] = sessionID;
            
            collection.remove({'sessionID': sessionID}, function(err, result) {
                collection.insert(blockString, function(err, records){
                    callback_();
                    db.close();
                });
            });
        }
    });
}

function getBlock(sessionID, callback_)
{
    MongoClient.connect(url, function (err, db) {
        if (err)
            console.log('Unable to connect to the mongoDB server. Error:', err);
        else {
            var collection = db.collection('blockedTimes');
            
            collection.find({"sessionID": sessionID}).toArray(function(err, docs){
                if (docs.length > 0)
                {
                    db.close();
                    callback_(docs[0]);
                } else {
                    db.close();
                    callback_(null);
                }
            });
        }
    });
}

function addCriteria(criteriaString, sessionID, callback_)
{
    MongoClient.connect(url, function (err, db) {
        if (err)
            console.log('Unable to connect to the mongoDB server. Error:', err);
        else {
            var collection = db.collection('criteria');
            
            criteriaString = JSON.parse(criteriaString);
            criteriaString['sessionID'] = sessionID;
            
            collection.remove({'sessionID': sessionID}, function(err, result) {
                collection.insert(criteriaString, function(err, records){
                    callback_();
                    db.close();
                });
            });
        }
    });
}

function getCriteria(sessionID, callback_)
{
    MongoClient.connect(url, function (err, db) {
        if (err)
            console.log('Unable to connect to the mongoDB server. Error:', err);
        else {
            var collection = db.collection('criteria');
            
            collection.find({"sessionID": sessionID}).toArray(function(err, docs){
                if (docs.length > 0)
                {
                    db.close();
                    callback_(docs[0]);
                } else {
                    db.close();
                    callback_(null);
                }
            });
        }
    });
}

function checkSession(cookie, callback_)
{
    MongoClient.connect(url, function (err, db) {
        if (err)
            console.log('Unable to connect to the mongoDB server. Error:', err);
        else {
            var collection = db.collection('userData');
            
            collection.find({"sessionID": cookie}).toArray(function(err, docs){
                if (docs.length > 0)
                {
                    db.close();
                    callback_({"Value" : 1, "Courses" : docs[0]['Data']});
                } else {
                    db.close();
                    callback_({"Value" : 0});
                }
            });
        }
    });
}

router.get('/', function(req, res) {
    if(!("sessionID" in req.cookies)) {
        res.cookie('sessionID', generateHash(), {expires: new Date(2147483647000)});
    }
    
    ejs.renderFile(__dirname + baseFilePath + 'index.html', {}, function(err, result) {
        if (!err) {
            res.end(result);
        } else {
            res.end(err.toString());
            console.log(err);
        }
    });
});

function runAlgorithm(sessionID, start, end, callback_)
{
    // get schedules 0 to 9
    // add another argument here for weight of schedules when rating
    //a = '{"Sections" : [ { "Meeting_Section" : "NA", "Enrollment" : "NA", "Instructors" : "NA", "Offerings" : [ { "Time_Start" : "1430", "Section_Type" : "BLOCK", "Time_End" : "1530", "Course" : "BLOCK", "Location" : "BLOCK", "Day" : "Tues, Thur" }]}]}'
    
    exec('../searchAlgorithm/generate',[sessionID, start.toString(), end.toString()], {maxBuffer:1028*1000}, function(err, data) {  
        console.log(err);
        callback_(data.toString());                       
    });
}

router.post('/getInfo', function(req,res) {
    res.setHeader('Content-type', 'application/json');
    
    checkDatabase(req.body.Code, function(isFound) {
        if (isFound!== null) {
            res.end(JSON.stringify(isFound));
        } else {
            res.end('{"error" : "Course not found"}');
        }
    });
});

function addClasses(classArray, callback_)
{
    toAdd = classArray.slice(0,1);
    classArray = classArray.slice(1,classArray.length);
    
    PythonShell.run('./main.py', {args:[sessionID].concat(toAdd)}, function(err, outputArray) {
        if (classArray.length == 0)
            callback_();
        else
            addClasses(classArray, function(done) {
                callback_();
            });
    });
}

router.post('/reload', function(req,res) {
    res.setHeader('Content-type', 'application/json');
    sessionID = req.cookies.sessionID;
    
    checkSession(sessionID, function(isFound) {
        if (isFound['Value'] == 1) {
            
            addArray = []
            for (x in isFound['Courses'])
            {
                deleteClass(isFound['Courses'][x]['Course']['Course'], sessionID, function(isFound) {});
                addArray.push(isFound['Courses'][x]['Course']['Course']);
                
                if (x == isFound['Courses'].length - 1)
                {
                    addClasses(addArray, function(done) {
                        res.end('{"success" : "No problems"}');
                    });
                }
            }
        } else {
            res.end('{"error" : "SessionID not found"}');
        }
    });
});

router.post('/getSchedules', function(req,res) {
    res.setHeader('Content-type', 'application/json');
    sessionID = req.cookies.sessionID;
    
    checkSession(sessionID, function(isFound) {
        if (isFound['Value'] == 1 && !isNaN(req.body.start) && !isNaN(req.body.end)) {
            runAlgorithm(sessionID, req.body.start, req.body.end, function(toReturn) {
                if (toReturn.indexOf("null") != 0)
                    res.end('{"course":' + JSON.stringify(isFound) + ', "schedules":' + toReturn + '}');
                else
                {
                    checkSession(sessionID, function(courseData) {
                        noSchedules(courseData, function(data) {
                            res.end(data);
                        });
                    });
                }
            });
        } else res.end('{"error" : "SessionID not found"}');
    });
});

function noSchedules(isFound, callback_)
{
    objectArray = [];
    
    if (isFound['Courses'].length == 0)
        callback_('{"error" : "No courses"}');
    
    for (x in isFound['Courses'])
    {
        object = {}
        
        object['Num_Credits'] = isFound['Courses'][x]['Course']['Num_Credits']
        object['Name'] = isFound['Courses'][x]['Course']['Name']
        object['Level'] = isFound['Courses'][x]['Course']['Level']
        object['Code'] = isFound['Courses'][x]['Course']['Course']
        
        objectArray.push(object);
        
        if (x == isFound['Courses'].length-1)
            callback_('{"error" : "No schedules exist", "schedules" : ' + JSON.stringify(objectArray) + '}');
    }
}

router.post('/init', function(req,res) {
    res.setHeader('Content-type', 'application/json');
    sessionID = req.cookies.sessionID;
    
    checkSession(sessionID, function(isFound) {
        if (isFound['Value'] == 1) {
            
            getBlock(sessionID, function(blockData) {
                
                if (blockData === null)
                    blockData = JSON.parse('{"Offerings" : []}');
                
                runAlgorithm(sessionID, 0, 9, function(toReturn) {
                    if (toReturn.indexOf("null") != 0) {
                        res.end('{"course":"null", "schedules":' + toReturn + ', "blocks":' + JSON.stringify(blockData) + '}');
                    } else {
                        noSchedules(isFound, function(data) {
                            data = JSON.parse(data);
                            data['blocks'] = blockData;
                            data = JSON.stringify(data);
                            
                            res.end(data);
                        });
                    }
                });
            });
        } else {
            res.end('{"error" : "SessionID not found"}');
        }
    });
});

function deleteClass(courseCode, sessionID, callback_)
{
    MongoClient.connect(url, function (err, db) {
        if (err)
            console.log('Unable to connect to the mongoDB server. Error:', err);
        else {
            var collection = db.collection('userData');
            
            collection.find({"sessionID": sessionID}).toArray(function(err, docs){
                if (docs.length > 0)
                {
                    for (x in docs[0]['Data'])
                        if (docs[0]['Data'][x]['Course']['Course'] == courseCode)
                            collection.update({"sessionID": sessionID}, {$pull: {'Data':docs[0]['Data'][x]}});
                    
                    db.close();
                    callback_(1);
                } else {
                    db.close();
                    callback_(0);
                }
            });
        }
    });
}

router.post('/delete', function(req,res) {
    res.setHeader('Content-type', 'application/json');
    sessionID = req.cookies.sessionID;
    
    deleteClass(req.body.Code, sessionID, function(isFound) {
        if (isFound == 1) {
            res.end('{"success" : "done"}');
        } else { 
            res.end('{"error" : "Course not found"}');
        }
    });
});

router.post('/updateBlock', function(req,res) {
    res.setHeader('Content-type', 'application/json');
    sessionID = req.cookies.sessionID;
    
    //check for days                        Day
    //start time (int between 700 and 2400) Time_Start
    //end time (int between 700 and 2400)   Time_End
    
    safeObject = {'Offerings':[]}
    
    for (x in req.body['Offerings'])
    {
        if (!('Time_Start' in req.body['Offerings'][x])) continue;
        if (!('Day' in req.body['Offerings'][x])) continue;
        if (!('Time_End' in req.body['Offerings'][x])) continue;
        if (req.body['Offerings'][x]['Day'] == "") continue;
        if (!(parseInt(req.body['Offerings'][x]['Time_Start']) <= 2300)) continue;
        if (!(parseInt(req.body['Offerings'][x]['Time_Start']) >= 700)) continue;
        if (!(parseInt(req.body['Offerings'][x]['Time_End']) <= 2300)) continue;
        if (!(parseInt(req.body['Offerings'][x]['Time_End']) >= 700)) continue;
        
        safeObjectTemp = {}
        safeObjectTemp['Time_Start'] = req.body['Offerings'][x]['Time_Start']
        safeObjectTemp['Time_End'] = req.body['Offerings'][x]['Time_End']
        safeObjectTemp['Day'] = req.body['Offerings'][x]['Day']
        
        safeObject['Offerings'].push(safeObjectTemp)
    }
    
    addBlock(JSON.stringify(safeObject), sessionID, function() {
        res.end('{"Success":"true"}');
    });
    
});

router.post('/updateCriteria', function(req,res) {
    res.setHeader('Content-type', 'application/json');
    sessionID = req.cookies.sessionID;
    
    working = true;
    
    if (req.body["Criteria"]["Weight"].length == 6 &&
        req.body["Criteria"]["Direction"].length == 6) {
            
        for (x in [0,1,2,3,4,5]) {
            if (!(parseInt(req.body["Criteria"]["Weight"][x]) in [0,1,2,3,4,5,6,7,8,9] &&
                parseInt(req.body["Criteria"]["Direction"][x]) in [0,1])) {
                
                working = false;
                break;
            }
        }
    } else {
        working = false;
    }
    
    if (working) {
        addCriteria(JSON.stringify(req.body["Criteria"]), sessionID, function() {
            res.end('{"Success":"true"}');
        });
    } else
        res.end('{"error":"criteria inputted incorrectly"}');
    
});

router.post('/add', function(req,res) {
    res.setHeader('Content-type', 'application/json');
    
    sessionID = req.cookies.sessionID;
    
    console.log(req.body.Code);
    
    checkDatabase(req.body.Code, function(isFound) {
        if (isFound!== null) {
            PythonShell.run('./main.py', {args:[sessionID, req.body.Code]}, function(err, outputArray) {
                if (err) throw err;
                
                console.log (outputArray)
                
                if(outputArray !== null)
                {
                    if (outputArray[1] == "1")
                    {
                        res.end('{"error" : "' + outputArray[0] + '"}');
                    } else {
                        res.end('{"success" : "done", "course":' + JSON.stringify(isFound) + '}');
                    }
                }
                else
                    res.end('{"error" : "Problem with python parser"}');
            });
        } else {
            res.end('{"error" : "Course not found"}') 
        };
    });
});

router.get('/searchClass/:query', function(req, res) {
    res.setHeader('Content-type', 'application/json');
    
    MongoClient.connect(url, function (err, db) {
        if (err)
            console.log('Unable to connect to the mongoDB server. Error:', err);
        else {
            var collection = db.collection('cachedData');
            collection.find({"Code": { "$regex": "^" + req.params.query.toUpperCase().replace(/\\/g, "\\\\").replace(/\*/g, "\\*").replace(/\$/g, "\\$").replace(/'/g, "\\'").replace(/"/g, "\\\"")}}, { Num_Credits: 1, Code: 1, Level: 1, Campus: 1, Name: 1}).limit(10).toArray(function(err, docs){
                if (docs.length == 0)
                {
                    collection.find({"Name": { "$regex": "\W*((?i)" + req.params.query.toUpperCase().replace(/\\/g, "\\\\").replace(/\*/g, "\\*").replace(/\$/g, "\\$").replace(/'/g, "\\'").replace(/"/g, "\\\"") + "(?-i))\W*"}}, { Num_Credits: 1, Code: 1, Level: 1, Campus: 1, Name: 1}).limit(10).toArray(function(err, docs){
                        db.close();
                        res.end(JSON.stringify(docs));
                    });
                }
                else
                {
                    db.close();
                    res.end(JSON.stringify(docs));
                }
            });
        }
    });
});

module.exports = router;
