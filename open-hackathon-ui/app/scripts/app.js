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
