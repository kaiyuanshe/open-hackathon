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

angular.module('oh.api', [])
  .factory('api', function($rootScope, $http, $window, $cookies, $q) {
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
        var methodName = obj.toUpperCase(),method = obj.toUpperCase();

        getCmd[methodName] = function(options, callback) {
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
            method: method,
            url: name,
            params: options.query,
            data: options.body,
            headers: options.header
          };
          $http(config)
            .success(function(data, status, headers, config) {
              if(data.error){
                if(data.error.code===401){
                  location.href = '/login';
                }
              }
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
        getCmd[methodName]._path_ = name;
        return getCmd[methodName];
      }
    }

    return API($window.CONFIG.apiconfig.api, $window.CONFIG.apiconfig.proxy + '/api');
  }).factory('uploadService', function($rootScope, $http, $window, $cookies) {
    return {
      uploadOneFile: function(fileType, formData, getUrlFunc) {
        $http.post($window.CONFIG.apiconfig.proxy + "/api/user/file?file_type=" + fileType, formData, {
          transformRequest: angular.identity,
          headers: {'Content-Type': undefined, token: $cookies.get('token')}
        }).success(function(data, status, headers, config){
          if ("files" in data && data["files"].length > 0 && "url" in data["files"][0])
            return getUrlFunc(data["files"][0]["url"]);
          return getUrlFunc("");
        }).error(function(data, status, headers, config){
          return getUrlFunc("");
        });
      },
      uploadFiles: function(fileType, formData, successFunc, errorFunc) {
        $http.post($window.CONFIG.apiconfig.proxy + "/api/user/file?file_type=" + fileType, formData, {
          transformRequest: angular.identity,
          headers: {'Content-Type': undefined, token: $cookies.get('token')}
        }).success(successFunc(data, status, headers, config)
        ).error(errorFunc(data, status, headers, config));
      }
    }
  }).factory('activityService', function($rootScope, $q, api) {
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
        var activity = {};
        angular.forEach(activity_list, function(value, key) {
          if (value.name == name) {
            activity = value;
            return
          }
        });
        return activity;
      },
      setCurrentActivity: function(activity) {
        return currentActivity = activity;
      },
      getCurrentActivity: function() {
        return currentActivity;
      }
    }
  }).factory('authService', function(api, session) {

    var user = api.user.get().then(function(data) {
      session.create(data)
      return data;
    })

    var factory = {};
    factory.getUser = function() {
      return user;
    };
    return factory;
  }).service('session', function() {
    this.create = function(user) {
      this.user = user;
    };
    this.destroy = function() {
      this.user = undefined;
    };
    return this;
  }).factory('dialog', function($uibModal, VERSION) {

    function open(modal) {
      var modalInstance = $uibModal.open({
        animation: true,
        templateUrl: modal.url,
        size: modal.size + ' modal-' + modal.status,
        resolve: modal.resolve,
        controller: modal.controller
      });
      return modalInstance;
    }

    function base(modal) {
      if (modal.icon) {
        modal.body = '<p class="dialog-centent"><label class="icon icon-md icon-' + modal.status + '"><i class="fa ' + modal.icon + '"></i></label><label class="dialog-message">' + modal.body + '</label></p>'
      }
      modal.ok = modal.ok || function() {return ''};
      modal.controller = function($scope, $uibModalInstance) {
        $scope.title = modal.title;
        $scope.body = modal.body;
        $scope.ok = function() {
          $uibModalInstance.close(modal.ok());
        };
        $scope.cancel = function() {
          $uibModalInstance.dismiss('cancel');
        };
      }
      return open(modal).result;
    }

    this.alert = function(modal) {
      modal.url = 'manage/template/dialogs/alert.html';
      return base(modal);
    }

    this.confirm = function(modal) {
      modal.url = 'manage/template/dialogs/confirm.html';
      return base(modal);
    }

    this.customize = function(modal) {
      open(modal);
    }
    return this;
  }).factory('speech', function() {

    var path = '/static/sound/';

    function audio(name) {
      var a = document.createElement('audio');
      a.setAttribute('src', path + name);
      a.addEventListener('load', function() {
        a.play()
      }, !0);
      a.pause();
      a.play();
    }

    this.alert = function() {
      audio('voice_alert.mp3');
    }
    this.off = function() {
      audio('voice_off.mp3');
    }
    this.on = function() {
      audio('voice_on.mp3');
    }
    this.tip = function() {
      audio('smallbox.mp3');
    }
    return this;
  }).factory('util', function($rootScope) {
    var util = $rootScope.util = {
      getUserPrimaryEmail: function(user) {
        if(! user.emails)
          return ;

        var email;
        for(email in user.emails) {
          if(email.primary_email)
            return email.email;
        }

        // default use first email as primary email
        return user.emails[0].email;
      }
    };

    return util;
  });
