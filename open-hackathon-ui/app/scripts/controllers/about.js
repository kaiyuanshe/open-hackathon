'use strict';

/**
 * @ngdoc function
 * @name hackathonApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the hackathonApp
 */
angular.module('hackathonApp')
  .controller('AboutCtrl', function ($scope,$cookieStore) {
    console.log($cookieStore);
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
