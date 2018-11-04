var express = require('express');
var router = express.Router();
var ejs = require('ejs');
var fs = require('fs');
var PythonShell = require('python-shell');

var baseFilePath = '/../html/'

router.get('/', (req, res) => {
    ejs.renderFile(
      __dirname + baseFilePath + 'select.html',
      {},
      (err, result) => {
        if (!err) {
            res.end(result);
        } else {
            res.end(err.toString());
            console.log(err);
        }
    });
});

module.exports = router;
