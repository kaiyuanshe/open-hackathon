var express = require('express')
var router = express.Router()
var config = require('../config')
var services = require('../common/services')
var request = require('request')
var querystring = require('querystring');
var util = require('util')


var COOKIE_USERINFORMATION = 'User'

function login(res, option) {
  res.api.user.login.post(option, function (response, data) {
    res.cookie(COOKIE_USERINFORMATION, JSON.stringify(data));
    console.log(data)
    if (data.experiments.length > 0) {
      res.redirect("/#/hackathon")
    } else if (data.register_state) {
      res.redirect("/#/settings")
    } else {
      res.redirect("/#/notregister")
    }
  });
}

router.get('/github', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.login.github.access_token_url,
    qs: {
      client_id: config.login.github.client_id,
      client_secret: config.login.github.client_secret,
      redirect_uri: util.format(config.login.github.redirect_uri, config.hostname),
      code: req.query.code
    },
    json:{}
  };
  request.get(option, function (err, request, body) {
    login(res, {
        provider: "github",
        access_token: body.access_token,
        hackathon_name: config.hackathon_name
      });
  });
});

router.get('/qq', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.login.qq.access_token_url,
    qs: {
      client_id: config.login.qq.client_id,
      client_secret: config.login.qq.client_secret,
      redirect_uri: util.format(config.login.qq.redirect_uri, config.hostname),
      grant_type: config.login.qq.grant_type,
      code: req.query.code,
      state: 'openhackathon'
    },
    json:{}
  };
  request.get(option, function (err, request, body) {
    body = querystring.parse(body);
    console.log(body)
    login(res, {
        provider: "qq",
        access_token: body.access_token,
        hackathon_name: config.hackathon_name
      });
  });

});

router.get('/gitcafe', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.login.gitcafe.access_token_url,
    qs: {
      client_id: config.login.gitcafe.client_id,
      client_secret: config.login.gitcafe.client_secret,
      redirect_uri: util.format(config.login.gitcafe.redirect_uri, config.hostname),
      grant_type: config.login.gitcafe.grant_type,
      code: req.query.code
    },
    json:{}
  };
  request.post(option, function (err, request, body) {
    login(res, {
        provider: "gitcafe",
        access_token: body.access_token,
        hackathon_name: config.hackathon_name
      });
  });
});

router.get('/weibo', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.login.weibo.access_token_url,
    qs: {
      client_id: config.login.weibo.client_id,
      client_secret: config.login.weibo.client_secret,
      redirect_uri: util.format(config.login.weibo.redirect_uri, config.hostname),
      grant_type: config.login.weibo.grant_type,
      code: req.query.code
    },
    json:{}
  };
  request.post(option, function (err, request, body) {
    console.log(body)
    login(res, {
        provider: "weibo",
        access_token: body.access_token,
        uid: body.uid,
        hackathon_name: config.hackathon_name
      });
  });
});


module.exports = router
