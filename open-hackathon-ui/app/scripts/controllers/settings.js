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
  .controller('settings.controller', function ($scope,$location, Authentication, API) {
    $scope.isLoading = true;
    Authentication.settings(function (data) {
      API.hackathon.template.get({header: {hackathon_name: config.name}}, function (data) {
        $scope.isLoading = false;
        if (data.error) {
          $scope.error = data;
        } else if (data.length > 0) {
          $scope.isSubmit = true;
          $scope.templates = data;
          $scope.type = {name: data[0].name};
        } else {
          $scope.error = {error: true, data: {message: '暂无模板'}}
        }
      });
    })
    $scope.submit = function () {
      API.user.experiment.post({
        body: {template_name: $scope.type.name, hackathon: config.name}
      }, function (data) {
        if (data.error) {
          $location.path('error');
        } else {
          $location.path('hackathon');
        }
      });
    }
  });
