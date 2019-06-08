var express = require('express');
var router = express.Router();
var ejs = require('ejs');
var fs = require('fs');
var PythonShell = require('python-shell');

router.get('/', (req, res) => {
  if(!("sessionID" in req.cookies)) {
    res.cookie('sessionID', generateHash(), {expires: new Date(2147483647000)});
  }
  
  res.sendFile(path.resolve('public/html/index.html'))
});

module.exports = router;
