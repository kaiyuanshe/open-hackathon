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
/*
          // if (data.status == -1) {
              //   $state.go('create', {
              //     name: toParams.name
              //   });
              // } else {
              $state.go(toState.name, {
                name: toParams.name
              });
              //}*/
angular.module('oh.controllers', [])
  .controller('MainController', MainController = function($scope, $rootScope, $state, $q, api, activityService) {
    $scope.isloaded = true;

    $scope.loading = false;

    function asyncActivity(toParams) {
      var deferred = $q.defer();
      deferred.notify('About to greet ' + name + '.');
      var activity = activityService.getCurrentActivity();
      $scope.currentActivity = {
        name: toParams.name
      };
      if (toParams.name === undefined || activity.name == toParams.name) {
        deferred.resolve(activity)
      } else {
        activity = activityService.getByName(toParams.name)
        if (activity.name != undefined) {
          activity.name = toParams.name;
          activityService.setCurrentActivity(activity);
          deferred.resolve(activity)
        } else {
          api.admin.hackathon.get({
            header: {
              hackathon_name: toParams.name
            }
          }).then(function(data) {
            if (data.error) {
              deferred.reject(data.error)
            } else {
              activityService.add(data);
              activityService.setCurrentActivity(data);
              deferred.resolve(data)
            }
          });
        }
      }

      return deferred.promise;
    }

    $rootScope.$on("$stateChangeStart", function(event, toState, toParams, fromState, fromParams) {
      $scope.loading = true;
      if (toState.name == 'create' || toState.name == 'main') {
        return;
      } else {
        asyncActivity(toParams).then(function(activity) {
            console.log(activity)
            if (activity.status == -1) {
              $state.go('create', {
                name: toParams.name
              });
            } else if (activity.config.cloud_provide == 0) {
              switch (toState.name) {
                case 'manage.ve':
                case 'manage.monitor':
                case 'manage.cloud':
                case 'manage.servers':
                  $state.go('404');
                  return
              }
            } else {
              $rootScope.$broadcast('chargeActitity')
            }
          },
          function(error) {
            $state.go('404');
            event.preventDefault();
          }
        )
      }
    });

    $rootScope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams) {
      $scope.loading = false;
    });

  })
  .controller('manageController', function($scope, $state, activityService, session, NAV) {
    var activity = $scope.activity = activityService.getCurrentActivity();
    $scope.$on('chargeActitity', function(event) {
      activity = $scope.activity = activityService.getCurrentActivity();
      event.preventDefault();
    })
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

    $scope.isShowNav = function(type) {
      if (type == 1) {
        return true;
      }
      if (activity.config) {
        return activity.config.cloud_provider != 0
      } else {
        return false;
      }
    }

    $scope.navLink = function(item) {
      return $state.href(item.state, {
        name: activity.name
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
    activity.config.max_enrollment = parseInt(activity.config.max_enrollment, 10) || 0;

    $scope.modules = activity;
    $scope.tags = [];
    $scope.activityFormDisabled = false;
    angular.forEach($scope.modules.tags, function(value, key) {
      $scope.tags.push({
        text: value
      });
    });

    $scope.provider = {
      windows: $filter('isProvider')(activity.config.login_provider, 1),
      github: $filter('isProvider')(activity.config.login_provider, 2),
      qq: $filter('isProvider')(activity.config.login_provider, 4),
      weibo: $filter('isProvider')(activity.config.login_provider, 8),
      alauda: $filter('isProvider')(activity.config.login_provider, 32),
      gitcafe: $filter('isProvider')(activity.config.login_provider, 16),
    };

    $scope.open = {
      event_start_time: false,
      event_end_time: false,
      registration_start_time: false,
      registration_end_time: false,
      judge_start_time: false,
      judge_end_time: false
    };


    $scope.showTip = function(level, content, showTime) {
      $scope.$emit('showTip', {
        level: level,
        content: content,
        showTime: showTime || 3000
      });
    };

    //update basic information
    $scope.updateBasicInformation = function() {
      $scope.modules.tags = [];
      angular.forEach($scope.tags, function(value, key) {
        $scope.modules.tags.push(value.text);
      });

      $scope.activityFormDisabled = true;
      api.admin.hackathon.put({
        header: {
          hackathon_name: $scope.modules.name
        },
        body: $scope.modules
      }, function(data) {
        if (data.error) {
          $scope.showTip(level = 'tip-danger', content = data.error.friendly_message);
        } else {
          $scope.showTip(level = 'tip-success', content = '更新成功');
        }
        $scope.activityFormDisabled = false;
      });
    };

    $scope.delBanner = function(index) {
      $scope.modules.banners.splice(index, 1);
      api.admin.hackathon.put({
        header: {
          hackathon_name: $scope.modules.name
        },
        body: {
          banners: $scope.modules.banners
        }
      }, function(data) {
        if (data.error) {
          $scope.showTip(level = 'tip-danger', content = data.error.friendly_message);
        } else {
          $scope.showTip(level = 'tip-success', content = '删除成功');
        }
      });
    };

    $scope.showAddBannerDialog = function() {
      $scope.modules.banners.push('http://image5.tuku.cn/pic/wallpaper/fengjing/shanshuilantian/014.jpg');
      api.admin.hackathon.put({
        header: {
          hackathon_name: $scope.modules.name
        },
        body: {
          banners: $scope.modules.banners
        }
      }, function(data) {
        if (data.error) {
          $scope.showTip(level = 'tip-danger', content = data.error.friendly_message);
        } else {
          $scope.showTip(level = 'tip-success', content = '添加成功');
        }
      });
    };

    $scope.updateDescription = function() {
      api.admin.hackathon.put({
        header: {
          hackathon_name: $scope.modules.name
        },
        body: {
          description: $scope.modules.description
        }
      }, function(data) {
        if (data.error) {
          $scope.showTip(level = 'tip-danger', content = data.error.friendly_message);
        } else {
          $scope.showTip(level = 'tip-success', content = '保存成功');
        }
      });
    };

    $scope.providerChange = function(checked, value) {
      if (checked) {
        $scope.modules.config.login_provider = ((+$scope.modules.config.login_provider) || 0) | value;
      } else {
        $scope.modules.config.login_provider = ((+$scope.modules.config.login_provider) || 0) ^ value;
      }

      api.admin.hackathon.config.put({
        header: {
          hackathon_name: $scope.modules.name
        },
        body: {
          login_provider: $scope.modules.config.login_provider
        }
      }).then(function(data) {
        if (data.error) {
          $scope.showTip(level = 'tip-danger', content = data.error.friendly_message);
        } else {
          $scope.showTip(level = 'tip-success', content = '登录方式修改成功');
        }
      });
    };

  })
  .controller('usersController', function($rootScope, $scope, activityService, api, util, dialog) {
    $scope.$emit('pageName', 'SETTINGS.USERS');

    var activity = activityService.getCurrentActivity();

    $scope.data = {
      registerUsers: [], // we cannot use activity.registration here, its single
      regStatus: {},
      checkAll: false,
      checks: {},
      perPage: 20,
      curPage: 1,
      nPage: 0,

      freedomTeam: false,
      autoApprove: false
    };

    var showTip = function(level, content, showTime) {
      $scope.$emit('showTip', {
        level: level,
        content: content,
        showTime: showTime || 3000
      });
    };

    var refresh = function() {
      api.admin.registration.list.get({
        header: {
          hackathon_name: activity.name
        }
      }, function(data) {
        if (data.error) {
          showTip('tip-danger', data.error.friendly_message);
        } else {
          $scope.data.regStatus = {};
          $scope.data.checkAll = false;
          $scope.data.checks = {};

          var i;
          for (i = 0; i < data.length; i++) {
            $scope.data.regStatus[data[i].id] = '' + data[i].status;
            $scope.data.checks[data[i].id] = false;
          }

          $scope.data.registerUsers = data;
          $scope.data.curPage = 1;
          $scope.data.nPage = parseInt(Math.round(data.length / $scope.data.perPage));

          $scope.data.autoApprove = activity.config.auto_approve;
          $scope.data.freedomTeam = activity.config.freedom_team;
        }
      });
    };

    $scope.$on('chargeActitity', function() {
      activity = activityService.getCurrentActivity();
      refresh();
    });

    var _updateBatch = function(updates, status, index) {
      if (index >= updates.length) {
        return;
      }

      var reg = updates[index];

      api.admin.registration.put({
        header: {
          hackathon_name: activity.name
        },
        body: {
          id: reg.id,
          status: status,
        },
      }, function(data) {
        if (data.error) {
          showTip('tip-danger', 'some of the registration updates failed: ' + data.error.friendly_message);
        } else {
          reg.status = parseInt(status);
          $scope.data.regStatus[reg.id] = '' + reg.status;
        }

        _updateBatch(updates, status, index + 1);
      });
    };

    $scope.updateStatus = function(reg) {
      return api.admin.registration.put({
        header: {
          hackathon_name: activity.name
        },
        body: {
          id: reg.id,
          status: parseInt($scope.data.regStatus[reg.id]),
        }
      }, function(data) {
        if (data.error) {
          showTip('tip-danger', data.error.friendly_message);
          $scope.data.regStatus[reg.id] = '' + reg.status;
        } else {
          reg.status = parseInt($scope.data.regStatus[reg.id]);
        }
      });
    };

    $scope.updateStatusBatch = function(status) {
      var i, id, reg;

      var toUpdate = [];
      for (i = 0; i < $scope.data.registerUsers.length; i++) {
        reg = $scope.data.registerUsers[i];
        id = reg.id;

        if ($scope.data.checks[id])
          toUpdate.push(reg);
      }

      _updateBatch(toUpdate, status, 0);
    };

    $scope.toggleCheckAll = function() {
      var i;
      for (i = 0; i < $scope.data.registerUsers.length; i++) {
        $scope.data.checks[$scope.data.registerUsers[i].id] = $scope.data.checkAll;
      }
    };

    $scope.checkCheckAll = function() {
      var i = 0,
        allChecked = true;
      for (i = 0; i < $scope.data.registerUsers.length; i++) {
        if (!$scope.data.checks[$scope.data.registerUsers[i].id]) {
          allChecked = false;
          break;
        }
      }

      $scope.data.checkAll = allChecked;
    };

    $scope.updateConfig = function() {
      api.admin.hackathon.put({
        header: {
          hackathon_name: activity.name
        },
        body: {
          config: {
            auto_approve: $scope.data.autoApprove,
            freedom_team: $scope.data.freedomTeam
          }
        }
      }, function(data) {
        if (data.error) {
          showTip('tip-danger', data.error.friendly_message);
          $scope.data.autoApprove = activity.config.auto_approve;
          $scope.data.freedomTeam = activity.config.freedom_team;
        } else {
          activity.config.auto_approve = $scope.data.autoApprove;
          activity.config.freedom_team = $scope.data.freedomTeam;
        }
      });
    };
  })
  .controller('adminController', function($rootScope, $scope, $uibModal, activityService, api, dialog) {
    $scope.$emit('pageName', 'SETTINGS.ADMINISTRATORS');

    var activity = activityService.getCurrentActivity();
    $scope.data = {
      admins: [],
      adminsType: [],
      adminsRemark: [],
      selectedAdmins: [],
      searchKeyword: "", // search users to create admins
      searchResult: [],
      selectedUserId: "", // user selected to create an admin
      selectedUserCSS: {color: 'red'}, // todo remove this line when CSS done
      selectedUserRole: 1,
      selectedUserRemark: ""
    }
    // 0-no condition, 1-admin, 2-judge
    $scope.filterAdminCondition = 0;

    function showTip(level, content, showTime) {
      $scope.$emit('showTip', {
        level: level,
        content: content,
        showTime: showTime || 3000
      });
    };

    $scope.filterAdmin = function(item) {
      if($scope.filterAdminCondition == 0)
        return true;
      return item.role == $scope.filterAdminCondition;
    }

    $scope.updateAdmin = function(admin) {
      api.admin.hackathon.administrator.put({
        header: {hackathon_name: activity.name},
        body: {
          id: admin.id,
          role: parseInt($scope.data.adminsType[admin.id]),
          remark: $scope.data.adminsRemark[admin.id]
        }
      }, function(data) {
        if(data.error)
          showTip('tip-danger', data.error.friendly_message);
        else{
          // update $scope.data.admin
          admin.role = parseInt($scope.data.adminsType[admin.id]);
          admin.remark = $scope.data.adminsRemark[admin.id];
          showTip('tip-success', '修改管理员成功');
        }
      });
    }

    $scope.isAdminSelected = function(admin) {
      return $scope.data.selectedAdmins.indexOf(admin.id) > -1;
    }

    $scope.isAllAdminsSelected = function() {
      return $scope.data.selectedAdmins.length == $scope.data.admins.length;
    }

    $scope.selectAdmin = function(admin) {
      var index = $scope.data.selectedAdmins.indexOf(admin.id)
      if(index > -1){
        $scope.data.selectedAdmins.splice(index, 1)
      } else {
        $scope.data.selectedAdmins.push(admin.id)
      }
    }

    $scope.toggleAllAdmins = function() {
      if($scope.data.admins.length == $scope.data.selectedAdmins.length){
        $scope.data.selectedAdmins = [];
      } else {
        $scope.data.selectedAdmins = [];
        for(var index in $scope.data.admins)
          $scope.data.selectedAdmins.push($scope.data.admins[index].id);
      }
    }

    $scope.deleteAdmins = function() {
      deleteAdminList($scope.data.selectedAdmins, 0);

      // delete admins one by one
      function deleteAdminList(list, index) {
        if(index == list.length){
          pageLoad();
          return;
        }
        api.admin.hackathon.administrator.delete({
          header: {hackathon_name: activity.name},
          query: {id: list[index]}
        }, function(data) {
          if(data.error)
            showTip('tip-danger', data.error.friendly_message);
          else
            showTip('tip-success', '成功删除管理员!');
          deleteAdminList(list, index + 1);
        });
      }
    }

    $scope.showSearchBar = function() {
      var data = $scope.data;

      $uibModal.open({
        templateUrl: 'addAdminModel.html',
        controller: function($scope, $uibModalInstance) {
          $scope.data = data;
          $scope.cancel = function() {
            $uibModalInstance.dismiss('cancel');
          };

          $scope.searchAdmin = searchAdmin;
          $scope.selectSearchedUser = selectSearchedUser;
          $scope.createAdmin = createAdmin;
        },
      });
    }

    function searchAdmin() {
      api.admin.user.list.get({
        header: {hackathon_name: activity.name},
        query: {keyword: $scope.data.searchKeyword}
      }, function(data) {
        if(data.error)
          showTip('tip-danger', data.error.friendly_message);
        else
          $scope.data.searchResult = data.items;
      });
    }

    function selectSearchedUser(user) {
      $scope.data.selectedUserId = user.id;
    }

    function createAdmin() {
      if($scope.data.selectedUserId == "") {
        showTip('tip-danger', "请选择需要设置成管理员的用户！");
      } else {
        api.admin.hackathon.administrator.post({
          header: {hackathon_name: activity.name},
          body: {
            id: $scope.data.selectedUserId,
            role: $scope.data.selectedUserRole,
            remark: $scope.data.selectedUserRemark
          }
        }, function(data) {
          if(data.error)
            showTip('tip-danger', data.error.friendly_message);
          else{
            showTip('tip-success', '创建管理员成功');
            pageLoad();
          }
        });
      }
    }

    function pageLoad() {
      api.admin.hackathon.administrator.list.get({
        header: {hackathon_name: activity.name}
      }, function(data){
        if(data.error)
          showTip('tip-danger', data.error.friendly_message);
        else{
          $scope.data.admins = data;
          $scope.data.adminsType = [];
          $scope.data.adminsRemark = [];
          $scope.data.selectedAdmins = [];
          $scope.data.searchKeyword = "";
          $scope.data.searchResult = [];
          $scope.data.selectedUserId = "";
          $scope.data.selectedUserRole = 1;
          $scope.data.selectedUserRemark = "";
          for(var index in data) {
            $scope.data.adminsType[data[index].id] = data[index].role.toString();
            $scope.data.adminsRemark[data[index].id] = data[index].remark;
          }
        }
      })
    }

    // init the page and load admins-list
    pageLoad();
  })
  .controller('organizersController', function($rootScope, $scope, $cookies, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.ORGANIZERS');

    // very quick and rough implementation, please feel free to update
    $scope.data = $scope.activity = activityService.getCurrentActivity();
    $scope.$on('chargeActitity', function(event) {
      $scope.data = $scope.activity = activityService.getCurrentActivity();
      event.preventDefault();
    })

    $scope.orgFormSubmit = function(){
      api.admin.hackathon.organizer.post({
        body: $scope.org,
        header: {
          hackathon_name: $scope.activity.name,
          token: $cookies.get('token')
        }
      }).then(function(data){
        if(data.error){
          $scope.$emit('showTip', {
            level: 'tip-danger',
            content: data.error.friendly_message
          });
        }else{
          $scope.showTip(level = 'tip-success', content = '修改成功');
        }
      })
    }

    $scope.delete_organizer = function(organizer_id){
      api.admin.hackathon.organizer.delete({
          query: {
            id: organizer_id
          },
          header: {
            hackathon_name: $scope.activity.name,
            token: $cookies.get('token')
          }
        }).then(function(data){
          if(data.error){
            $scope.$emit('showTip', {
              level: 'tip-danger',
              content: data.error.friendly_message
            });
          }else{
            $scope.data.organizers = $scope.data.organizers.filter(function(organizer){
              return organizer.id != organizer_id
            })
            $scope.data.partners = $scope.data.partners.filter(function(partner){
              return partner.id != organizer_id
            })
          }
        })
    }
  })
  .controller('awardsController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'SETTINGS.AWARDS');

  })
  .controller('prizesController', function($rootScope, $scope, $uibModal, activityService, api, dialog) {
    $scope.$emit('pageName', 'SETTINGS.PRIZES');

    var activity = activityService.getCurrentActivity();
    $scope.data = {
      awards: activity.awards,
    };

    var formData = {};

    var showTip = function(level, msg) {
      $scope.$emit('showTip', {
        level: level,
        content: msg
      });
    };

    var refreshAward = function() {
      return api.admin.hackathon.award.list.get({
        header: {hackathon_name: activity.name}
      }, function(data) {
        if(data.error) {
          showTip('tip-danger', data.error.friendly_message);
          return ;
        }

        activity.awards = data;
        $scope.data.awards = data;
      });
    };

    $scope.$on('chargeActitity', function() {
      activity = activityService.getCurrentActivity();
      refreshAward();
    });

    var deleteAward = function(id) {
      return api.admin.hackathon.award.delete({
        query: {id: id},
        header: {
          hackathon_name: activity.name
        }
      });
    };

    var createAward = function() {
      var award = formData;
      var fn;

      if(award.id)
        fn = api.admin.hackathon.award.put;
      else
        fn = api.admin.hackathon.award.post;

      return fn({
        body: award,
        header: {
          hackathon_name: activity.name
        }
      }, function(data) {
        if(data.error)
          showTip('tip-danger', data.error.friendly_message);
        else {
          showTip('tip-success', '创建/修改成功');
          refreshAward();
        }
      });
    };

    var openAddAwardWizard = function() {
      $uibModal.open({
        templateUrl: 'awardModel.html',
        controller: function($scope, $uibModalInstance) {
          $scope.data = formData;

          $scope.cancel = function() {
            $uibModalInstance.dismiss('cancel');
          };

          $scope.addAward = function() {
            createAward()
            $uibModalInstance.close();
          };
        },  // end controller
      })

      // handel create
      .result.then(createAward);
    };

    $scope.delete = function(id) {
      dialog.confirm({
        title: '提示',
        body: '确认删除此奖项?'
      }).then(function() {
        return deleteAward(id);
      }).then(function(data) {
        if(data.error)
          showTip('tip-danger', data.error.friendly_message);
        else {
          showTip('tip-success', '删除成功');
          return refreshAward();
        }
      });
    };

    $scope.edit = function(idx) {
      formData = activity.awards[idx];
      openAddAwardWizard();
    };

    $scope.add = function() {
      formData = {
        name: '',
        award_url: '',
        level: 5,
        quota: 1,
        description: '',
      };
      openAddAwardWizard();
    };
  })
  .controller('veController', function($rootScope, $scope, $stateParams, $filter, activityService, $cookies, FileUploader, activity, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.VIRTUAL_ENVIRONMENT');

    api.template.list.get({}).then(function(data) {
      $scope.image_templates = data;
    });

    api.admin.hackathon.template.list.get({
      header: {
        hackathon_name: activity.name
      }
    }, function(data) {
      $scope.templates = data;
    })

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
            hackathon_name: activity.name
          }
        });
      } else {
        result = api.admin.hackathon.template.delete({
          query: {
            template_id: id
          },
          header: {
            hackathon_name: activity.name
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
        updataActivityStatus(0);
      } else {
        $scope.$emit('showTip', {
          level: 'tip-danger',
          content: '请绑定模板'
        });
      }
    }

  })
  .controller('monitorController', function($rootScope, $scope, $stateParams, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.ENVIRONMENTAL_MONITOR');

    var activity = activityService.getCurrentActivity();
    $scope.data = {
      "experiments": []
    }
    // filterCondition -1:all, 2:running, 3:stopped, 5:fail
    $scope.filterExperimentCondition = -1;
    $scope.searchKeyword = "";

    $scope.filterExperiments = function(item) {
      if($scope.filterExperimentCondition == -1)
        return true;
      return item.status== $scope.filterExperimentCondition;
    }

    function showTip(level, content, showTime) {
      $scope.$emit('showTip', {
        level: level,
        content: content,
        showTime: showTime || 3000
      });
    };

    $scope.updateExperiment = function(experiment) {
      showTip('tip-danger', "暂时不支持更新操作");
    }

    $scope.deleteExperiment = function(experiment) {
      showTip('tip-danger', "暂时不支持删除操作");
    }

    $scope.searchExperiment = function() {
      if($scope.searchKeyword == "") {
        pageLoad();
        return
      }

      api.admin.experiment.list.get({
        header: {
          hackathon_name: activity.name
        },
        query: {
          user_name: $scope.searchKeyword
        }
      }).then(function(data) {
        if (data.error) {
          showTip('tip-danger', data.error.friendly_message);
        } else {
          if(data.length == 0)
            showTip('tip-danger', "未找到满足要求的结果");
          $scope.data.experiments = data;
          $scope.filterExperimentCondition = -1;
        }
      })
    }

    function pageLoad() {
      api.admin.experiment.list.get({
        header: {
          hackathon_name: activity.name
        }
      }).then(function(data) {
        if (data.error) {
          showTip('tip-danger', data.error.friendly_message);
        } else {
          $scope.data.experiments = data;
          $scope.filterExperimentCondition = -1;
          $scope.searchKeyword = ""
        }
      })
    }

    pageLoad();
  })
  .controller('cloudController', function($rootScope, $scope, activityService, api) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.CLOUD_RESOURCES');

  })
  .controller('azurecertController', function($rootScope, $scope, $stateParams, activityService, api, dialog) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.AZURECERT');
    var isDeleteCerDisabled = false;
    $scope.azureFormDisabled = false;
    $scope.azure = {
      management_host: 'management.core.chinacloudapi.cn',
    };


    function getAzureCer() {
      api.admin.azure.get({
        header: {
          hackathon_name: $stateParams.name
        }
      }).then(function(data) {
        $scope.azurecerts = data;
        console.log(data);
      });
    }

    $scope.checksubid = function(ecert) {
      api.admin.azure.checksubid.post({
        body: {
          subscription_id: ecert.subscription_id
        },
        header: {
          hackathon_name: $stateParams.name
        }
      }).then(function(data) {
        if (!data.message) {
          $scope.$emit('showTip', {
            level: 'tip-warning',
            content: '证书授权失败，请检验SUBSCRIPTION ID是否正确。'
          });
        } else {
          $scope.$emit('showTip', {
            level: 'tip-success',
            content: '检验成功。'
          });
          ecert.verified = true;
        }
      })
    };


    $scope.azureFormSubmit = function() {
      $scope.azureFormDisabled = true;
      api.admin.azure.post({
        body: $scope.azure,
        header: {
          hackathon_name: $stateParams.name
        }
      }).then(function(azure_key) {
        if (azure_key.error) {
          $scope.$emit('showTip', {
            level: 'tip-danger',
            content: azure_key.error.friendly_message
          });
        } else {
          $scope.$emit('showTip', {
            level: 'tip-success',
            content: '创建SUBSCRIPTION ID成功'
          });
          $scope.azure.subscription_id = '';
          $scope.azure.management_host = 'management.core.chinacloudapi.cn';
        }
        $scope.azureFormDisabled = false;
      });
    };


    $scope.deleteCert = function(id) {
      if (!isDeleteCerDisabled) {
        isDeleteCerDisabled = !isDeleteCerDisabled;
        dialog.confirm({
          title: '提示',
          body: '确定删除此Azure证书？',
          icon: 'fa-exclamation',
          size: 'sm',
          status: 'warning'
        }).then(function() {
          api.admin.azure.delete({
            header: {
              hackathon_name: $stateParams.name
            },
            query: {
              certificate_id: id
            }
          }).then(function(data) {
            if (data.error) {
              $scope.$emit('showTip', {
                level: 'tip-danger',
                content: data.error.friendly_message
              });
            } else {
              $scope.$emit('showTip', {
                level: 'tip-success',
                content: '删除成功'
              });
              getAzureCer();
            }
            isDeleteCerDisabled = !isDeleteCerDisabled;
          });
        })
      }
    }


    getAzureCer();
  })
  .controller('serversController', function($rootScope, $scope, $uibModal, $cookies, activityService, api, dialog) {
    $scope.$emit('pageName', 'ADVANCED_SETTINGS.SERVERS');
    var activity = activityService.getCurrentActivity();
    var refresh = function(){
      api.admin.hostserver.list.get({
          header: {
            hackathon_name: activity.name,
            token: $cookies.get('token')
          }
        }).then(function(data){
          if(data.error){
            $scope.$emit('showTip', { level: 'tip-danger', content: data.error.friendly_message});
          }else{
            $scope.data = data
          }
        })
    }

    var afterAdd = function(new_server){
      $scope.$emit('showTip', { level: 'tip-success', content: "添加成功"});
      $scope.data.push(new_server)
    }

    var afterUpdate = function(new_server){
      $scope.$emit('showTip', { level: 'tip-success', content: "更新成功"});
      $scope.data = $scope.data.map(function(server){
        if(server.id==new_server.id){
          return new_server
        }else{
          return server
        }
      })
    }

    $scope.$on('chargeActitity', function() {
      activity = activityService.getCurrentActivity();
      refresh();
    });

    var openModel = function(data){
      $uibModal.open({
        templateUrl: 'serverModel.html',
        controller: function($scope, $uibModalInstance, $cookies, api) {
          $scope.data = data;

          $scope.cancel = function() {
            $uibModalInstance.dismiss('cancel');
          };

          $scope.add_server = function() {
            var fn, af;
            if(data.id){
              fn = api.admin.hostserver.put
              af = afterUpdate
            }else{
              fn = api.admin.hostserver.post
              af = afterAdd
            }
            fn({
              body: $scope.data,
              header: {
                hackathon_name: activity.name,
                token: $cookies.get('token')
              }
            }).then(function(data){
              if(data.error){
                $scope.$emit('showTip', { level: 'tip-danger', content: data.error.friendly_message});
              }else{
                af(data)
              }
              $uibModalInstance.close();
            })
          };
        },  // end controller
      })
    }

    $scope.add = function(){
      openModel({})
    }

    $scope.edit = function(server){
      openModel(server)
    }

    $scope.delete = function(server_id){
      api.admin.hostserver.delete({
        query: {
          id: server_id
        },
        header: {
          hackathon_name: activity.name,
          token: $cookies.get('token')
        }
      }).then(function(data){
        if(data.error){
          $scope.$emit('showTip', { level: 'tip-danger', content: data.error.friendly_message});
        }else{
          $scope.$emit('showTip', { level: 'tip-success', content: "删除成功"});
          $scope.data = $scope.data.filter(function(server){
            return server.id != server_id
          })
        }
      })
    }

    $scope.getState = function(state){
      desc= {0:"创建中", 1:"创建中", 2:"可用", 3:"不可用"}
      return desc[state] || ""
    }
  })
  .controller('createController', function($scope, $timeout, $filter, $cookies, $state, $stateParams, FileUploader, dialog, api) {
    var request;
    $scope.wizard = 1;
    $scope.isShowAdvancedSettings = true;

    $scope.activityFormDisabled = false;

    $scope.activity = {
      location: '',
      tags: [],
      config: {
        cloud_provider: 0,
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
      if (newValue) {
        request = $timeout(function() {
          api.admin.hackathon.checkname.get({
            query: {
              name: newValue
            }
          }, function(data) {
            $scope.activityForm.name.$setValidity('rometname', !data);
          });
        }, 400);
      }
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
      updataActivityStatus(0).then(function(data) {
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
        api.admin.hackathon.config.put({
          header: {
            hackathon_name: $scope.activity.name
          },
          body: {
            cloud_provider: parseInt($scope.clondservices)
          }
        }).then(function(data) {
          if (data.error) {
            $scope.$emit('showTip', {
              level: 'tip-danger',
              content: data.error.friendly_message
            });
          }
        });
      })
    };

    /*------------------------------------------------------*/
    $scope.azureFormDisabled = false;
    $scope.azuse_download_cer = false;
    $scope.azure = {
      management_host: 'management.core.chinacloudapi.cn',
    };

    $scope.azureNext = function() {
      $scope.wizard = 3;
    }

    $scope.azureFormSubmit = function() {
      $scope.azureFormDisabled = true;
      api.admin.azure.post({
        body: $scope.azure,
        header: {
          hackathon_name: $scope.activity.name
        }
      }).then(function(azure_key) {
        if (azure_key.error) {
          $scope.$emit('showTip', {
            level: 'tip-danger',
            content: azure_key.error.friendly_message
          });
        } else {
          api.admin.azure.checksubid.post({
            body: {
              subscription_id: $scope.azure.subscription_id
            },
            header: {
              hackathon_name: $scope.activity.name
            }
          }).then(function(data) {
            if (!data.message) {
              $scope.$emit('showTip', {
                level: 'tip-warning',
                content: '证书授权失败，请检验SUBSCRIPTION ID是否正确。'
              });
            }
          })

          var cert_url = azure_key.cert_url;
          window.location.href = cert_url;
          $scope.azuse_download_cer = true;
          $scope.azurecer = cert_url;
        }
        $scope.azureFormDisabled = false;
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
        updataActivityStatus(0);
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
      api.admin.hackathon.online.post({
        header: {
          hackathon_name: $scope.activity.name
        }
      }).then(function(data) {
        $scope.onlineDisabled = false;
        if (data.error) {
          var message = ''
          if (data.error.code == 412101) {
            message = '当前黑客松没有还未创建成功。'
          } else if (data.error.code == 412102) {
            message = '证书授权失败，请检验SUBSCRIPTION ID是否正确。'
          } else {
            message = data.error.friendly_message
          }
          $scope.$emit('showTip', {
            level: 'tip-danger',
            content: message
          });
        } else {
          $scope.$emit('showTip', {
            level: 'tip-success',
            content: '上线成功'
          });
        }
      })
    }
  });
