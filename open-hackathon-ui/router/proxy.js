var express = require('express')
var router = express.Router()
var config = require('../config')
var services = require('../common/services')
var request = require('request')
var util = require('util')


var COOKIE_USERINFORMATION = 'UserInformation'
router.get('/github', function(req, res) {
    var option = {
        'content-type': 'application/json',
        url: config.sociallogin.github.access_token_url,
        json: {
            method: config.sociallogin.github.method,
            client_id: config.sociallogin.github.client_id,
            client_secret: config.sociallogin.github.client_secret,
            redirect_uri: util.format(config.sociallogin.github.redirect_uri, config.hostname),
            code: req.query.code
        }
    };
    request.post(option, function(err, request, body) {
        services.user.login.post({
            provider: 'github',
            access_token: body.access_token
        }, function(response, data) {
            res.cookie(COOKIE_USERINFORMATION, JSON.stringify(data));
            res.redirect('/');
        });
    });
})

router.get('/qq', function(req, res) {
    services.user.login.post({
        Provider: 'qq',
        access_token: req.query['#access_token'],
    }, function(response, data) {
        res.cookie(COOKIE_USERINFORMATION, JSON.stringify(data));
        res.redirect('/')
    })
})

router.delete('/proxy/login', function(req, res) {
    services.user.login.del({
        token: req.body.token
    }, function(response, data) {
        res.clearCookie(COOKIE_USERINFORMATION);
        res.josn(data);
    });
})
router.all('/proxy/:api(*)/:?',function(req,res){
    console.log(req);
    res.json(req);
})
module.exports = router
