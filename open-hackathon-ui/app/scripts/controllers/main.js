'use strict';

/**
 * @ngdoc function
 * @name hackathonApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the hackathonApp
 */
angular.module('hackathonApp')
  .controller('MainCtrl', function ($scope) {
    $scope.githublogin = function () {
      var l, t;
      l = (screen.width - 600) / 2;
      t = (screen.height - 400) / 2;

      var url = "https://github.com/login/oauth/authorize?client_id=a10e2290ed907918d5ab&redirect_uri=http://hackathon.chinacloudapp.cn/github&scope=user"
      window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=600, height=500, top=' + t + ', left=' + l)

    };
    $scope.qqlogin = function () {
      var l, t;
      l = (screen.width - 600) / 2;
      t = (screen.height - 400) / 2;
      var url = 'https://graph.qq.com/oauth2.0/authorize?client_id=101157515&redirect_uri=http://hackathon.chinacloudapp.cn/qq&scope=get_user_info&state=openhackathon&response_type=code';
      window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=600, height=500, top=' + t + ', left=' + l)
    };
    $scope.gitcafelogin = function () {

    };
  })
  .controller('HeaderCtr',function($scope){
    $scope.isHackathon = true;
  });


