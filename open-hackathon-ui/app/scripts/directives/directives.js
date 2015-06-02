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
 * @namespace oh.directives
 * @author <ifendoe@gmail.com>
 * @version 0.0.1
 * Created by Boli Guan on 15-3-12.
 */

angular.module('oh.directives', [])
  /* .run(function ($templateCache) {
   $templateCache.put('hackathon.html', '');
   $templateCache.get('hackathon.html');
   })*/
  .directive('hackathonNav', function ($interval, $cookieStore, $templateCache, API) {

    var heartbeatInterval = null;
    var stop = null;

    function showErrorMsg(code, msg) {
      $('#load').hide();
      var errorbox = $('#error');
      if (code) {
        errorbox.find('.code').text(code);
      }
      if (msg) {
        errorbox.find('.message').text(msg);
      }
      errorbox.show();
    }

    function bindTemp(data) {
      var servers = data.remote_servers || data.guacamole_servers;
      var work_center = $('.center').on('mouseover', 'iframe', function (e) {
        $(this).focus();
      });
      var hnav = $('.hackathon-nav').on('click', 'a.vm-box', function (e) {
        hnav.find('.vm-box').removeClass('active')
        var a = $(this).addClass('active');
        var url = a.data('url');
        var token = a.data('token');
        var name = a.attr('id')
        var ifrem = work_center.find('#' + name);
        work_center.find('iframe').addClass('invisible');
        if (ifrem.length > 0) {
          ifrem.removeClass('invisible');
        } else {
          ifrem = $('<iframe>').attr({

            src: url ,

            id: name,
            width: '100%',
            height: '100%',
            frameborder: 'no',
            marginwidth: '0',
            scrolling: 'no'
          }).appendTo(work_center)
        }
      });
    }

    function heartbeat(id) {
      API.user.experiment.put({
        body: {id: id}
      }, function (data) {
        if (data.error) {
          $interval.cancel(heartbeatInterval);
        }
      });
    }

    return {
      restrict: 'E',//'AEMC'
      templateUrl: 'views/tpls/hackathon-nav.html', //<div ng-transclude></div>
      replace: true,
      link: function (scope, elemten, attr) {
        scope.$watch('workData', function (newValue, oldValue) {
          if (newValue) {
            var temp = $templateCache.get('hackathon-vm.html');
            var list = [];
            var loopstart = function () {
              API.user.experiment.get({query: {id: newValue.experiment.id}}, function (data) {
                if (data.status == 2) {
                  var dockers = []
                  for (var i in data.public_urls) {
                    dockers.push({
                      purl: data.public_urls[i].url,
                      name: data.remote_servers[i].name,
                      surl: data.remote_servers[i].url+ "&oh=" + $cookieStore.get('token')
                    })
                    list.push(temp.format(dockers[i]));
                  }
                  $('.hackathon-nav').append(list.join(''))
                  bindTemp(data);
                  $('.hackathon-nav a.vm-box:eq(0)').trigger('click');
                  $interval.cancel(stop);
                  heartbeatInterval = $interval(function () {
                    heartbeat(data.expr_id)
                  }, 300000, true);
                } else if (data.status == 1) {
                  stop = $interval(loopstart, 60000, true);
                } else {
                  showErrorMsg()
                  $interval.cancel(stop);
                }
              });
            }
            loopstart();
          }
        });
        scope.$on('$destroy', function (event) {
          $interval.cancel(stop);
          $interval.cancel(heartbeatInterval);
        });
      }
    }
  })
  .directive('workFull', function () {
    return {
      restrict: 'A',
      transclude: true,
      template: '<ng-transclude></ng-transclude>',
      link: function (scope, element, attr) {
        element.bind('click', function () {
          $('iframe[class!="invisible"]').addClass('work-full');
          $('.smallscreen').show();
        });
      }
    }
  })
  .directive('workSmall', function () {
    return {
      restrict: 'EA',
      template: '<div class="smallscreen"><a class="glyphicon glyphicon-resize-small" href="javascript:;" ></a></div>',
      link: function (scope, element, attr) {
        var small = element.find('.smallscreen').appendTo('body');
        small.hide();
        small.bind('click', function () {
          $('iframe[class!="invisible"]').removeClass('work-full');
          small.hide();
        });
      }
    }
  })
  .directive('countdown', function ($interval) {
    return {
      restrict: 'E',
      link: function (scope, element, attr) {
        scope.second = parseInt(attr.second);
        var countdown = $interval(function () {
          scope.second--;
        }, 1000, 4, true);
        countdown.then(function () {
          window.location.href = attr.link;
        });
        scope.$on('$destroy', function (event) {
            $interval.cancel(countdown);
          }
        );
      }
    }
  })
  .directive('headdropdownMenu', function ($cookieStore, API) {
    return {
      scope: {},
      restrict: 'E',
      templateUrl: 'views/tpls/dropdown-menu.html',
      link: function (scope) {
        scope.items = [{
          name: '管理我的黑客松',
          link: ''
        }, {
          name: '黑客松活动指南',
          link: ''
        }, {
          name: '我的黑客松挑战',
          link: ''
        }, {
          name: '使用帮助',
          link: 'https://github.com/msopentechcn/open-hackathon-tutorial/wiki/%E5%9C%A8%E7%BA%BF%E7%BC%96%E7%A8%8B%E9%BB%91%E5%AE%A2%E6%9D%BE%E5%B9%B3%E5%8F%B0%E3%80%8A%E4%BD%BF%E7%94%A8%E5%B8%AE%E5%8A%A9%E3%80%8B'
        }]
        scope.logout = function () {
          API.user.login.del();
          $cookieStore.remove('User');
          location.replace('/#/');
        }
        scope.user = $cookieStore.get('User');
      }
    }
  })
  .directive('ohOline', function ($rootScope, $interval, API) {
    return {
      scope: {},
      restrict: 'E',
      templateUrl: 'views/tpls/online-total.html',
      link: function (scope, element) {
        API.hackathon.list.get({
          query: {name: config.name}
        }, function (data) {
          var getStat = function () {
            API.hackathon.stat.get({
              header: {hackathon_name: config.name}
            }, function (data) {
              element.find('[oh-online]').text(data.online);
              element.find('[oh-total]').text(data.total);
            });
          }
          getStat();
          var stop = $interval(function () {
            getStat(0)
          }, 60000);
          scope.$on('$destroy', function (event) {
              $interval.cancel(stop);
            }
          );
        });
      }
    }
  })
  .directive('endCountdown', function ($interval, API) {
    var timerTmpe = '{day}天{hour}小时{minute}分钟{second}秒';
    var stop = null;

    function show_time() {
      var timing = {day: 0, hour: 0, minute: 0, second: 0, distance: 0};
      this.time_server += 1000
      timing.distance = this.time_end - this.time_server;
      if (timing.distance > 0) {
        timing.day = Math.floor(timing.distance / 86400000)
        timing.distance -= timing.day * 86400000;
        timing.hour = Math.floor(timing.distance / 3600000)
        timing.distance -= timing.hour * 3600000;
        timing.minute = Math.floor(timing.distance / 60000)
        timing.distance -= timing.minute * 60000;
        timing.second = Math.floor(timing.distance / 1000)
        if (timing.day == 0) {
          timing.day = null
        }
        if (timing.hour == 0 && timing.day == null) {
          timing.hour = null
        }
        if (timing.minute == 0 && timing.hour == null) {
          timing.minute = null
        }
        if (timing.second == 0 && timing.minute == null) {
          timing.second = null
        }
        return timing;
      } else {
        return null;
      }
    }
    function showCountDown(elemten, countDown) {
      var timing = show_time.apply(countDown);
      if (!timing) {
        elemten.find('#timer').text('本次活动已结束，非常感谢您的参与。')
        $interval.cancel(stop);
      } else {
        elemten.find('#end_timer').text(timerTmpe.format(timing))
      }
    }
    return {
      scope: {},
      restrict: 'A',
      templateUrl: 'views/tpls/end-countdown.html',
      link: function (scope, elemten, attr) {
        API.hackathon.get({header: {hackathon_name: config.name}}, function (data) {
          if (data.error) {
            $location.path('error');
          } else {
            var countDown = {
              time_server: new Date().getTime(),
              time_end: data.event_end_time
            }
            showCountDown(elemten, countDown);
            stop = $interval(function () {
              showCountDown(elemten, countDown);
            }, 1000);
          }
        });
        scope.$on('$destroy', function (event) {
          $interval.cancel(stop);
        });
      }
    }
  })
  .
  directive('ohTooltip', function ($timeout) {
    return {
      scope: {},
      restrict: 'EA',
      templateUrl: 'views/tpls/oh-tooltip.html',
      link: function (scope, element, attr) {
        $timeout(function () {
          element.fadeOut(2000);
        }, 1500)
      }
    }
  })
  .directive('ohEmailAvailable', function ($q, $timeout, API) {
    return {
      require: 'ngModel',
      link: function (scope, element, attrs, ngModel) {
        ngModel.$asyncValidators.emailAvailable = function (modelValue, viewValue) {
          if (ngModel.$isEmpty(modelValue)) {
            return $q.when();
          }
          var def = $q.defer();
          $timeout(function () {
            API.user.registration.checkemail.get({query: {hid: attrs.hid, email: modelValue}}, function (data) {
              if (data) {
                def.resolve();
              } else {
                def.reject();
              }
            })
          }, 500);
          return def.promise;
        };
      }
    }
  });
