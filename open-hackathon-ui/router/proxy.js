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
    if (data.experiments.length > 0) {
      res.send('<script type="text/javascript">window.opener.location.href = "/#/hackathon";window.close();</script>');
    } else if (data.register_state) {
      res.send('<script type="text/javascript">window.opener.location.href = "/#/settings";window.close();</script>');
    } else {
      res.send('<script type="text/javascript">window.opener.location.href = "/#/notregister";window.close();</script>');
    }
  });
}

router.get('/github', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.login.github.access_token_url,
    json: {
      client_id: config.login.github.client_id,
      client_secret: config.login.github.client_secret,
      redirect_uri: util.format(config.login.github.redirect_uri, config.hostname),
      code: req.query.code
    }
  };
  request.get(option, function (err, request, body) {
    login(res, 'github', body.access_token);
  });
});

router.get('/qq', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.login.qq.access_token_url,
    json: {
      client_id: config.login.qq.client_id,
      client_secret: config.login.qq.client_secret,
      redirect_uri: util.format(config.login.qq.redirect_uri, config.hostname),
      grant_type: config.login.qq.grant_type,
      code: req.query.code
    }
  };
  request.get(option, function (err, request, body) {
    login(res, 'qq', body.access_token);
  });

});

router.get('/gitcafe', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.login.gitcafe.access_token_url,
    json: {
      client_id: config.login.gitcafe.client_id,
      client_secret: config.login.gitcafe.client_secret,
      redirect_uri: util.format(config.login.gitcafe.redirect_uri, config.hostname),
      grant_type: config.login.gitcafe.grant_type,
      code: req.query.code
    }
  };
  request.get(option, function (err, request, body) {
    login(res, 'gitcafe', body.access_token);
  });
});

router.get('/weibo', function (req, res) {
  var option = {
    'content-type': 'application/json',
    url: config.login.weibo.access_token_url,
    json: {
      client_id: config.login.weibo.client_id,
      client_secret: config.login.weibo.client_secret,
      redirect_uri: util.format(config.login.weibo.redirect_uri, config.hostname),
      grant_type: config.login.weibo.grant_type,
      code: req.query.code
    }
  };
  request.get(option, function (err, request, body) {
    login(res, 'weibo', body.access_token);
  });
});

module.exports = router
