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

angular.module('oh.controllers', [])
  .controller('MainController', MainController = function($scope, $rootScope, $location, $window, $cookies, $state, $translate, api, activityService, NAV) {
    $scope.isloaded = true;
    $scope.loading = false;

    $rootScope.$on("$stateChangeStart", function(event, toState, toParams, fromState, fromParams) {
      $scope.loading = true;
      var activity = activityService.getCurrentActivity();
      $scope.currentActivity = {
        name: toParams.name
      };
      if (toParams.name === undefined || activity.name == toParams.name) {

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
              $state.go(toState.name, {
                name: toParams.name
              });
            }
          });
          event.preventDefault();
        }
      }
    });

    $rootScope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams) {
      $scope.loading = false;
    });

  })
  .controller('manageController', function($scope, $state, session, NAV) {
    $scope.page = {
      name: ''
    };
    $scope.currentUser = session.user;
    $scope.$on('pageName', function(event, pageName) {
      $scope.page.name = pageName;
      event.preventDefault();
      event.stopPropagation();
    });


    $scope.currentArea = NAV.manage;
    $scope.$emit('pageName', '');
    $scope.isActive = function(item) {
      return {
        active: $state.includes(item.state)
      }
    }

    $scope.navLink = function(item) {
      return $state.href(item.state, {
        name: $scope.currentActivity.name
      }, {});
    }

  })
  .controller('editController', function($rootScope, $scope, $filter, dialog, session, activityService, api, activity, speech) {

    $scope.$emit('pageName', 'SETTINGS.EDIT_ACTIVITY');

    $scope.animationsEnabled = true;

    activity.event_start_time = new Date(activity.event_start_time);
    activity.event_end_time = new Date(activity.event_end_time);
    activity.registration_start_time = new Date(activity.registration_start_time);
    activity.registration_end_time = new Date(activity.registration_end_time);
    activity.judge_start_time = new Date(activity.judge_start_time);
    activity.judge_end_time = new Date(activity.judge_end_time);

    $scope.provider = {
      windows: $filter('isProvider')(activity.config.login_provider, 1),
      github: $filter('isProvider')(activity.config.login_provider, 2),
      qq: $filter('isProvider')(activity.config.login_provider, 4),
      weibo: $filter('isProvider')(activity.config.login_provider, 8),
      alauda: $filter('isProvider')(activity.config.login_provider, 32),
      gitcafe: $filter('isProvider')(activity.config.login_provider, 16),
    };

    activity.config.max_enrollment = parseInt(activity.config.max_enrollment, 10) || 0;

    $scope.open = {
      event_start_time: false,
      event_end_time: false,
      registration_start_time: false,
      registration_end_time: false,
      judge_start_time: false,
      judge_end_time: false
    };

    $scope.modules = activity;

    // $scope.delBanner = function(index) {
    //   $scope.modules.banners.splice(index, 1);
    // }

    // $scope.showAddBannerDialog = function() {
    //   $scope.modules.banners.push('http://image5.tuku.cn/pic/wallpaper/fengjing/shanshuilantian/014.jpg');
    // }

    $scope.showTip = function(level, content) {
      $scope.$emit('showTip', {
        level: level,
        content: content
      });
    }

    $scope.delBanner = function(index) {
      $scope.modules.banners.splice(index, 1);
      api.admin.hackathon.put({
        header: {
          hackathon_name: activity.name
        },
        body: {
          banners: activity.banners
        }
      }, function(data) {
        if (data.error) {
          $scope.showTip(level='tip-danger', content=data.error.friendly_message);
        } else {
          $scope.showTip(level='tip-success', content='删除成功');
        }
      });
    }

    $scope.showAddBannerDialog = function() {
      $scope.modules.banners.push('http://image5.tuku.cn/pic/wallpaper/fengjing/shanshuilantian/014.jpg');
      api.admin.hackathon.put({
        header: {
          hackathon_name: activity.name
        },
        body: {
          banners: activity.banners
        }
      }, function(data) {
        if (data.error) {
          $scope.showTip(level='tip-danger', content=data.error.friendly_message);
        } else {
          $scope.showTip(level='tip-success', content='添加成功');
        }
      });
    }

    $scope.updateDescription = function() {
      api.admin.hackathon.put({
        header: {
          hackathon_name: activity.name
        },
        body: {
          description: activity.description
        }
      }, function(data) {
        if (data.error) {
          $scope.showTip(level='tip-danger', content=data.error.friendly_message);
        } else {
          $scope.showTip(level='tip-success', content='保存成功');
        }
      });
    }

    $scope.providerChange = function(checked, value) {
      if (checked) {
        $scope.modules.config.login_provider = ((+$scope.modules.config.login_provider) || 0) | value;
      } else {
        $scope.modules.config.login_provider = ((+$scope.modules.config.login_provider) || 0) ^ value;
      }

      api.admin.hackathon.config.put({
        header: {
          hackathon_name: activity.name
        },
        body: {
          login_provider: activity.config.login_provider
        }
      }).then(function(data) {
        if (data.error) {
          $scope.showTip(level='tip-danger', content=data.error.friendly_message);
        } else {
          $scope.showTip(level='tip-success', content='登录方式修改成功');
        }
      });
    }

  })
  .controller('usersController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.USERS');

  })
  .controller('adminController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.ADMINISTRATORS');

  })
  .controller('organizersController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.ORGANIZERS');

  })
  .controller('prizesController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.PRIZES');

  })
  .controller('awardsController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.AWARDS');

  })
  .controller('veController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.VIRTUAL_ENVIRONMENT');

  })
  .controller('monitorController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.ENVIRONMENTAL_MONITOR');

  })
  .controller('cloudController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.CLOUD_RESOURCES');

  })
  .controller('serversController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.SERVERS');
  })
  .controller('createController', function($scope, $timeout, $filter, $cookies, $state, FileUploader, dialog, api) {
    var request;
    $scope.wizard = 1;
    $scope.isShowAdvancedSettings = true;

    $scope.activityFormDisabled = false;

    $scope.activity = {
      name: 'aaa',
      status: -1,
      location: '',
      tags: [],
      config: {
        cloud_provide: 0,
        auto_approve: true,
        recycle_enabled: false,
        recycle_minutes: 0,
        pre_allocate_enabled: false,
        pre_allocate_number: 1,
        freedom_team: false,
        login_provider: 63
      }
    }



    $scope.$watch('activity.name', function(newValue, oldValue, scope) {
      if (request && newValue) {
        $timeout.cancel(request);
      }
      $timeout(function() {
        api.admin.hackathon.checkname.get({
          query: {
            name: newValue
          }
        }, function(data) {
          $scope.activityForm.name.$setValidity('rometname', !data);
        });
      }, 400);
    });



    $scope.$watch('wizard', function(newValue, oldValue, scope) {
      if (newValue == 3) {
        api.template.list.get({}).then(function(data) {
          $scope.image_templates = data;
        });
        api.admin.hackathon.template.list.get({
          header: {
            hackathon_name: $scope.activity.name
          }
        }, function(data) {
          $scope.templates = data;
        })
      } else if (newValue == 4) {
        updataActivityStatus(0).then(function(data) {
          if (data.error) {
            $scope.$emit('showTip', {
              level: 'tip-danger',
              content: data.error.friendly_message
            });
          }
        })
      }
    });

    function getConfigs() {
      var configs = [];
      angular.forEach($scope.configs, function(value, key) {
        configs.push({
          key: key,
          value: value
        });
      })
      return configs;
    }


    $scope.activitySubmit = function() {
      angular.forEach($scope.tags, function(value, key) {
        $scope.activity.tags.push(value.text);
      });

      $scope.activityForm.disabled = true;
      api.admin.hackathon.post({
        body: $scope.activity
      }, function(data) {
        if (data.error) {
          if (data.error.code == 412) {
            $scope.activityForm.name.$setValidity('rometname', false);
          } else {
            $scope.$emit('showTip', {
              level: 'tip-danger',
              content: data.error.friendly_message
            });
          }
          $scope.activityForm.disabled = false;
        } else {
          $scope.wizard = 2;
        }
      });
    };


    /*------------------------------------------------------*/
    $scope.notUseCloud = function() {
      api.admin.hackathon.put({
        header: {
          hackathon_name: $scope.activity.name
        },
        body: {
          status: 0
        }
      }).then(function(data) {
        if (data.error) {
          $scope.$emit('showTip', {
            level: 'tip-danger',
            content: data.error.friendly_message
          });
        } else {
          $scope.isShowAdvancedSettings = false;
          $scope.wizard = 4;
        }
      });
    }


    $scope.clondFormSubmit = function() {
      dialog.confirm({
        title: '提示',
        body: '一旦确定服务商就不能在修改！是否确定？',
        icon: 'fa-exclamation',
        size: 'sm',
        status: 'warning'
      }).then(function() {
        $scope.isAzureForm = $scope.clondservices == 1;
        if (!$scope.isAzureForm) {
          api.admin.hackathon.config.put({
            header: {
              hackathon_name: $scope.activity.name
            },
            body: {
              cloud_provide: $scope.clondservices
            }
          }).then(function(data) {
            if (data.error) {
              $scope.$emit('showTip', {
                level: 'tip-danger',
                content: data.error.friendly_message
              });
            } else {
              $scope.wizard = 3;
            }
          });
        }
      })
    };

    /*------------------------------------------------------*/
    $scope.azureFormDisabled = false;
    $scope.azure = {
      management_host: 'management.core.chinacloudapi.cn',
    };

    $scope.azureFormSubmit = function() {
      $scope.azureFormDisabled = true;
      api.admin.azure.post({
        body: $scope.azure,
        header: {
          hackathon_name: $scope.activity.name
        }
      }).then(function(data) {
        if (data.error) {
          $scope.$emit('showTip', {
            level: 'tip-danger',
            content: data.error.friendly_message
          });
          $scope.azureFormDisabled = false;
        } else {
          $scope.wizard = 3;
        }
      });
    };
    /*------------------------------------------------------*/

    var uploader = $scope.uploader = new FileUploader({
      url: api.template.file.post._path_,
      headers: {
        token: $cookies.get('token')
      },
      autoUpload: true
    });

    uploader.filters.push({
      name: 'templateFilter',
      fn: function(item, options) {
        return /js|json|txt$/i.test(item.name);
      }
    });
    uploader.onWhenAddingFileFailed = function(item, filter, options) {
      $scope.$emit('showTip', {
        level: 'tip-warning',
        content: '模板文件必须是txt、js、json后缀名'
      });
    };
    uploader.onAfterAddingFile = function(fileItem) {
      //console.info('onAfterAddingFile', fileItem);
    };
    uploader.onAfterAddingAll = function(addedFileItems) {
      //console.info('onAfterAddingAll', addedFileItems);
    };
    uploader.onBeforeUploadItem = function(item) {
      //console.info('onBeforeUploadItem', item);
    };
    uploader.onProgressItem = function(fileItem, progress) {
      //console.info('onProgressItem', fileItem, progress);
    };
    uploader.onProgressAll = function(progress) {
      //console.info('onProgressAll', progress);
    };
    uploader.onSuccessItem = function(fileItem, response, status, headers) {
      //console.info('onSuccessItem', fileItem, response, status, headers);
    };
    uploader.onErrorItem = function(fileItem, response, status, headers) {
      //console.info('onErrorItem', fileItem, response, status, headers);
    };
    uploader.onCancelItem = function(fileItem, response, status, headers) {
      //console.info('onCancelItem', fileItem, response, status, headers);
    };
    uploader.onCompleteItem = function(fileItem, data) {
      if (data.error) {
        $scope.$emit('showTip', {
          level: 'tip-danger',
          content: data.error.friendly_message
        });
      } else {
        api.template.list.get({}).then(function(data) {
          $scope.image_templates = data;
        });
      }
    };
    uploader.onCompleteAll = function() {
      $scope.file = '';
    };

    console.info('uploader', uploader);

    $scope.oneAtATime = true;
    $scope.templates = [];
    $scope.search = {
      status: '-1'
    }
    $scope.searchTemplates = function() {
      api.template.list.get({
        query: $scope.search
      }).then(function(data) {
        $scope.image_templates = data;
      });
    }

    $scope.testchange = function($event, id) {
      var result
      if ($event.target.checked) {
        result = api.admin.hackathon.template.post({
          body: {
            template_id: id
          },
          header: {
            hackathon_name: $scope.activity.name
          }
        });
      } else {
        result = api.admin.hackathon.template.delete({
          query: {
            template_id: id
          },
          header: {
            hackathon_name: $scope.activity.name
          }
        });
      }
      result.then(function(data) {
        if (data.error) {
          $scope.$emit('showTip', {
            level: 'tip-danger',
            content: data.error.friendly_message
          });
        } else {
          $scope.templates = data;
        }

      })
    }

    $scope.expression = function($event) {
      $event.stopPropagation();
    }

    $scope.isChecked = function(list, id) {
      var obj = $filter('filter')(list, {
        id: id
      }, true);
      return obj.length > 0 ? true : false;
    }
    $scope.templateSubmit = function() {
      if ($scope.templates.length > 0) {
        $scope.wizard = 4;
      } else {
        $scope.$emit('showTip', {
          level: 'tip-danger',
          content: '请绑定模板'
        });
      }
    }

    /*------------------------------------------------------*/

    function updataActivityStatus(status) {
      return api.admin.hackathon.put({
        body: {
          status: status
        },
        header: {
          hackathon_name: $scope.activity.name
        }
      })
    }


    $scope.onlineDisabled = false;
    $scope.online = function() {
      $scope.onlineDisabled = true;
      api.admin.hackathon.canonline.get({
        header: {
          hackathon_name: $scope.activity.name
        }
      }).then(function(data) {
        console.log(data);
        if (data.message) {
          updataActivityStatus(1).then(function(data) {
            if (data.error) {
              $scope.$emit('showTip', {
                level: 'tip-danger',
                content: data.error.friendly_message
              });
              $scope.onlineDisabled = false;
            } else {
              $state.go('manage.edit', {
                name: $scope.activity.name
              });
            }
          });
        } else {
          $scope.onlineDisabled = false;
          $scope.$emit('showTip', {
            level: 'tip-danger',
            content: '证书授权失败，请检验SUBSCRIPTION ID是否正确。'
          });
        }
      })
    }
  });
