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
 * Created by v-boguan on 2015/5/3.
 */

angular.module('oh.app')
  .factory('Authentication', function Authentication($q, $location, $cookieStore, API) {
    var authenticatedUser = null;

    /**
     * Get user information
     * @method getUser
     * @returns {{avatar_url: string, create_time: string, email: {create_time: number, email: string, id: number, name: string, primary_email: number, update_time: null, user_id: number, verified: number}[], id: number, last_login_time: string, name: string, nickname: string, online: number}}
     */
    function getUser() {
      return $cookieStore.get('User') || {};
    }

    /**
     * hackathon Page load
     * @method hackathon
     * @param {function}
     */
    function hackathon(callback) {
      var user = this.getUser();
      if (user) {
        API.user.hackathon.get({header: {hackathon_name: config.name}}, function (data) {
          if (data.error) {
            $location.path('error');
          } else {
            if (data.hackathon.status != 1) {
              $location.path('error')
            } else {
              if (data.registration) {
                if (data.registration.status == 0 || data.registration.status == 2) {
                  $location.path('register');
                } else if (data.registration.status == 3 && data.hackathon.basic_info.auto_approve == 0) {
                  $location.path('register');
                } else if (!data.experiment) {
                  $location.path('settings');
                } else {
                  callback(data);
                }
              } else {
                $location.path('register');
              }
            }
          }
        });
      } else {
        $location.path('error');
      }
    }

    /**
     * settings Page load
     * @method settings
     * @param {function}
     */
    function settings(callback) {
      var user = this.getUser();
      if (user) {
        API.user.hackathon.get({header: {hackathon_name: config.name}}, function (data) {
          if (data.error) {
            $location.path('error');
          } else {
            if (data.hackathon.status != 1) {
              $location.path('error');
            } else {
              if (data.registration) {
                if (data.registration.status == 0 || data.registration.status == 2) {
                  $location.path('register');
                } else if (data.registration.status == 3 && data.hackathon.basic_info.auto_approve == 0) {
                  $location.path('register');
                } else if (data.experiment) {
                  $location.path('hackathon');
                } else {
                  callback(data);
                }
              } else {
                $location.path('register');
              }
            }
          }
        });
      } else {
        $location.path('error');
      }
    }

    /**
     * register Page load
     * @method register
     * @param {function}
     */
    function register(callback) {
      var user = this.getUser();
      if (user) {
        API.user.hackathon.get({header: {hackathon_name: config.name}}, function (data) {
          if (data.error) {
            $location.path('error');
          } else {
            callback(data);
          }
        });
      } else {
        API.hackathon.get({header: {hackathon_name: config.name}}, function (data) {
          if (data.error) {
            $location.path('error');
          } else {
            callback(data);
          }
        });
      }
    }

    return {
      getUser: getUser,
      hackathon: hackathon,
      settings: settings,
      register: register
    }
  });




