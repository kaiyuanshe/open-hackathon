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
    width = width || 600;
    var l, t;
    l = (screen.width - width ) / 2;
    t = (screen.height - 400) / 2;
    window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=' + width + ', height=500, top=' + t + ', left=' + l);
  }

  $scope.githublogin = function () {
    var url = 'https://github.com/login/oauth/authorize?' +
      $.param($scope.config.sociallogin.github);
    openWindow(url);
  };
  $scope.qqlogin = function () {
    var url = 'https://graph.qq.com/oauth2.0/authorize?' +
      $.param($scope.config.sociallogin.qq);
    openWindow(url);
  };
  $scope.gitcafelogin = function () {
    var url = 'https://api.gitcafe.com/oauth/authorize?' +
      $.param($scope.config.sociallogin.gitcafe);
    openWindow(url, 980);
  };
  $scope.weibologin = function () {
    var url = 'https://api.weibo.com/oauth2/authorize?' +
      $.param($scope.config.sociallogin.weibo);
    openWindow(url);
  }
});


