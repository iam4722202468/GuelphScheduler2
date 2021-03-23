const express = require('express')
const cookieParser = require('cookie-parser')

const MongoClient = require('mongodb').MongoClient
const url = 'mongodb://localhost:27017/'

const app = express()
app.use(express.static('dist'))
app.use(express.json())
app.use(express.urlencoded())
app.use(cookieParser())

app.get('/api/load', (req, res) => {
  res.send('{message:\'ok\'}')
})

app.post('/api/generate', (req, res) => {
  const toSchedule = req.body.future // ["CIS*3760", "CIS*1910", "STAT*2040", "ACCT*3340", "ACCT*2220", "ECON*2770", "AGR*2350", "NUTR*4040"]
  const ignoreSchedule = req.body.taken // ["MATH*1080", "BIOL*1030", "MGMT*4000"]
  let limit = parseInt(req.body.limit)

  if (!Number.isInteger(limit) || limit <= 0) {
    limit = 5
  }

  const spawn = require('child_process').spawn
  const child = spawn('python3', ['./newparse.py'])

  child.stdin.setEncoding('utf-8')
  child.stdout.pipe(process.stdout)

  child.stdin.write(JSON.stringify(toSchedule) + '\n')
  child.stdin.write(JSON.stringify(ignoreSchedule) + '\n')
  child.stdin.write(limit + '\n')
  child.stdin.end()

  child.stdout.on('data', (data) => {
    res.send(JSON.parse(data.toString()))
  })

  child.stderr.on('data', (data) => {
    console.log(data.toString())
  })
})

app.get('/api/query', function (req, res) {
  res.setHeader('Content-type', 'application/json')
  res.send([])
})

const client = new MongoClient(url)
client.connect()

app.get('/api/course/:query', async function (req, res) {
  res.setHeader('Content-type', 'application/json')
  const school = 'Guelph'

  try {
    const db = client.db('scheduler')
    var collection = db.collection('cachedData')

    const query = { School: school, Code: req.params.query.toUpperCase() }
    const found = await collection.findOne(query, {})
    res.end(JSON.stringify(found))
  } finally {
  }
})

app.get('/api/query/:query', async function (req, res) {
  res.setHeader('Content-type', 'application/json')
  const school = 'Guelph'

  try {
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
    ).limit(10).toArray(async (err, docs) => {
      res.end(JSON.stringify(docs))
    })
  } finally {
  }
})

app.listen(8085, () => console.log('Listening on port 8085!'))
