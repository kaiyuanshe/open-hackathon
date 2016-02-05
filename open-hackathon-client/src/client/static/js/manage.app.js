/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   manage.app.js                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: anonymous <anonymous@student.42.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2016/01/27 20:11:57 by anonymous         #+#    #+#             */
/*   Updated: 2016/02/05 16:46:03 by anonymous        ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

angular.module('manageView', [
    'ngCookies',
    'ngSanitize',
    'bootstrap',
    'ui.router',
    'oh.pages',
    'oh.api',
    'oh.controllers',
    'oh.directives',
    'ui.bootstrap.dropdown',
    'pascalprecht.translate',
    'bw.paging'
  ])
  .config(['$locationProvider', '$translateProvider', '$stateProvider', '$urlRouterProvider', 'MANAGE_PAGES', function($locationProvider,
    $translateProvider,
    $stateProvider,
    $urlRouterProvider,
    MANAGE_PAGES) {
    $translateProvider.useStaticFilesLoader({
        prefix: '/static/languages/',
        suffix: '.json'
      }).preferredLanguage('zh-de')
      .useSanitizeValueStrategy()
      .useLocalStorage();

    $urlRouterProvider.otherwise('');

    $stateProvider.state('manage', {
      url: '/',
      templateUrl: '/static/partials/manage/main.html'
    });
    $stateProvider.state('404', {
      url: '/404',
      templateUrl: '/static/partials/manage/404.html'
    });
    angular.forEach(MANAGE_PAGES.pages, function(value, key) {
      $stateProvider.state(value.name, {
        url: value.url,
        templateUrl: value.path
      });
    });

    $locationProvider.html5Mode(true).hashPrefix('!');

  }]).run(function($rootScope, $state, api, activityService) {
    //activityService.load();



    $rootScope.$on('showTip', function(event, obj) {
      $rootScope.tip = obj;
      event.preventDefault();
      event.stopPropagation();
    });


  });



angular.module('oh.providers ', [])
  .provider();



angular.module('oh.api', [])
  .factory('api', function($rootScope, $http, $window, $cookies, $q) {
    var methods = {
      get: 'GET',
      post: 'POST',
      put: 'PUT',
      del: 'DELETE'
    };

    function API(obj, name) {
      var key;
      var getCmd = {};
      if (obj instanceof Array) {
        for (key in obj) {
          getCmd[obj[key]] = API(obj[key], name)
        }
        return getCmd;
      } else if (obj instanceof Object) {
        for (key in obj) {
          if (obj.hasOwnProperty(key)) {
            if (key == '') {
              getCmd = API(obj[key], name)
            } else {
              getCmd[key] = API(obj[key], name + '/' + key);
            }
          }
        }
        return getCmd;
      } else {
        return getCmd[obj] = function(options, callback) {
          var deferred = $q.defer();
          var _params = {
            query: {},
            body: {},
            header: {},
          };
          callback = callback || new Function();
          if (angular.isFunction(options)) {
            callback = options;
            options = {};
          }
          options = angular.extend(_params, options);
          options.header.token = $cookies.get('token');

          var config = {
            method: methods[obj],
            url: name,
            params: options.query,
            data: options.body,
            headers: options.header
          };
          $http(config)
            .success(function(data, status, headers, config) {
              callback(data);
            }).error(function(data, status, headers, config) {
              console.log(data);
            }).then(function(data) {
              deferred.resolve(data.data);
            }, function(data) {
              console.log(data);
            });
          return deferred.promise;
        }
      }
    }

    return API($window.CONFIG.apiconfig.api, $window.CONFIG.apiconfig.proxy + '/api');
  })
  .factory('activityService', function($rootScope, $q, api) {
    var activity_list = [],
      isLoad = false,
      currentActivity = {};

    return {
      load: function() {
        if (!isLoad) {
          api.admin.hackathon.list.get().then(function(data) {
            activity_list = data;
            isLoad = true;
            $rootScope.$emit('getActivity', activity_list);
          });
        }
      },
      reload: function() {
        isLoad = false;
        activity_list = [];
        this.load();
      },
      add: function(obj) {
        if (angular.isArray(obj)) {
          activity_list = activity_list.concat(obj)
        } else {
          activity_list.push(obj);
        }
      },
      update: function(activity) {
        angular.forEach(activity_list, function(value, key) {
          if (value.name == activity.name) {
            activity_list[key] = activity;
            return true;
          }
        });
        return false;
      },
      getAll: function() {
        return activity_list;
      },
      getById: function(id) {
        angular.forEach(activity_list, function(value, key) {
          if (value.id == id) {
            return value;
          }
        });
        return {};
      },
      getByName: function(name) {
        angular.forEach(activity_list, function(value, key) {
          if (value.name == name) {
            return value;
          }
        });
        return {};
      },
      setCurrentActivity: function(activity) {
        return currentActivity = activity;
      },
      getCurrentActivity: function() {
        return currentActivity;
      }
    }
  });
