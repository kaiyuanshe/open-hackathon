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
 * @name oh.controllers:oh.header.controller
 * @description
 * @author <ifendoe@gmail.com>
 * # oh.header.controller
 * Controller of the oh.header.controller
 */
angular.module('oh.controllers')
  .controller('oh.hackathon.controller', function ($scope, $rootScope,$location, Authentication) {
    $rootScope.hackathon = true;
    Authentication.hackathon(function (data) {
      $scope.workData = data;
    });

    $scope.status = {
      isopen: false
    }

    $scope.toggled = function (open) {
      console.log('dropdown is now', open);
    }
    $scope.toggledDropdown = function ($event) {
      $event.preventDefult();
      $event.stopPropagation();
      $event.status.isopen = !$scope.status.isopen;
    }
    $scope.$on('$destroy', function (event) {
        // $rootScope.hackathon = false;
      }
    );
  });

