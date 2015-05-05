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
 * Created by v-boguan on 2015/5/4.
 */


angular.module('oh.app')
  .factory('RouteFilter', function Routefilter() {
    var filters = [];

    var getFilter = function (route) {
      for (var i = filters.length - 1; i >= 0; i--) {
        for (var j = filters[i].routes.length - 1; j >= 0; j--) {
          if (matchRoute(filters[i].routes[j], route)) {
            return filters[i];
          }
        }
      }
    }

    var matchRoute = function (filterRoute, route) {
      if (route instanceof RegExp) {
        return route.test(filterRoute);
      } else {
        return route === filterRoute;
      }
    }

    return {
      register: function (routes, callback) {
        filters.push({
          routes: routes,
          callback: callback
        });
      },
      run: function (route) {
        var filter = getFilter(route);
        if (filter != null) {
          filter.callback();
        }
      }
    }
  });
