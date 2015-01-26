var express = require('express')
var  request = require('request')
var config = require("./config")
var bodyParser = require('body-parser')
var path = require('path')
var port = process.env.PORT || config.post
var app = express()

app.enable('trust proxy')
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())
app.use(express.static(__dirname + '/.tmp'))
app.use('/bower_components', express.static('./bower_components'))
app.use(express.static(__dirname+'/app'))


app.use('/login',function(req,res){
    console.log(req.url)
})

app.get('/github',function(req,res){
    var option = {
        url: 'http://127.0.0.1:15000/api/user/login',
        json:{
            provider:'github',
            code: req.query.code
        }
    }
    request.post(option,function(err, httpResponse,body){
        console.log(httpResponse)
        res.json({success: 1})
    })
})
app.get('/api/login',function(req,res){
    console.log(req.query)
    res.json({success: 1})
})
app.post('/api/login',function(req,res){
    console.log(req.query)
    res.json({success: 1})
})
app.put('/api/login',function(req,res){
    console.log(req.query)
    res.json({success: 1})
})
app.delete('/api/login',function(req,res){
    console.log(req.query)
    res.json({success: 1})
})
app.get('/',function(req,res){
    res.sendfile('./app/index.html')
    //res.send('hello world');
})
app.listen(port, config.hostname)

console.log('open '+config.hostname+' started on prot ' + port)
