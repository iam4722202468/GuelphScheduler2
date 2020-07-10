var express = require('express');
var router = express.Router();
var fs = require('fs');
var path = require('path');

const { PythonShell } = require('python-shell');

var mongodb = require('mongodb'),
  MongoClient = mongodb.MongoClient,
  url = 'mongodb://localhost:27017/scheduler';

var exec = require('child_process').execFile;

function generateHash() {
  let hash = "";
  for (let x = 0; x <= 9; x++) {
    currentChar = Math.floor(Math.random() * 36);
    if (currentChar > 9) {
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
    MongoClient.connect(url, function (err, client) {
      if (err)
        console.log('Unable to connect to the mongoDB server. Error:', err);
      else {
        const db = client.db('scheduler');
        var collection = db.collection('cachedData');
        
        // 80% sure this is safe
        collection.find({"Code": checkFor.toUpperCase()})
          .limit(2)
          .toArray(function(err, docs){
          if (docs.length == 2 || docs.length == 0)
          {
            client.close();
            callback_(null);
          } else {
            client.close();
            callback_(docs[0]);
          }
        });
      }
    });
  } else {
    callback_(null);
  }
}

function getSections(checkFor, callback_)
{
  if (checkFor !== undefined && typeof checkFor == "string") {
    MongoClient.connect(url, function (err, client) {
      if (err)
        console.log('Unable to connect to the mongoDB server. Error:', err);
      else {
        const db = client.db('scheduler');
        var collection = db.collection('cachedCourses');
        
        // 80% sure this is safe
        collection.find({"Course": checkFor.toUpperCase()})
          .limit(2)
          .toArray(function(err, docs){
          if (docs.length == 2 || docs.length == 0)
          {
            client.close();
            callback_(null);
          } else {
            client.close();
            callback_(docs[0].Data.Sections);
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
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('blockedTimes');
      
      blockString = JSON.parse(blockString);
      blockString['sessionID'] = sessionID;
      
      collection.remove({'sessionID': sessionID}, function(err, result) {
        collection.insert(blockString, function(err, records){
          callback_();
          client.close();
        });
      });
    }
  });
}

function getSelectedSections(sessionID, callback_)
{
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('sections');
      
      collection.find({"sessionID": sessionID}).toArray(function(err, docs){
        if (docs.length > 0)
        {
          client.close();
          callback_(docs[0]);
        } else {
          client.close();
          callback_(null);
        }
      });
    }
  });
}

function getBlock(sessionID, callback_)
{
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('blockedTimes');
      
      collection.find({"sessionID": sessionID}).toArray(function(err, docs){
        if (docs.length > 0)
        {
          client.close();
          callback_(docs[0]);
        } else {
          client.close();
          callback_(null);
        }
      });
    }
  });
}

function addCriteria(criteriaList, sessionID, callback_)
{
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('criteria');
      var criteriaString = {};

      criteriaString['data'] = criteriaList;
      criteriaString['sessionID'] = sessionID;
      
      collection.remove({'sessionID': sessionID}, function(err, result) {
        collection.insert(criteriaString, function(err, records){
          callback_();
          client.close();
        });
      });
    }
  });
}

function getCriteria(sessionID, callback_) {
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('criteria');
      
      collection.find({"sessionID": sessionID}).toArray(function(err, docs){
        if (docs.length > 0)
        {
          client.close();
          callback_(docs[0]);
        } else {
          client.close();
          callback_(null);
        }
      });
    }
  });
}

