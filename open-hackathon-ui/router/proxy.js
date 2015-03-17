var express = require('express')
var router = express.Router()
var config = require('../config')
var services = require('../common/services')
var request = require('request')
var util = require('util')

var COOKIE_USERINFORMATION = 'User'

function login(res, name, token) {
  res.api.user.login.post({
    provider: name,
    access_token: token
  }, function (response, data) {
    res.cookie(COOKIE_USERINFORMATION, JSON.stringify(data));
    if (data.experiments) {
      res.send('<script>window.opener.location.href = "/#/hackathon";window.close();</script>');
    } else if (data.register_state) {
      res.send('<script>window.opener.location.href = "/#/settings";window.close();</script>');
    } else {
      res.send('<script>window.opener.location.href = "/#/notregister";window.close();</script>');
    }
  });
}

router.get('/github', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.sociallogin.github.access_token_url,
    json: {
      client_id: config.sociallogin.github.client_id,
      client_secret: config.sociallogin.github.client_secret,
      redirect_uri: util.format(config.sociallogin.github.redirect_uri, config.hostname),
      code: req.query.code
    }
  };
  request.get(option, function (err, request, body) {
    login(res, 'github', body.access_token);
  });
});

router.get('/qq', function (req, res) {
  login(res, 'qq', req.query['#access_token']);
});

router.get('/gitcafe', function (req, res) {

});

router.delete('/proxy/login', function (req, res) {
  res.api.login.del({
    token: req.body.token
  }, function (ares, body) {
    res.clearCookie(COOKIE_USERINFORMATION);
    res.josn(data);
  });
});

module.exports = router
