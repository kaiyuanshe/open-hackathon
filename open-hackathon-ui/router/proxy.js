var express = require('express')
var router = express.Router()
var config = require('../config')
var services = require('../common/services')
var request = require('request')
var async = require('async')
var util = require('util')

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
    }
    request.post(option, function(err, body) {
        services.user.login.post({
            Provider: 'github',
            access_token: body.access_token,
            client_id: config.sociallogin.qq.client_id
        }, function(response, data) {
            res.cookie('UserInformation', JSON.stringify(data), {
                maxAge: 86400000,
                httpOnly: true
            });
            res.sendFile('/')
        })
    })
})

router.get('/qq', function(req, res) {
    services.user.login.post({
        Provider: 'qq',
        access_token: req.query['#access_token'],
        client_id: config.sociallogin.github.client_id
    }, function(response, data) {
        res.cookie('UserInformation', JSON.stringify(data), {
            maxAge: 86400000,
            httpOnly: true
        });
        res.sendFile('/')
    })
})

module.exports = router;
