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

angular.module('oh.controllers', [])
  .controller('MainController', MainController = function($scope, $rootScope, $location, $window, $cookies, $state, $translate, api, activityService, NAV) {
    $scope.isloaded = true;
    $scope.loading = false;

    $rootScope.$on("$stateChangeStart", function(event, toState, toParams, fromState, fromParams) {
      $scope.loading = true;
      var activity = activityService.getCurrentActivity();
      $scope.currentActivity = {
        name: toParams.name
      };
      if (toParams.name === undefined || activity.name == toParams.name) {

      } else {
        activity = activityService.getByName(toParams.name)
        if (activity.name != undefined) {
          activity.name = toParams.name;
          activityService.setCurrentActivity(activity);
          $scope.$emit('changeCurrenActivity', activity);
        } else {
          api.admin.hackathon.get({
            header: {
              hackathon_name: toParams.name
            }
          }).then(function(data) {
            if (data.error) {
              $state.go('404');
            } else {
              activityService.add(data);
              $state.go(toState.name, {
                name: toParams.name
              });
            }
          });
          event.preventDefault();
        }
      }
    });

    $rootScope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams) {
      $scope.loading = false;
    });

  }).controller('manageController', function($scope, $state, session, NAV) {
    $scope.page = {
      name: ''
    };
    $scope.currentUser = session.user;
    $scope.$on('pageName', function(event, pageName) {
      $scope.page.name = pageName;
      event.preventDefault();
      event.stopPropagation();
    });


    $scope.currentArea = NAV.manage;
    $scope.$emit('pageName', '');
    $scope.isActive = function(item) {
      return {
        active: $state.includes(item.state)
      }
    }

    $scope.navLink = function(item) {
      return $state.href(item.state, {
        name: $scope.currentActivity.name
      }, {});
    }



  }).controller('editController', function($rootScope, $scope, $filter, dialog, session, activityService, api, activity) {
    //
    $scope.$emit('pageName', 'SETTINGS.EDIT_ACTIVITY');


    $scope.animationsEnabled = true;
    activity.banners = $filter('split')(activity.banners, ',');

    activity.event_start_time = new Date(activity.event_start_time);
    activity.event_end_time = new Date(activity.event_end_time);
    //var banners = $filter('split')('http://img.zcool.cn/community/03320dd554c75c700000158fce17209.jpg,http://www.bz55.com/uploads/allimg/100719/1_100719110156_1.jpg');
    $scope.modules = activity
      //$scope.minDate = new Date();
    $scope.delBanner = function(index) {
      $scope.modules.banners.splice(index, 1);
    }


    $scope.showAddBannerDialog = function() {
      $scope.modules.banners.push('http://image5.tuku.cn/pic/wallpaper/fengjing/shanshuilantian/014.jpg');
    }

    $scope.showTip = function() {
      $scope.$emit('showTip', {
        level: 'tip-success',
        content: '保存成功'
      });
    }
    $scope.open = {
      date1: false
    }

    $scope.openDatetime = function() {
      $scope.open.date1 = true;
    }

    $scope.provider = {
      windows: $filter('isProvider')($scope.modules.config.login_provider, 1),
      github: $filter('isProvider')($scope.modules.config.login_provider, 2),
      qq: $filter('isProvider')($scope.modules.config.login_provider, 4),
      weibo: $filter('isProvider')($scope.modules.config.login_provider, 8),
      alauda: $filter('isProvider')($scope.modules.config.login_provider, 32),
      gitcafe: $filter('isProvider')($scope.modules.config.login_provider, 16),
    };
    $scope.providerChange = function(checked, value) {
      if (checked) {
        $scope.modules.config.login_provider = ((+$scope.modules.config.login_provider) || 0) | value;
      } else {
        $scope.modules.config.login_provider = ((+$scope.modules.config.login_provider) || 0) ^ value;
      }
      $scope.$emit('showTip', {
        level: 'tip-success',
        content: '登录方式修改成功'
      });
    }

  }).controller('usersController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.USERS');


  }).controller('adminController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.ADMINISTRATORS');

  }).controller('organizersController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.ORGANIZERS');

  }).controller('prizesController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.PRIZES');

  }).controller('awardsController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.AWARDS');

  }).controller('veController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.VIRTUAL_ENVIRONMENT');

  }).controller('monitorController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.ENVIRONMENTAL_MONITOR');

  }).controller('cloudController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.CLOUD_RESOURCES');

  }).controller('serversController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.SERVERS');
  });
