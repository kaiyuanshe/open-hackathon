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
    'oh.services',
    'oh.controllers',
    'oh.directives'
  ])
  .config(function ($stateProvider, $urlRouterProvider) {
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
            templateUrl: 'views/main.html',
            controller: 'main.controller'
          },
          'footer@index': {
            templateUrl: 'views/footer.html'
          }
        }
      })
      .state('index.settings', {
        url: 'settings',
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
      .state('index.hackathon', {
        url: 'hackathon',
        views: {
          'header@index': {
            templateUrl: 'views/hackathon-header.html',
            controller: 'oh.header.controller'
          },
          'main@index': {
            templateUrl: 'views/hackathon.html',
            controller: ''
          }
        }
      })
      .state('notregister', {
        url: '/notregister',
        views: {
          '': {
            templateUrl: 'views/notregister.html',
            controller: 'notregister.controller'
          }
        }
      })
      .state('lineup', {
        url: '/lineup',
        views: {
          '': {
            templateUrl: 'views/lineup.html',
            controller: 'lineup.controller'
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
    ;
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
