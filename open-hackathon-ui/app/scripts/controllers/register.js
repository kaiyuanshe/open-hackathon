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
  .controller('register.controller', function ($scope, $rootScope, $cookieStore, $state, API) {
    $scope.hackathon = {
      isRegister: false
    };
    $scope.isLoad = true;
    $scope.registerForm = {show: false};
    $scope.isRegister = true;
    $scope.showRegister = function () {
      $scope.registerForm.show = true;
    }
    $scope.dimensional = 'http://qr.liantu.com/api.php?bg=f2f2f2&fg=101010&gc=101010&el=l&w=150&m=10&text=' + location.href;
    $scope.hideRegister = function () {
      $scope.registerForm.show = false;
    }



    $scope.check_status = ['您的报名正在审核中，请等待。', '您的报名已经审核已通过。', '您的报名已被拒绝，如有疑问请联系主办方。'];
    API.hackathon.get({header: {hackathon_name: config.name}}, function (data) {
      var User = $cookieStore.get('User') || '';
      var isExpired = data.end_time < Date.now();
      var message = '';
      $scope.hackathon = data;
      if (User) {
        $scope.hackathon.isRegister = (data.check_register && !isExpired && (User.status & 1) != 1);
        if (isExpired) {
          message = '活动已经结束';
        } else if ((User.status & 1) == 1) {
          API.register.get({query:{hid:$scope.hackathon.id,uid:User.id}},function(data){
            User.check_status = data.status || 0;
            $cookieStore.put('User', User)
            $scope.hackathon.message = $scope.check_status[User.check_status];
          });
        }
      }
      $scope.isLoad = false;
      $scope.hackathon.message = message;
    });

  }).controller('registerFormController', function ($scope, $cookieStore, API) {
    $scope.register = {
      sex: 1,
      career_type: '计算机/互联网/通信',
      age: 20
    };
    $scope.id = $scope.hackathon.id;
    var User = $cookieStore.get('User');

    $scope.submit = function () {
      $scope.register.hackathon_id = $scope.hackathon.id;
      API.register.post({body: $scope.register}, function (data) {
        User.status |= 1;
        User.user_id = User.id;
        User.check_status = data.status || 0;
        $cookieStore.put('User', User)
        $scope.hackathon.isRegister = false;
        $scope.hackathon.message = $scope.check_status[User.check_status];
      });
    }
  });
