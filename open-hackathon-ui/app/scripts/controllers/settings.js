'use strict';
/**
 * @namespace oh.controllers
 * @author <ifendoe@gmail.com>
 * @version 0.0.1
 * Created by Boli Guan on 15-3-12.
 */

/**
 * @ngdoc function
 * @name oh.controllers:settings.controller
 * @description
 * # settings.controller
 * Controller of the settings.controller
 */
angular.module('oh.controllers')
  .controller('settings.controller', function ($scope, $cookieStore, $state, API) {
    $scope.type = 'ssh';
    var User = $cookieStore.get('User') || '';
    if (!User) {
      $state.go('index');
    } else if (!User.register_state) {
      $state.go('notregister');
    } else if (User.experiments.length > 0) {
      $state.go('index.hackathon');
    }
    $scope.submit = function () {
      API.user.experiment.post(JSON.stringify({cid: $scope.type, hackathon: $scope.config.name}), function (data) {
        $state.go('index.hackathon');
      });
    }
  });
