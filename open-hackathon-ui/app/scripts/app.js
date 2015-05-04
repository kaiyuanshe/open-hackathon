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
  .config(function ($stateProvider, $urlRouterProvider, $locationProvider) {
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
        url: 'register',
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
            templateUrl: 'views/error.html'
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
      });
  })
  .run(function ($rootScope, $location, API) {

    $rootScope.$on('$locationChangeStart', function (scope, next, current) {

      if($location.path() === '/' || $location.path() === 'register' || $location.path() === 'settings') return;

      API.user.hackathon.get({header:{hackathon_name :config.name}},function(data){
        if(data.error){
          $location.path('error')
        }else{
          if(data.hackathon.status !=1){
            $location.path('error')
            return
          }else {
            if(data.registration){
              if(data.registration.status == 0 || data.registration.status == 2){
                $location.path('register')
              }else if(data.registration.status == 3 && data.hackathon.basic_info.auto_approve == 0){
                $location.path('register')
              }else if(data.experiment){
                $location.path('hackathon')
              }else{
                $location.path('settings')
              }
            }else{
              $location.path('register')
            }
          }
        }
      });

      //console.log($location.path());
    })
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
