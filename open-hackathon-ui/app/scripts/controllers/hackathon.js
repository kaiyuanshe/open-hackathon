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
  .controller('oh.header.controller', function ($scope, $rootScope, $cookieStore, $state) {
    if (!$cookieStore.get('User')) {
      $state.go('index');
    }
    $rootScope.hackathon = true;
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
        $rootScope.hackathon = false;
      }
    );
  });

