var express = require('express');
var subdomain = require('express-subdomain');

var path = require('path');
var favicon = require('static-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var fs = require("fs");

var home = require('./routes/main');
var selectHome = require('./routes/select');

var app = express();
var http = require('http');

app.use(favicon());
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, '../dist')));

app.set('views', path.join(__dirname, 'html'));

app.use(subdomain('guelph', home));
app.use('/', home);

/// catch 404 and forward to error handler
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});

/// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
    app.use(function(err, req, res, next) {
        res.status(err.status || 500);
        res.send('error: ' + err.message);
    });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.send('error: ' + err.message);
});

app.set('port', process.env.PORT || 8083);

http.createServer(app).listen(app.get('port'));
console.log("Listening");

function closeServer(cb)
{
    console.log('Stopping ...');
    cb();
}

process.on('SIGINT', function() {
    closeServer(function() {
        process.exit();
    });
});
