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
  var l, t;
  l = (screen.width - 600) / 2;
  t = (screen.height - 400) / 2;
  $scope.githublogin = function () {
    var url = "https://github.com/login/oauth/authorize?client_id=a10e2290ed907918d5ab&redirect_uri=http://hackathon.chinacloudapp.cn/github&scope=user";
    window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=600, height=500, top=' + t + ', left=' + l);
  };
  $scope.qqlogin = function () {
    var url = 'https://graph.qq.com/oauth2.0/authorize?client_id=101157515&redirect_uri=http://hackathon.chinacloudapp.cn/qq&scope=get_user_info&state=openhackathon&response_type=code';
    window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=600, height=500, top=' + t + ', left=' + l);
  };
  $scope.gitcafelogin = function () {
    var url = 'https://graph.qq.com/oauth2.0/authorize?client_id=101157515&redirect_uri=http://hackathon.chinacloudapp.cn/qq&scope=get_user_info&state=openhackathon&response_type=code';
    window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=600, height=500, top=' + t + ', left=' + l);
  };
});