function checkSession(cookie, callback_) {
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('userData');
      
      collection.find({"sessionID": cookie}).toArray(function(err, docs){
        if (docs.length > 0)
        {
          client.close();
          callback_({"Value" : 1, "Courses" : docs[0]['Data']});
        } else {
          client.close();
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
  
  res.sendFile(path.resolve('public/html/index.html'))
});

function runAlgorithm(sessionID, callback_)
{
  // get schedules 0 to 9
  // add another argument here for weight of schedules when rating
  //a = '{"Sections" : [ { "Meeting_Section" : "NA", "Enrollment" : "NA", "Instructors" : "NA", "Offerings" : [ { "Time_Start" : "1430", "Section_Type" : "BLOCK", "Time_End" : "1530", "Course" : "BLOCK", "Location" : "BLOCK", "Day" : "Tues, Thur" }]}]}'
  
  exec('../searchAlgorithm/generate',[sessionID], {maxBuffer:1028*1000}, function(err, data) {  
    console.log(err);
    callback_(data.toString());             
  });
}

router.post('/getInfo', function(req,res) {
  res.setHeader('Content-type', 'application/json');
  
  checkDatabase(req.body.Code, function(isFound) {
    if (isFound!== null) {
      getSections(req.body.Code, (sections) => {
        isFound.Sections = sections
        res.end(JSON.stringify(isFound));
      })
    } else {
      res.end('{"error" : "Course not found"}');
    }
  });
});


/*function addClasses(classArray, callback_)
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
}*/

/*router.post('/reload', function(req,res) {
  res.setHeader('Content-type', 'application/json');
  sessionID = req.cookies.sessionID;
  
  checkSession(sessionID, function(isFound) {
    if (isFound['Value'] == 1) {
      
      addArray = []
      
      for (x in isFound['Courses'])
      {
        deleteClass(isFound['Courses'][x], sessionID, function(isFound) {});
        addArray.push(isFound['Courses'][x]);
        
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
});*/

router.post('/getSchedules', function(req,res) {
  res.setHeader('Content-type', 'application/json');
  sessionID = req.cookies.sessionID;
  
  checkSession(sessionID, function(isFound) {
    if (isFound['Value'] == 1) {
      runAlgorithm(sessionID, function(toReturn) {
        if (toReturn.indexOf("null") != 0)
        {
          let parsedRes = JSON.parse(toReturn);
          let data = {};
          data['course'] = isFound;
          data['schedules'] = parsedRes.results;
          data['searchSpace'] = parsedRes.searchSpace;

          res.end(JSON.stringify(data))
        }
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

/* make a list of schedules to show on right if none are generates */
function noSchedules(isFound, callback_) {
  objectArray = [];
  
  if (isFound && isFound['Courses'] && isFound['Courses'].length == 0)
    callback_('{"error" : "No courses"}');
  
  callback_('{"error" : "No schedules exist", "schedules" : ' + JSON.stringify(isFound['Courses']) + '}');
}

router.post('/init', function(req,res) {
  res.setHeader('Content-type', 'application/json');
  sessionID = req.cookies.sessionID;
  
  checkSession(sessionID, function(isFound) {
    if (isFound['Value'] == 1) {
      
      getBlock(sessionID, function(blockData) {
        getSelectedSections(sessionID, (sections) => {
          if (blockData === null)
            blockData = JSON.parse('{"Offerings" : []}');

          if (sections === null)
            sections = {}
          else
            sections = sections.sections
          
          runAlgorithm(sessionID, function(toReturn) {
            if (toReturn.indexOf("null") != 0) {
              let parsedRes = JSON.parse(toReturn);
              data = {};
              data['course'] = null;
              data['schedules'] = parsedRes.results;
              data['blocks'] = blockData;
              data['sections'] = sections;
              data['searchSpace'] = parsedRes.searchSpace;

              data = JSON.stringify(data);

              res.end(data)
            } else {
              noSchedules(isFound, function(data) {
                data = JSON.parse(data);
                data['blocks'] = blockData;
                data['sections'] = sections;
                data['searchSpace'] = 0;
                data = JSON.stringify(data);
                
                res.end(data);
              });
            }
          });
        });
      });
    } else {
      res.end('{"error" : "SessionID not found"}');
    }
  });
});

function deleteClass(courseCode, sessionID, callback_) {
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('userData');
      
      collection.find({"sessionID": sessionID}).toArray(function(err, docs){
        if (docs.length > 0)
        {
          for (x in docs[0]['Data'])
            if (docs[0]['Data'][x] == courseCode)
              collection.update({"sessionID": sessionID}, {$pull: {'Data':docs[0]['Data'][x]}});
          
          client.close();
          callback_(1);
        } else {
          client.close();
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
  
  //check for days            Day
  //start time (int between 700 and 2400) Time_Start
  //end time (int between 700 and 2400)   Time_End
  
  safeObject = {'Offerings':[]}
  
  for (x in req.body['Offerings'])
  {
    // Validate data
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

function validateSections(sectionData) {
  if (typeof sectionData != "object")
    return false;

  if (Object.keys(sectionData).length > 20)
    return false;

  for (course in sectionData) {
    if (typeof course != "string")
      return false;
    if (course.length > 10)
      return false;

    if (typeof sectionData[course] != "object")
      return false;

    for (section in sectionData[course]) {
      if (typeof sectionData[course][section] != "string")
        return false;

      if (sectionData[course][section].length > 10)
        return false;
    }
  }

  return true;
}

function updateSections(sessionID, newSections, callback_) {
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('sections');
      
      collection.update(
        { "sessionID": sessionID },
        {
          "sessionID": sessionID,
          "sections": newSections
        },
        { upsert: true }
      ).then(() => {
        client.close()
      })
    }
  });
}

router.post('/updateSections', function(req,res) {
  res.setHeader('Content-type', 'application/json');
  sessionID = req.cookies.sessionID;

  if (validateSections(req.body)) {
    updateSections(sessionID, req.body)
    res.end('{"done":"success"}')
  } else {
    res.end('{"error":"invalid sections object"}')
  }
});

router.post('/updateCriteria', function(req,res) {
  res.setHeader('Content-type', 'application/json');
  sessionID = req.cookies.sessionID;

  if (req.body["Criteria"].filter(x => !isNaN(parseInt(x))).length === 2) {
    addCriteria(req.body["Criteria"], sessionID, function() {
      res.end('{"Success":"true"}');
    });
  } else
    res.end('{"error":"criteria inputted incorrectly"}');
  
});

router.post('/add', function(req,res) {
  res.setHeader('Content-type', 'application/json');
  
  sessionID = req.cookies.sessionID;
  courseCode = req.body.Code.toUpperCase();
  
  console.log("Adding " + courseCode);
  
  checkDatabase(courseCode, function(isFound) {
    console.log("Found: " + isFound)
    
    if (isFound!== null) {
      var school = "Guelph";
      
      const options = {
        pythonPath: '/usr/bin/python3',
        args: [ sessionID, courseCode, school ]
      }

      PythonShell.run(
        './src/main.py',
        options,
        (err, outputArray) => {
        if(!err && outputArray !== null) {
          console.log(outputArray);
          
          if (outputArray[1] == "1")
            res.end('{"error" : "' + outputArray[0] + '"}');
          else {
            getSections(courseCode, (sections) => {
              isFound.Sections = sections;
              res.end('{"success" : "done", "course":' + JSON.stringify(isFound) + '}');
            })
          }
        } else {
          console.log(err);
          res.end('{"error" : "Problem with python parser"}');
        }
      });
    } else {
      res.end('{"error" : "Course not found"}') 
    };
  });
});

router.get('/searchClass/:query', function(req, res) {
  res.setHeader('Content-type', 'application/json');
  
  const school = "Guelph"
  
  MongoClient.connect(url, function (err, client) {
    if (err)
      console.log('Unable to connect to the mongoDB server. Error:', err);
    else {
      const db = client.db('scheduler');
      var collection = db.collection('cachedData');
      
      const safeQuery = req.params.query
        .replace(/\*/g, '\\\*')
        .replace(/\'/g, '\\\'')
        .replace(/\$/g, '\\\$')
        .replace(/\(/g, '\\\(')
        .replace(/\)/g, '\\\)')
        .replace(/\+/g, '\\\+')
        .replace(/\]/g, '\\\]')
        .replace(/\[/g, '\\\[')

      const safeQueryCode = safeQuery.replace(/\ /, '\\\*')

      const searchRegexCode = new RegExp(`(${safeQueryCode})`, 'gi');
      const searchRegex = new RegExp(`(${safeQuery})`, 'gi');

      collection.find(
        {
          School: school,
          $or: [
            { Code: { $regex: searchRegexCode } },
            { Name: { $regex: searchRegex } }
          ]
        }
      ).limit(10).toArray((err, docs) => {
        client.close();
        res.end(JSON.stringify(docs));
      });
    }
  });
});

module.exports = router;
