angular.module('oh.manage.router', [
  'ui.router'
]).config(function($stateProvider, $urlRouterProvider) {

  $stateProvider.state('manage', {
      abstract: true,
      url: '/',
      templateUrl: '/static/partials/manage/manage.html',
      resolve: {
        contacts: function() {
          return {}
        }
      },
      controller: function($scope, $state, NAV) {
        $scope.navLink = function(item) {
          return $state.href(item.state, {
            name: $scope.currentActivity.name
          }, {});
        }
        $scope.currentArea = NAV.manage;
      }
    }).state('manage.edit', {
      url: 'edit/:name',
      templateUrl: '/static/partials/manage/edit.html'
    })
    .state('manage.users', {
      url: 'users/:name',
      templateUrl: '/static/partials/manage/users.html'
    })
    .state('manage.admin', {
      url: 'admin/:name',
      templateUrl: '/static/partials/manage/admin.html'
    })
    .state('manage.organizers', {
      url: 'organizers/:name',
      templateUrl: '/static/partials/manage/organizers.html'
    })
    .state('manage.prizes', {
      url: 'prizes/:name',
      templateUrl: '/static/partials/manage/prizes.html'
    })
    .state('manage.awards', {
      url: 'awards/:name',
      views: {
        '': {
          templateUrl: '/static/partials/manage/awards.html',
          controller: ['$scope', '$stateParams',
            function($scope, $stateParams) {
              //$scope.contact = utils.findById($scope.contacts, $stateParams.contactId);
            }
          ]
        }
      }
    })
    .state('manage.ve', {
      url: 've/:name',
      templateUrl: '/static/partials/manage/ve.html'
    })
    .state('manage.monitor', {
      url: 'monitor/:name',
      templateUrl: '/static/partials/manage/monitor.html'
    })
    .state('manage.cloud', {
      url: 'cloud/:name',
      views: {
        '': {
          templateUrl: '/static/partials/manage/cloud.html',
          controller: ['$scope', '$stateParams', '$state',
            function($scope, $stateParams, $state) {

            }
          ]
        }
      }
    })
    .state('manage.servers', {
      url: 'servers/:name',
      templateUrl: '/static/partials/manage/servers.html'
    })
});
