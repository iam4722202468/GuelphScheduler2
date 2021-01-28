const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');

/*
 * Requires the MongoDB Node.js Driver
 * https://mongodb.github.io/node-mongodb-native
 */

const agg = [
  {
    '$match': {
      'ts': {
        '$gte': new Date('Tue, 18 Aug 2020 00:00:00 GMT')
      }
    }
  }, {
    '$project': {
      'Code': 1, 
      'ts': 1, 
      'Remaining': {
        '$subtract': [
          '$Total', '$Remaining'
        ]
      }
    }
  }, {
    '$sort': {
      'Remaining': -1
    }
  }, {
    '$group': {
      '_id': '$Code', 
      'allObj': {
        '$push': {
          'ts': '$ts', 
          'remaining': '$Remaining'
        }
      }, 
      'maxObj': {
        '$first': {
          'max': '$Remaining', 
          'ts': '$ts'
        }
      }
    }
  }, {
    '$unwind': {
      'path': '$allObj'
    }
  }, {
    '$sort': {
      'allObj.remaining': 1
    }
  }, {
    '$group': {
      '_id': '$_id', 
      'allObj': {
        '$push': {
          'ts': '$allObj.ts', 
          'remaining': '$allObj.remaining'
        }
      }, 
      'maxObj': {
        '$first': '$maxObj'
      }
    }
  }, {
    '$unwind': {
      'path': '$allObj'
    }
  }, {
    '$sort': {
      'allObj.ts': -1
    }
  }, {
    '$group': {
      '_id': '$_id', 
      'maxObj': {
        '$first': '$maxObj'
      }, 
      'minObj': {
        '$first': '$allObj'
      }
    }
  }, {
    '$match': {
      'maxObj.max': {
        '$ne': 0
      }
    }
  }, {
    '$project': {
      'min': '$minObj.remaining', 
      'max': '$maxObj.max'
    }
  }, {
    '$project': {
      'min': 1, 
      'max': 1, 
      'change': {
        '$subtract': [
          '$min', '$max'
        ]
      }, 
      'percent': {
        '$subtract': [
          1, {
            '$divide': [
              '$min', '$max'
            ]
          }
        ]
      }
    }
  }, {
    '$sort': {
      'percent': -1
    }
  }, {
    '$match': {
      'change': {
        '$lte': -2
      }, 
      'min': {
        '$gte': 1
      }
    }
  }
]

MongoClient.connect(
  'mongodb://192.168.0.15:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false',
  { useNewUrlParser: true, useUnifiedTopology: true },
  async function(connectErr, client) {
    assert.equal(null, connectErr);
    const coll = client.db('scheduler').collection('registrationData');
    const cursor = coll.aggregate(agg,{allowDiskUse: true});

    await cursor.toArray((err, res) => {
      console.log(res)
      require('fs').writeFile(

    './percent.json',

    JSON.stringify(res),

    function (err) {
        if (err) {
            console.error('Crap happens');
        }
    }
);


    });

    // client.close();
  });
