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

'use strict';
/**
 * @namespace oh.app
 * @author <ifendoe@gmail.com>
 * @version 0.0.1
 * Created by Boli Guan on 15-3-10.
 */

/**
 * @ngdoc overview
 * @name hackathonApp
 * @description
 * # hackathonApp
 *
 * Main module of the application.
 */

'use strict';

/**
 * @name $$cookieReader
 * @requires $document
 *
 * @description
 * This is a private service for reading cookies used by $http and ngCookies
 *
 * @return {Object} a key/value map of the current cookies
 */
function $$CookieReader($document) {
  var rawDocument = $document[0] || {};
  var lastCookies = {};
  var lastCookieString = '';

  function safeDecodeURIComponent(str) {
    try {
      return decodeURIComponent(str);
    } catch (e) {
      return str;
    }
  }

  return function() {
    var cookieArray, cookie, i, index, name;
    var currentCookieString = rawDocument.cookie || '';

    if (currentCookieString !== lastCookieString) {
      lastCookieString = currentCookieString;
      cookieArray = lastCookieString.split('; ');
      lastCookies = {};

      for (i = 0; i < cookieArray.length; i++) {
        cookie = cookieArray[i];
        index = cookie.indexOf('=');
        if (index > 0) { //ignore nameless cookies
          name = safeDecodeURIComponent(cookie.substring(0, index));
          // the first value that is seen for a cookie is the most
          // specific one.  values for the same cookie name that
          // follow are for less specific paths.
          if (lastCookies[name] === undefined) {
            lastCookies[name] = safeDecodeURIComponent(cookie.substring(index + 1));
          }
        }
      }
    }
    return lastCookies;
  };
}

$$CookieReader.$inject = ['$document'];
angular.module('ngCookies').provider('$$cookieReader', function $$CookieReaderProvider() {
  this.$get = $$CookieReader;
});



angular
  .module('oh.app', [
    'ngAnimate',
    'ngAria',
    'ngCookies',
    'ngMessages',
    'ngResource',
    'ui.router',
    'ngSanitize',
    'ngTouch',
    'ui.bootstrap',
    'oh.common',
    'oh.services',
    'oh.controllers',
    'oh.directives'
  ])
  .config(function ($stateProvider, $urlRouterProvider, $locationProvider ,$compileProvider) {
    $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|skype):/);
    $locationProvider.html5Mode(false);
    $locationProvider.hashPrefix('!');
    $urlRouterProvider.otherwise('/');
    $stateProvider
      .state('index', {
        url: '/',
        views: {
          '': {
            templateUrl: 'views/master.html'
          },
          'header@index': {
            templateUrl: 'views/header.html'
          },
          'main@index': {
            templateUrl: 'views/home.html',
            controller: 'oh.home.controller'
          },
          'footer@index': {
            templateUrl: 'views/footer.html'
          }
        }
      })
      .state('index.settings', {
        url: ':hackathon_name/settings',
        views: {
          'header@index': {
            templateUrl: 'views/header.html',
            controller: function ($scope) {
              $scope.isShow = true;
            }
          },
          'main@index': {
            templateUrl: 'views/settings.html',
            controller: 'settings.controller'
          }
        }
      })
      .state('hackathon', {
        url: '/:hackathon_name/hackathon',
        views: {
          '': {
            templateUrl: 'views/master.html',
            controller: 'oh.hackathon.controller'
          },
          'header@hackathon': {
            templateUrl: 'views/hackathon-header.html'
          },
          'main@hackathon': {
            templateUrl: 'views/hackathon.html'
          },
          'footer@hackathon': {
            templateUrl: 'views/footer.html'
          }
        }
      })
      .state('index.challenges', {
        url: 'challenges',
        views: {
          'header@index': {
            templateUrl: 'views/header.html',
            controller: function ($scope, User) {
              if (User) {
                $scope.isShow = true;
              }
            }
          },
          'main@index': {
            templateUrl: 'views/challenges.html'
          }
        }
      })
      .state('index.register', {
        url: ':hackathon_name/register',
        views: {
          'main@index': {
            templateUrl: 'views/register.html',
            controller: 'register.controller'
          }
        }
      })
      .state('error', {
        url: '/error',
        views: {
          '': {
            templateUrl: 'views/error.html',
            controller: function ($scope, $stateParams, log) {
              $scope.error = $stateParams.error;
              console.log(log);
            }
          }
        }
      })
      .state('expired', {
        url: '/expired',
        views: {
          '': {
            templateUrl: 'views/expired.html'
          }
        }
      })
      .state('login', {
        url: '/login',
        views: {
          '': {
            templateUrl: 'views/login.html',
            controller: 'login.controller'
          }
        }
      })
      .state('index.userprofile',{
        url:'userprofile',
        views: {
          'main@index': {
            templateUrl: '../views/userprofile.html',
            controller:'userprofile.controller'
          }
        }
      })
      .state('redirect', {
        url: '/redirect',
        controller: function ($cookies, state) {
          var hackathon_name = $cookies.get('redirectHakathonName');
          state.go('index.register', {hackathon_name: hackathon_name})
        }
      });
  })
  .run(function ($rootScope, Authentication, $stateParams, $log) {
    $rootScope.config = config;
    $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
      var user = Authentication.getUser();
      if (user) {
        $rootScope.isUser = true;
      } else {
        $rootScope.isUser = false;
      }
    });

    $rootScope.$on('stateChangeSuccess', function (event) {

    });
  });
String.prototype.format = function (args) {
  var result = this;
  if (arguments.length > 0) {
    if (arguments.length == 1 && typeof(args) == 'object') {
      for (var key in args) {
        if (args[key] != undefined) {
          var reg = new RegExp('({' + key + '})', 'g');
          result = result.replace(reg, args[key]);
        }
      }
    } else {
      for (var i = 0; i < arguments.length; i++) {
        if (arguments[i] != undefined) {
          var reg = new RegExp('({[' + i + ']})', 'g');
          result = result.replace(reg, arguments[i]);
        }
      }
    }
  }
  return result;
};
