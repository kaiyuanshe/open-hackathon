/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

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
  .factory('API', function ($http, $cookies, state, log) {
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
        return getCmd[obj] = function (options, callback) {
          var _params = {
            query: null,
            body: null,
            header: {}
          };
          callback = callback || new Function();
          if ($.isFunction(options)) {
            callback = options;
            options = {};
          }
          options = $.extend(_params, options);
          var url = name;
          options.header.token = $cookies.get('token') || '';
          log.time(name);
          return $http({
            method: obj,
            url: url,
            params: options.query,
            //contentType: obj == 'get' ? 'application/x-www-form-urlencoded' : 'application/json',
            headers: options.header,
            data: options.body
          }).success(function (data) {
            log.timeEnd(name);
            callback(data)
          }).error(function (data) {
            callback({error: true, data: data});
          })
        }
      }
    }

    return API(config.api, config.url + '/api');
  });



