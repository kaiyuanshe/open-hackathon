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
 * Created by Boli Guan on 15-3-12.
 */

/**
 * @ngdoc function
 * @name oh.controllers:settings.controller
 * @description
 * # settings.controller
 * Controller of the settings.controller
 */
angular.module('oh.controllers')
  .controller('settings.controller', function ($scope, $cookieStore, $state, API) {
    $scope.type = {name: ''};
    var User = $cookieStore.get('User') || '';
    if (!User) {
      $state.go('index');
    } else if ((User.status & 8) == 8) {
      $state.go('index.register');
    } else if ((User.status & 128) == 128) {
      if ((User.status & 1) != 1) {
        $state.go('index.register');
      } else if (User.experiments.length > 0) {
        $state.go('index.hackathon');
      }
    }
    API.template.list.get({query: {hackathon_name: $scope.config.name}}, function (data) {
      var _temp = data;
      API.register.get({query: {hid: data.id, uid: User.id}}, function (data) {
        User.check_status = data.status || 0;
        $cookieStore.put('User', User);
        if (User.check_register != 1) {
          $state.go('index.register');
        } else {
          $scope.templates = _temp;
          if (data.length > 0) {
            $scope.type.name = _temp[0].name
          }
        }
      });
    });

    $scope.submit = function () {
      API.user.experiment.post({
        body: {cid: $scope.type, hackathon: $scope.config.name}
      }, function (data) {
        $state.go('index.hackathon');
      });
    }

  });
