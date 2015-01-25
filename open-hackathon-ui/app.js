var express = require('express')
var config = require('./config')
var bodyParser = require('body-parser')
var cookieParser = require('cookie-parser')
var path = require('path')
var proxy = require('./router/proxy')
var port = process.env.PORT || config.post
var app = express()

app.enable('trust proxy')
app.use(express.static(__dirname + '/.tmp'))
app.use('/bower_components', express.static('./bower_components'))
app.use(express.static(__dirname + '/app'))
app.use(cookieParser())
app.use(bodyParser.urlencoded({
    extended: true
}))
app.use(bodyParser.json())
app.use(proxy)

app.get('/clearcookie', function(req, res) {
    res.clearCookie('osslab.msopentech.cn')
    res.redirect('/sss.html')
})
app.listen(port, config.hostname)

console.log('open ' + config.hostname + ' started on prot ' + port)
