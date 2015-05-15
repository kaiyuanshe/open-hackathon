// -----------------------------------------------------------------------------------
// Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
//
// The MIT License (MIT)
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
// -----------------------------------------------------------------------------------

var express = require('express')
var router = express.Router()
var config = require('../config')
var services = require('../common/services')
var request = require('request')
var querystring = require('querystring');
var util = require('util');


var COOKIE_USERINFORMATION = 'User';

var COOKIE_TOKEN = 'token';

/**
 * Hackathon must be registered
 * @type {number}
 */
var HACKATHON_REGISTERED = 128;

/**
 * User already registered
 * @type {number}
 */
var USER_REGISTERED = 1;

/**
 * Hackathon has expired
 * @type {number}
 */
var HACKATHON_EXPIRED = 8;

function login(res, option) {
  res.api.user.login.post(option, function (response, data) {
    var redirect = '/#!/settings';
    if (response.statusCode >= 200 && response.statusCode < 300 && !data.error) {
      console.log(data);
      res.cookie(COOKIE_TOKEN, JSON.stringify(data.token));
      res.cookie(COOKIE_USERINFORMATION, JSON.stringify(data.user));
    }else{
      redirect = '/#!/error'
    }
    res.redirect(redirect);
  });
}


function login_bak(res, option) {
  res.api.user.login.post(option, function (response, data) {
    var redirect = '/#!/hackathon';
    if (response.statusCode >= 200 && response.statusCode <= 300) {
      var user = data.user;
      user.status = data.hackathon.end_time < Date.now() ? HACKATHON_EXPIRED:0;
      user.check_status = 0;
      if (data.hackathon.check_register == 1) {
        //当hackathon需要注册
        user.status |= HACKATHON_REGISTERED;
        if (data.registration) {
          //当用户已经注册
          user.status |= USER_REGISTERED;
          user.check_status = data.registration.status;
          if (data.registration.status == 1) {
            //data.registration.status :0表示等待审核，1表示审核通过，2表示拒绝。
            if (user.experiments && user.experiments.length > 0) {
              redirect = '/#!/hackathon';
            } else {
              redirect = '/#!/settings';
            }
          } else {
            redirect = '/#!/register';
          }
        } else {
          //当用户未注册
          redirect = '/#!/register';
        }
      } else {
        if (data.user.experiments.length == 0) {
          redirect = '/#!/settings'
        }
      }
      res.cookie(COOKIE_USERINFORMATION, JSON.stringify(user));
    } else {
      redirect = '/#!/error';
    }
    res.redirect(redirect);
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
    json: {}
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
    json: {}
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
    json: {}
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
    json: {}
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

router.get('/live', function (req, res) {
  var option = {
    //'content-type': 'application/x-www-form-urlencoded',
    url: config.login.live.access_token_url,
   // form:'application/x-www-form-urlencoded',
    form: {
      client_id: config.login.live.client_id,
      client_secret: config.login.live.client_secret,
      redirect_uri: util.format(config.login.live.redirect_uri, config.hostname),
      grant_type: config.login.live.grant_type,
      code: req.query.code
    }
  };
  request.post(option, function (err, request, body) {
    console.log(body)
    var body = JSON.parse(body);
    login(res, {
      provider: "live",
      access_token: body.access_token,
      hackathon_name: config.hackathon_name,
      user_id: body.user_id
    });
  });
});


module.exports = router
