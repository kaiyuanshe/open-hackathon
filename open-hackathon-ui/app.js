var express = require('express')
var bodyParser = require('body-parser')
var cookieParser = require('cookie-parser')
var path = require('path')
var config = require('./config')
var log4js = require('./common/log')
var proxy = require('./router/proxy')
var port = process.env.PORT || config.post
var app = express()

app.enable('trust proxy')

app.use(express.static(__dirname + '/.tmp'))
app.use('/bower_components', express.static('./bower_components'))
app.use(express.static(__dirname + '/app'))
app.use(log4js.connectLogger(path.join(__dirname, 'log4js.json')))
app.use(cookieParser())
app.use(bodyParser.urlencoded({
    extended: true
}))
app.use(bodyParser.json())
app.use(proxy)

app.get('/addcookie', function(req, res) {
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

app.listen(port, config.hostname, function() {
    log4js.worker().error('start ' + config.hostname + ', started on prot ' + port);
})

process.on('uncaughtEExeption', function(err) {
    log4js.worker().error('Error caught in uncaughtException event:', err);
})
