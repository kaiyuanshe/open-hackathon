'use strict';

/**
 * @ngdoc function
 * @name learnangularApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the learnangularApp
 */
angular.module('learnangularApp')
  .controller('AboutCtrl', function ($scope,$cookies) {
    console.log($cookies)
    $cookies.
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
