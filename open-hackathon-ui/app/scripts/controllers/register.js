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
 * @namespace oh.controllers
 * @author <ifendoe@gmail.com>
 * @version 0.0.1
 * Created by Boli Guan on 15-4-15.
 */

angular.module('oh.controllers')
  .controller('register.controller', function ($scope, $rootScope, $stateParams, $cookies, $modal, state, Authentication, API) {
    var registration = null;
    $rootScope.isShow = true;
    var user = Authentication.getUser();
    var hackathon_name = $stateParams.hackathon_name || config.name;

    API.hackathon.registration.list.get({header: {hackathon_name: hackathon_name}})
      .then(function (res) {
        //$scope.registerList = res.data;
    })


    API.hackathon.get({header: {hackathon_name: hackathon_name}}).then(function (res) {
      $scope.hackathon = res.data;
      var isExpired = $scope.hackathon.registration_end_time < Date.now();
      if (isExpired) {
        $scope.hackathon.message = '活动已经结束';
      }
      if ($scope.hackathon.status == 0) {
        state.go('index.home');
      }
      $scope.isLoad = false;
    })

    API.user.registration.get({header: {hackathon_name: hackathon_name}}).then(function (res) {
      $scope.hackathon.isRegister = true;
      if (res.data.error) {
        user = undefined;
      } else {
        registration = res.data.registration;

        if (registration) {
          checkUserStatus(registration.status, res.data.hackathon.basic_info.auto_approve);
        }
        $scope.goWork = function () {
          if (res.data.experiment) {
            state.go('hackathon', {hackathon_name: hackathon_name});
          } else {
            state.go('index.settings', {hackathon_name: hackathon_name});
          }
        }
      }
    });

    $scope.showRegister = function () {
      if (!user) {
        $cookies.put('redirectHakathonName', hackathon_name);
        state.go('index');
        return;
      }
      if (!user.user_profile) {
        state.go('index.userprofile');
        return;
      }
      openModal();
    }

    function checkUserStatus(status, approve) {
      $scope.hackathon.isRegister = false;
      if (status == 0 && !approve) {
        $scope.hackathon.message = '您的报名正在审核中，请等待。';
      } else if (status == 2) {
        $scope.hackathon.message = '您的报名已被拒绝，如有疑问请联系主办方。';
      } else if (status == 3 && !approve) {
        $scope.hackathon.isRegister = true;
      } else if (status == 1 || status == 3 || approve) {
        $scope.hackathon.start = true
        $scope.hackathon.message = '您的报名已经审核已通过。';
      }
    }

    function openModal() {
      var modalInstance = $modal.open({
        animation: $scope.animationsEnabled,
        templateUrl: 'myModalContent.html',
        controller: 'registerFormController'
      });
      modalInstance.result.then(function (register) {
        API.user.registration.post({
          body: {
            hackathon_id: $scope.hackathon.id,
            team_name: register.team_name
          },
          header: {hackathon_name: hackathon_name}
        }).then(function (res) {
          if ($scope.hackathon.basic_info.auto_approve) {
            checkUserStatus(3, 0);
          } else {
            checkUserStatus(0, 0);
          }
        })
      }, function () {
        //$log.info('Modal dismissed at: ' + new Date());
      });
    }

    $scope.dimensional = 'http://qr.liantu.com/api.php?bg=f2f2f2&fg=101010&gc=101010&el=l&w=150&m=10&text=' + location.href;

  })
  .controller('registerFormController', function ($scope, $modalInstance, $stateParams, API) {
    var hackathon_name = $stateParams.hackathon_name || config.name;
    $scope.states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Dakota', 'North Carolina', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'];
    $scope.ok = function () {
      $modalInstance.close($scope);
    };
    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
    $scope.getTeamNames = function (name) {
      return API.hackathon.team.list.get({
        query: {
          name: name,
          number: 5
        }, header: {hackathon_name: hackathon_name}
      }).then(function (res) {
        return res.data;
      })
    }
    $scope.submit = function () {
      $modalInstance.close($scope.register);
    }
  });
