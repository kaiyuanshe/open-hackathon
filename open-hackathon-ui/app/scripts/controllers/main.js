'use strict';

/**
 * @ngdoc function
 * @name learnangularApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the learnangularApp
 */
angular.module('learnangularApp')
  .controller('MainCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
