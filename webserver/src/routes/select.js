var express = require('express');
var router = express.Router();
var ejs = require('ejs');
var fs = require('fs');
var PythonShell = require('python-shell');

router.get('/', (req, res) => {
  res.sendFile(path.resolve('public/html/select.html'))
});

module.exports = router;
