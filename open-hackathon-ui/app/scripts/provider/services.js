// -----------------------------------------------------------------------------------
// Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
//  
// The MIT License (MIT)
//  
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//  
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//  
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
// -----------------------------------------------------------------------------------

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


