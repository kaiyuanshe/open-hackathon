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
  'ui.router'
]).config(function($stateProvider, $urlRouterProvider) {
  $stateProvider.state('manage', {
      abstract: true,
      url: '/',
      templateUrl: '/static/partials/manage/manage.html',
      controller: 'manageController'
    }).state('manage.edit', {
      url: 'edit/:name',
      templateUrl: '/static/partials/manage/edit.html',
      controller: 'editController'
    })
    .state('manage.users', {
      url: 'users/:name',
      templateUrl: '/static/partials/manage/users.html',
      controller: 'usersController'
    })
    .state('manage.admin', {
      url: 'admin/:name',
      templateUrl: '/static/partials/manage/admin.html',
      controller: 'adminController'
    })
    .state('manage.organizers', {
      url: 'organizers/:name',
      templateUrl: '/static/partials/manage/organizers.html',
      controller: 'organizersController'
    })
    .state('manage.prizes', {
      url: 'prizes/:name',
      templateUrl: '/static/partials/manage/prizes.html',
      controller: 'prizesController'
    })
    .state('manage.awards', {
      url: 'awards/:name',
      templateUrl: '/static/partials/manage/awards.html',
      controller: 'awardsController'
    })
    .state('manage.ve', {
      url: 've/:name',
      templateUrl: '/static/partials/manage/ve.html',
      controller: 'veController'
    })
    .state('manage.monitor', {
      url: 'monitor/:name',
      templateUrl: '/static/partials/manage/monitor.html',
      controller: 'monitorController'
    })
    .state('manage.cloud', {
      url: 'cloud/:name',
      templateUrl: '/static/partials/manage/cloud.html',
      controller: 'cloudController'
    })
    .state('manage.servers', {
      url: 'servers/:name',
      templateUrl: '/static/partials/manage/servers.html',
      controller: 'serversController'
    })
});
