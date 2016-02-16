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
  
angular.module('manageView', [
    'ngCookies',
    'ngSanitize',
    'pascalprecht.translate',
    'ui.router',
    'ui.bootstrap',
    'oh.manage.router',
    'oh.pages',
    'oh.providers',
    'oh.filters',
    'oh.controllers',
    'oh.directives',
    'oh.api'
  ])
  .config(function($locationProvider, $translateProvider, $stateProvider, $urlRouterProvider, VERSION) {
    $translateProvider.useStaticFilesLoader({
        prefix: '/static/languages/',
        suffix: '.json'
      }).preferredLanguage('zh-de')
      .useSanitizeValueStrategy()
      .useLocalStorage();

    $urlRouterProvider.otherwise('/main');

    $stateProvider.state('main', {
      url: '/main',
      templateUrl: '/static/partials/manage/main.html?v=' + VERSION,
      controller: function($scope, $rootScope, activityService) {
        activityService.reload();

        $rootScope.$on('getActivity', function(event, activities) {
          $scope.activities = activityService.getAll();
          event.stopPropagation();
        });

        $scope.online = function(activity) {
          activity.status = 1;
        }
        $scope.offline = function(activity) {
          activity.status = 2;
        }
      }
    });
    $stateProvider.state('create', {
      url: '/create',
      templateUrl: '/static/partials/manage/create.html?v=' + VERSION,
    });
    $stateProvider.state('404', {
      url: '/404',
      templateUrl: '/static/partials/manage/404.html?v=' + VERSION,
    });

    $locationProvider.html5Mode(true).hashPrefix('!');

  }).run(function($rootScope, $state, authService, api, activityService) {
    authService.getUser();
    $rootScope.$on('showTip', function(event, obj) {
      $rootScope.tip = obj;
      event.preventDefault();
      event.stopPropagation();
    });
  });
