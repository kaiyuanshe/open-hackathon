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

angular.module('oh.manage.router', [
  'ui.router',
  'oh.pages'
]).config(function($stateProvider, $urlRouterProvider, VERSION) {
  $stateProvider.state('manage', {
      abstract: true,
      url: '/',
      templateUrl: '/static/partials/manage/manage.html?v=' + VERSION,
      controller: 'manageController'
    }).state('manage.edit', {
      url: 'edit/:name',
      templateUrl: '/static/partials/manage/edit.html?v=' + VERSION,
      controller: 'editController',
      resolve: {
        activity: function($stateParams, api) {
          return api.admin.hackathon.get({
            header: {
              hackathon_name: $stateParams.name
            }
          }).then(function(data) {
            return data;
          });
        }
      }
    })
    .state('manage.users', {
      url: 'users/:name',
      templateUrl: '/static/partials/manage/users.html?v=' + VERSION,
      controller: 'usersController'
    })
    .state('manage.admin', {
      url: 'admin/:name',
      templateUrl: '/static/partials/manage/admin.html?v=' + VERSION,
      controller: 'adminController'
    })
    .state('manage.organizers', {
      url: 'organizers/:name',
      templateUrl: '/static/partials/manage/organizers.html?v=' + VERSION,
      controller: 'organizersController'
    })
    .state('manage.prizes', {
      url: 'prizes/:name',
      templateUrl: '/static/partials/manage/prizes.html?v=' + VERSION,
      controller: 'prizesController'
    })
    .state('manage.awards', {
      url: 'awards/:name',
      templateUrl: '/static/partials/manage/awards.html?v=' + VERSION,
      controller: 'awardsController'
    })
    .state('manage.ve', {
      url: 've/:name',
      templateUrl: '/static/partials/manage/ve.html?v=' + VERSION,
      controller: 'veController'
    })
    .state('manage.monitor', {
      url: 'monitor/:name',
      templateUrl: '/static/partials/manage/monitor.html?v=' + VERSION,
      controller: 'monitorController'
    })
    .state('manage.cloud', {
      url: 'cloud/:name',
      templateUrl: '/static/partials/manage/cloud.html?v=' + VERSION,
      controller: 'cloudController'
    })
    .state('manage.servers', {
      url: 'servers/:name',
      templateUrl: '/static/partials/manage/servers.html?v=' + VERSION,
      controller: 'serversController'
    })
});
