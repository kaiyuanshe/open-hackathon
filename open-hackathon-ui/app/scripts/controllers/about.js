'use strict';

/**
 * @ngdoc function
 * @name learnangularApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the learnangularApp
 */
angular.module('learnangularApp')
  .controller('AboutCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
