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
 * Created by Boli Guan on 15-3-10.
 */

/**
 * @ngdoc function
 * @name oh.controllers:main.controller
 * @description
 * # main.controller
 * Controller of the main.controller
 */
var s = angular.module('oh.controllers', []);
s.controller('main.controller', function ($scope) {

  function openWindow(url, width) {
//    width = width || 600;
//    var l, t;
//    l = (screen.width - width ) / 2;
//    t = (screen.height - 400) / 2;
//    window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=' + width + ', height=500, top=' + t + ', left=' + l);
    window.location.href = url
  }

  $scope.githublogin = function () {
    var url = config.social.github +
      $.param(config.sociallogin.github);
    openWindow(url);
  };
  $scope.qqlogin = function () {
    var url = config.social.qq +
      $.param(config.sociallogin.qq);
    openWindow(url);
  };
  $scope.gitcafelogin = function () {
    var url = config.social.gitcafe +
      $.param(config.sociallogin.gitcafe);
    openWindow(url, 980);
  };
  $scope.weibologin = function () {
    var url = config.social.weibo +
      $.param(config.sociallogin.weibo);
    openWindow(url);
  }
});


