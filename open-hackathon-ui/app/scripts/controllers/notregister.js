'use strict';
/**
 * @namespace hackathonApp
 * @author <ifendoe@gmail.com>
 * @version 0.0.1
 * Created by Boli Guan on 15-3-12.
 */

/**
 * @ngdoc function
 * @name hackathonApp.controller:notregister
 * @description
 * @author <ifendoe@gmail.com>
 * # notregisterCtrl
 * Controller of the hackathonApp
 */
angular.module('hackathonApp')
  .controller('notregisterCtrl', function ($scope, $timeout) {
    //alert(1111111);
    $scope.second = 5;
   // alert('dfsdf');

    var timer = $timeout(function(){
      console.log( "Timeout executed", Date.now());
      $timeout.
    },1000);
    timer.then(function(){
      console.log( "Timer resolved!", Date.now() );
    },function(){
      console.log( "Timer rejected!", Date.now() );
    })
    $scope.clear= function(){
      console.log('111111111')
      $timeout.cancel( timer );
    }
  });
