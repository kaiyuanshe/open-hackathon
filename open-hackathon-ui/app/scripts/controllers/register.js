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
  .controller('register.controller', function ($scope, $rootScope, $stateParams, $cookieStore, state, Authentication, API) {
    var registration = null;
    $rootScope.isShow = true;
    var user = Authentication.getUser();
    var hackathon_name = $stateParams.hackathon_name || config.name;

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
      if (res.data.error) {
        user = undefined;
        $scope.hackathon.isRegister = true;
      } else {

        registration = res.data.registration;
        if (registration) {
            checkUserStatus(registration.status, res.data.hackathon.basic_info.auto_approve);
            $scope.goWork = function () {
              if (res.data.experiment) {
                state.go('hackathon', {hackathon_name: hackathon_name});
              } else {
                state.go('index.settings', {hackathon_name: hackathon_name});
              }
            }
        } else {
            $scope.hackathon.isRegister = true;
        }
      }
    });

    function checkUserStatus(status, approve) {
      $scope.hackathon.isRegister = false;
      if (status == 0) {
        $scope.hackathon.message = '您的报名正在审核中，请等待。';
      } else if (status == 2) {
        $scope.hackathon.message = '您的报名已被拒绝，如有疑问请联系主办方。';
      } else if (status == 3 && approve == 0) {
        $scope.hackathon.isRegister = true;
      } else if (status == 1 || status == 3) {
        $scope.hackathon.start = true
        $scope.hackathon.message = '您的报名已经审核已通过。';
      }
    }

    $scope.submitRegister = function (register) {
      if (registration) {
        register.id = registration.id;
        API.user.registration.put({body: register, header: {hackathon_name: hackathon_name}}, function (data) {
          state.go('hackathon', {hackathon_name: $stateParams.hackathon_name});
        });
      } else {
        API.user.registration.post({body: register, header: {hackathon_name: hackathon_name}}, function (data) {
          if($scope.hackathon.basic_info.auto_approve){
            checkUserStatus(3, 0);
          }else{
            checkUserStatus(0, 0);
          }
        });
      }
    }

    $scope.showRegister = function () {

      if (!user) {
        $cookieStore.put('redirectHakathonName', hackathon_name);
        state.go('index');
        return;
      }
      if ($scope.hackathon.basic_info.auto_approve == 1) {
        $scope.submitRegister({
          user_id: user.id,
          hackathon_id: $scope.hackathon.id,
          gender: 1,
          real_name: user.name,
          team_name: user.name,
          email: user.email[0].email
        });
      } else {
        if (registration) {
          if ($scope.hackathon.basic_info.auto_approve == 0 && registration.status == 3) {
            $scope.registerForm.show = true;
          }
        } else {
          $scope.registerForm.show = true;
        }
      }
    }

    $scope.hackathon = {
      isRegister: false
    };
    $scope.isLoad = true;
    $scope.registerForm = {show: false};
    $scope.isRegister = true;
    $scope.dimensional = 'http://qr.liantu.com/api.php?bg=f2f2f2&fg=101010&gc=101010&el=l&w=150&m=10&text=' + location.href;
    $scope.hideRegister = function () {
      $scope.registerForm.show = false;
    }

  }).
  controller('registerFormController', function ($scope, Authentication) {
    var user = Authentication.getUser() || {};
    $scope.id = $scope.hackathon.id;
    $scope.register = {
      gender: 1,
      career_type: '计算机/互联网/通信',
      age: 20,
      user_id: user.user_id
    };
    $scope.submit = function () {
      $scope.register.hackathon_id = $scope.hackathon.id;
      $scope.register.team_name = $scope.register.real_name;
      $scope.submitRegister($scope.register);
    }
  });
