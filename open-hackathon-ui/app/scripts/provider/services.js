'use strict';
/**
 * @namespace oh.services
 * @author <ifendoe@gmail.com>
 * @version 0.0.1
 * Created by Boli Guan on 15-3-12.
 */

/**
 * @ngdoc function
 * @name oh.services:API
 * @description
 * # API
 * Controller of the API
 */
angular.module('oh.services', [])
  .run(function ($http, $rootScope) {
    $http.get('/config')
      .success(function (data) {
        $rootScope.config = data;
      })
      .error(function (data) {
        console.log(data);
      })
  })
  .factory('API', function ($http, $cookieStore, $rootScope) {
    var methods = {get: 'GET', post: 'POST', put: 'PUT', del: 'DELETE'};

    function scan(obj, name) {
      var key;
      var getCmd = {};
      if (obj instanceof Array) {
        for (key in obj) {
          getCmd[obj[key]] = scan(obj[key], name)
        }
        return getCmd;
      } else if (obj instanceof Object) {
        for (key in obj) {
          if (obj.hasOwnProperty(key)) {
            if (key == '_self') {
              getCmd = scan(obj[key], name)
            } else {
              getCmd[key] = scan(obj[key], name + '/' + key);
            }
          }
        }
        return getCmd;
      } else {
        return getCmd[obj] = function (query, headers, callback) {
          if (!callback) {
            callback = headers || function () {
            };
            headers = {};
          }
          headers.token = ($cookieStore.get('User') || '' ).token;
          var options = {
            method: methods[obj],
            url: name,
            contentType: obj == 'get' ? 'application/x-www-form-urlencoded' : 'application/json',
            headers: headers,
            data: query,
            success: function (data) {
              callback(data)
            },
            error: function (data) {
              callback(data)
            }
          }
          $.ajax(options);
        }
      }
    }

    var API = scan($rootScope.config.api, $rootScope.config.url + '/api');
    return API;
  });


