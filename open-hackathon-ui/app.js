var path = require('path');
var http = require('http');
var express = require('express');
var hbs = require('hbs');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var services = require('./common/services');
var proxy = require('./router/proxy');
var config = require('./config');

var app = express();

hbs.registerPartials(path.join(__dirname, 'views/partials'));
app.enable('trust proxy');
app.set('view engine', 'html');
app.set('views', path.join(__dirname, 'views'));
app.engine('html', hbs.__express);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));
app.use(express.static(path.join(__dirname, '.tmp')));
app.use(express.static(path.join(__dirname,'app')));
app.use('/bower_components', express.static('./bower_components'))
app.use(cookieParser());

app.use(function (req, res, next){
  res.api = services;
  res.config = config;
  next();
});

app.use(proxy);

app.use(function (req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  res.render('error', {message: '404', error: "Error:Not Found", layout: ''});
});

if (app.get('env') === 'development') {
  app.use(function (err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
      message: err.message,
      error: err
    });
  });
}

var port = normalizePort(process.env.PORT || 80 );
var server = http.createServer(app);

server.listen(port, function () {
  console.log('start ' + config.hostname + ', started on prot ' + port)
});

server.on('error', function (error) {
  if (error.syscall !== 'listen') {
    throw error;
  }
  var bind = typeof port === 'string'
    ? 'Pipe ' + port
    : 'Port ' + port
  switch (error.code) {
    case 'EACCES':
      console.error(bind + ' requires elevated privileges');
      process.exit(1);
      break;
    case 'EADDRINUSE':
      console.error(bind + ' is already in use');
      process.exit(1);
      break;
    default:
      throw error;
  }
});

function normalizePort(val) {
  var port = parseInt(val, 10);
  if (isNaN(port)) {
    return val;
  }
  if (port >= 0) {
    return port;
  }
  return false;
}


/*app.get('/addcookie', function(req, res) {
 res.cookie('add', JSON.stringify({
 ab: 'sdfsadf',
 sss: 'sdfsf'
 }));
 res.cookie('UserInformation', '{"avatar_url":"https://avatars.githubusercontent.com/u/5856568?v=3","create_time":"2015-01-27 03:35:27","email":"ifendoe@gmail.com","experiments":[],"id":1,"last_login_time":"2015-01-27 03:35:27","name":"Fendoe","nickname":"Boli Guan","online":1,"token":"896628af-a5d5-11e4-879d-0800271a48a8"}')
 res.redirect('/')
 })

 app.get('/clearcookie', function(req, res) {
 console.log(req.cookies)
 res.clearCookie('UserInformation')
 res.clearCookie('add')
 res.redirect('/')
 })

 app.listen(port, function() {
 consolelog.log('start ' + config.hostname + ', started on prot ' + port)
 //log4js.worker().info('start ' + config.hostname + ', started on prot ' + port);
 })

 process.on('uncaughtEExeption', function(err) {
 //log4js.worker().error('Error caught in uncaughtException event:', err);
 })*/
