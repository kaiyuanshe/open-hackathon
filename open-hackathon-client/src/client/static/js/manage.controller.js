angular.module('oh.controllers', [])
  .controller('MainController', MainController = function($scope, $rootScope, $location, $window, $cookies, $state, api, activityService, NAV) {
    $scope.isloaded = true;
    $scope.loading = false;
    $scope.currentActivity = {
      name: 'sss'
    };


    $rootScope.$on("$stateChangeStart", function(event, toState, toParams, fromState, fromParams) {
      var activity = activityService.getCurrentActivity();

      if (activity.name == toParams.name) {

      } else {
        activity = activityService.getByName(toParams.name)
        if (activity.name != undefined) {
          activity.name = toParams.name;



          activityService.setCurrentActivity(activity);
          $scope.$emit('changeCurrenActivity', activity);
        } else {
          api.admin.hackathon.get({
            header: {
              hackathon_name: toParams.name
            }
          }).then(function(data) {
            if (data.error) {
              $state.go('404');
            } else {
              activityService.add(data);
            }
          });
          event.preventDefault();
          return false;
        }
      }
      console.log(event)
    });


    $scope.$on('changeCurrenActivity', function(e, activity) {
      $scope.currentActivity = activity;
      e.preventDefault()
    });

    $scope.$watch('currentActivity', function(newValue, oldValue, scope) {
      console.log(newValue, oldValue);
    }, true);

    $scope.currentArea = NAV.manage;

    $rootScope.$on('getActivity', function(event, activities) {
      console.log('111111111111111111');
      $scope.activities = activityService.getAll();
    })

    $scope.navLink = function(item) {
      return $state.href(item.state, {
        name: $scope.currentActivity.name
      }, {});
    }

    $scope.isActive = function(item) {

      return {
        active: $state.includes(item.state)
      }
    }
    $scope.navClass = function(item) {

      //console.log($state.current.name);
    }

    $scope.stateGo = function(state) {
      // $state.go(state, {
      //     name: $scope.currentActivity.name
      // })

    }
    $scope.changeActivity = function() {
      // activityService.getAll().then(function(data) {
      //     console.log(data);
      // })
      $scope.currentActivity.name = 333;

    }

  })
  .controller('EditController', function($rootScope, $scope, activityService) {
    // activityService.getAll().then(function(data) {
    //     console.log(data);
    // })
    // $rootScope.page = {
    //   name: 'SETTINGS.ADMINISTRATORS'
    // }
    $scope.showTip = function() {
      $scope.$emit('showTip', {
        level: 'tip-success',
        content: '保存成功'
      });
    }
  });
