'use strict';

/**
 * @ngdoc function
 * @name hackathonApp.controller:SettingsCtrl
 * @description
 * # SettingsCtrl
 * Controller of the hackathonApp
 */
angular.module('hackathonApp')
  .controller('SettingsCtrl', function ($scope,$cookieStore) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
