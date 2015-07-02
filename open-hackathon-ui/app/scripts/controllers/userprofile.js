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
 * @namespace oh.controllers
 * @author <ifendoe@gmail.com>
 * @version 0.0.1
 * Created by Boli Guan on 15-4-15.
 */
angular.module('oh.controllers')
  .controller('userprofile.controller', function ($scope, $stateParams,$cookies, state, Authentication, API) {
    var user = Authentication.getUser();
    if (!user) {
      state.go('index');
    }
    $scope.user = user;
    var isProfile = false
    API.user.profile.get().then(function (res) {
      if (!res.data.error) {
        $scope.profile = res.data;
        isProfile = true;
      }
    })

    var def = undefined;
    $scope.submit = function () {
      if (isProfile) {
        def = API.user.profile.put({body: $scope.profile});
      } else {
        def = API.user.profile.post({body: $scope.profile});
      }
      def.then(function (res) {
        var hackathon_name = $cookies.get('redirectHakathonName');
        state.go('index.register', {hackathon_name: hackathon_name})
      })
    }
  })
