const express = require('express')
const cookieParser = require('cookie-parser')

const MongoClient = require('mongodb').MongoClient
const url = 'mongodb://localhost:27017/'

const app = express()
app.use(express.static('dist'))
app.use(express.json())
app.use(express.urlencoded())
app.use(cookieParser())

app.get('/api/test', (req, res) => {
  res.send('Hello world')
})

app.get('/api/load', (req, res) => {

})

app.get('/api/query', function (req, res) {
  res.setHeader('Content-type', 'application/json')
  res.send([])
})

app.get('/api/query/:query', function (req, res) {
  res.setHeader('Content-type', 'application/json')
  const school = 'Guelph'

  MongoClient.connect(url, function (err, client) {
    if (err) {
      console.log('Unable to connect to the mongoDB server. Error:', err)
    } else {
      const db = client.db('scheduler')
      var collection = db.collection('cachedData')

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

      const searchRegexCode = new RegExp(`(${safeQueryCode})`, 'gi')
      const searchRegex = new RegExp(`(${safeQuery})`, 'gi')

      collection.find(
        {
          School: school,
          $or: [
            { Code: { $regex: searchRegexCode } },
            { Name: { $regex: searchRegex } }
          ]
        }
      ).limit(10).toArray((err, docs) => {
        client.close()
        res.end(JSON.stringify(docs))
      })
    }
  })
})


app.listen(8085, () => console.log('Listening on port 8085!'))
