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
]).config(function($locationProvider, $stateProvider, $urlRouterProvider, VERSION) {
  $urlRouterProvider.otherwise('/main');
  $stateProvider.state('main', {
    url: '/main',
    templateUrl: '/static/partials/manage/main.html?v=' + VERSION,
    controller: function($scope, $rootScope, activityService, session, api) {
      activityService.reload();

      $rootScope.$on('getActivity', function(event, activities) {
        $scope.activities = activityService.getAll();
        $scope.currentUser = session.user;
        event.stopPropagation();
      });

      $scope.online = function(activity) {
        if (activity.status == 1) return;
        api.admin.hackathon.online.post({
          header: {
            hackathon_name: activity.name
          }
        }).then(function(data) {
          if (data.error) {
            var message = ''
            if (data.error.code == 412101) {
              message = '当前黑客松没有还未创建成功。'
            } else if (data.error.code == 412102) {
              message = '证书授权失败，请检验SUBSCRIPTION ID是否正确。'
            } else {
              message = data.error.friendly_message
            }
            $scope.$emit('showTip', {
              level: 'tip-danger',
              content: message
            });
          } else {
            $scope.$emit('showTip', {
              level: 'tip-success',
              content: '上线成功'
            });
            activity.status = 1;
          }
        })
      }

      $scope.applyOnline = function(activity) {
        if (activity.status == 1 || activity.status == 3) return;
        api.admin.hackathon.applyonline.post({
          header: {
            hackathon_name: activity.name
          }
        }).then(function(data) {
          if (data.error) {
            var message = ''
            if (data.error.code == 412101) {
              message = '当前黑客松没有还未创建成功。'
            } else if (data.error.code == 412102) {
              message = '证书授权失败，请检验SUBSCRIPTION ID是否正确。'
            } else {
              message = data.error.friendly_message
            }
            $scope.$emit('showTip', {
              level: 'tip-danger',
              content: message
            });
          } else {
            $scope.$emit('showTip', {
              level: 'tip-success',
              content: '已经申请上线'
            });
            activity.status = 3;
          }
        })
      }
      $scope.offline = function(activity) {
        if (activity.status == 2) return;
        api.admin.hackathon.offline.post({
          header: {
            hackathon_name: activity.name
          }
        }).then(function(data) {
          if (data.error) {
            var message = ''
            if (data.error.code == 412101) {
              message = '当前黑客松没有还未创建成功。'
            } else {
              message = data.error.friendly_message
            }
            $scope.$emit('showTip', {
              level: 'tip-danger',
              content: message
            });
          } else {
            $scope.$emit('showTip', {
              level: 'tip-success',
              content: '成功'
            });
            activity.status = 2;
          }
        })
      }
      $scope.delete = function(activity) {
        api.admin.hackathon.delete({
          header: {
            hackathon_name: activity.name
          }
        }).then(function(data) {
          if (data.error) {
            var message = ''
            $scope.$emit('showTip', {
              level: 'tip-danger',
              content: message
            });
          } else {
            var index = $scope.activities.indexOf(activity)
            $scope.activities.splice(index, 1)
            $scope.$emit('showTip', {
              level: 'tip-success',
              content: '删除成功'
            });
          }
        })
      }
    }
  }).state('create', {
    url: '/create?name',
    templateUrl: '/static/partials/manage/create.html?v=' + VERSION,
    controller: 'createController'
  }).state('404', {
    url: '/404',
    templateUrl: '/static/partials/manage/404.html?v=' + VERSION,
  }).state('manage', {
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
  }).state('manage.users', {
    url: 'users/:name',
    templateUrl: '/static/partials/manage/users.html?v=' + VERSION,
    controller: 'usersController',
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
  }).state('manage.admin', {
    url: 'admin/:name',
    templateUrl: '/static/partials/manage/admin.html?v=' + VERSION,
    controller: 'adminController'
  }).state('manage.organizers', {
    url: 'organizers/:name',
    templateUrl: '/static/partials/manage/organizers.html?v=' + VERSION,
    controller: 'organizersController'
  }).state('manage.prizes', {
    url: 'prizes/:name',
    templateUrl: '/static/partials/manage/prizes.html?v=' + VERSION,
    controller: 'prizesController',
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
  }).state('manage.awards', {
    url: 'awards/:name',
    templateUrl: '/static/partials/manage/awards.html?v=' + VERSION,
    controller: 'awardsController'
  }).state('manage.notices', {
    url: 'notices/:name',
    templateUrl: '/static/partials/manage/notices.html?v=' + VERSION,
    controller: 'noticesController',
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
  }).state('manage.cloud', {
    url: 'cloud/:name',
    templateUrl: '/static/partials/manage/cloud.html?v=' + VERSION,
    controller: 'cloudController',
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
  }).state('manage.ve', {
    url: 've/:name',
    templateUrl: '/static/partials/manage/ve.html?v=' + VERSION,
    controller: 'veController',
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
  }).state('manage.monitor', {
    url: 'monitor/:name',
    templateUrl: '/static/partials/manage/monitor.html?v=' + VERSION,
    controller: 'monitorController'
  }).state('manage.azurecert', {
    url: 'azure/:name',
    templateUrl: '/static/partials/manage/azurecert.html?v=' + VERSION,
    controller: 'azurecertController'
  }).state('manage.servers', {
    url: 'servers/:name',
    templateUrl: '/static/partials/manage/servers.html?v=' + VERSION,
    controller: 'serversController'
  })
  $locationProvider.html5Mode(true).hashPrefix('!');

});
