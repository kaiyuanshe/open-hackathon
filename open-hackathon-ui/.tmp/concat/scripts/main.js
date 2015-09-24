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
 * @namespace oh.app
 * @author <ifendoe@gmail.com>
 * @version 0.0.1
 * Created by Boli Guan on 15-3-10.
 */

/**
 * @ngdoc overview
 * @name hackathonApp
 * @description
 * # hackathonApp
 *
 * Main module of the application.
 */
angular
  .module('oh.app', [
    'ngAnimate',
    'ngAria',
    'ngCookies',
    'ngMessages',
    'ngResource',
    'ui.router',
    'ngSanitize',
    'ngTouch',
    'ui.bootstrap',
    'oh.services',
    'oh.controllers',
    'oh.directives'
  ])
  .config(["$stateProvider", "$urlRouterProvider", function ($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');
    $stateProvider
      .state('index', {
        url: '/',
        views: {
          '': {
            templateUrl: 'views/master.html'
          },
          'header@index': {
            templateUrl: 'views/header.html'
          },
          'main@index': {
            templateUrl: 'views/main.html',
            controller: 'main.controller'
          },
          'footer@index': {
            templateUrl: 'views/footer.html'
          }
        }
      })
      .state('index.settings', {
        url: 'settings',
        views: {
          'header@index': {
            templateUrl: 'views/header.html',
            controller: ["$scope", function ($scope) {
              $scope.isShow = true;
            }]
          },
          'main@index': {
            templateUrl: 'views/settings.html',
            controller: 'settings.controller'
          }
        }
      })
      .state('index.hackathon', {
        url: 'hackathon',
        views: {
          'header@index': {
            templateUrl: 'views/hackathon-header.html',
            controller: 'oh.header.controller'
          },
          'main@index': {
            templateUrl: 'views/hackathon.html',
            controller: ''
          }
        }
      })
      .state('notregister', {
        url: '/notregister',
        views: {
          '': {
            templateUrl: 'views/notregister.html',
            controller: 'notregister.controller'
          }
        }
      })
      .state('index.challenges', {
        url: 'challenges',
        views: {
          'header@index': {
            templateUrl: 'views/header.html',
            controller: ["$scope", "User", function ($scope, User) {
              if (User) {
                $scope.isShow = true;
              }
            }]
          },
          'main@index': {
            templateUrl: 'views/challenges.html'
          }
        }
      })
    ;
  }]);

String.prototype.format = function (args) {
  var result = this;
  if (arguments.length > 0) {
    if (arguments.length == 1 && typeof(args) == 'object') {
      for (var key in args) {
        if (args[key] != undefined) {
          var reg = new RegExp('({' + key + '})', 'g');
          result = result.replace(reg, args[key]);
        }
      }
    } else {
      for (var i = 0; i < arguments.length; i++) {
        if (arguments[i] != undefined) {
          var reg = new RegExp('({[' + i + ']})', 'g');
          result = result.replace(reg, arguments[i]);
        }
      }
    }
  }
  return result;
};

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
  .run(["$http", "$rootScope", function ($http, $rootScope) {
    $http.get('/config')
      .success(function (data) {
        $rootScope.config = data;
      })
      .error(function (data) {
        console.log(data);
      })
  }])
  .factory('API', ["$http", "$cookieStore", "$rootScope", function ($http, $cookieStore, $rootScope) {
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
  }]);



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
 * Created by Boli Guan on 15-3-10.
 */

/**
 * @ngdoc function
 * @name oh.controllers:main.controller
 * @description
 * # main.controller
 * Controller of the main.controller
 */
var s = angular.module('oh.controllers', []);
s.controller('main.controller', ["$scope", function ($scope) {

  function openWindow(url, width) {
//    width = width || 600;
//    var l, t;
//    l = (screen.width - width ) / 2;
//    t = (screen.height - 400) / 2;
//    window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=' + width + ', height=500, top=' + t + ', left=' + l);
    window.location.href = url
  }

  $scope.githublogin = function () {
    var url = 'https://github.com/login/oauth/authorize?' +
      $.param($scope.config.sociallogin.github);
    openWindow(url);
  };
  $scope.qqlogin = function () {
    var url = 'https://graph.qq.com/oauth2.0/authorize?' +
      $.param($scope.config.sociallogin.qq);
    openWindow(url);
  };
  $scope.gitcafelogin = function () {
    var url = 'https://gcs.dgz.sh/oauth/authorize?' +
      $.param($scope.config.sociallogin.gitcafe);
    openWindow(url, 980);
  };
  $scope.weibologin = function () {
    var url = 'https://api.weibo.com/oauth2/authorize?' +
      $.param($scope.config.sociallogin.weibo);
    openWindow(url);
  }
}]);



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
 * Created by Boli Guan on 15-3-12.
 */

/**
 * @ngdoc function
 * @name oh.controllers:notregister.controller
 * @description
 * @author <ifendoe@gmail.com>
 * # notregister.controller
 * Controller of the notregister.controller
 */
angular.module('oh.controllers')
  .controller('notregister.controller', ["$scope", "$timeout", "$interval", function ($scope, $timeout, $interval) {

  }]);

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
 * Created by Boli Guan on 15-3-12.
 */

/**
 * @ngdoc function
 * @name oh.controllers:oh.header.controller
 * @description
 * @author <ifendoe@gmail.com>
 * # oh.header.controller
 * Controller of the oh.header.controller
 */
angular.module('oh.controllers')
  .controller('oh.header.controller', ["$scope", "$rootScope", "$cookieStore", "$state", function ($scope, $rootScope, $cookieStore, $state) {
    if (!$cookieStore.get('User')) {
      $state.go('index');
    }
    $rootScope.hackathon = true;
    $scope.status = {
      isopen: false
    }

    $scope.toggled = function (open) {
      console.log('dropdown is now', open);
    }
    $scope.toggledDropdown = function ($event) {
      $event.preventDefult();
      $event.stopPropagation();
      $event.status.isopen = !$scope.status.isopen;
    }
    $scope.$on('$destroy', function (event) {
        $rootScope.hackathon = false;
      }
    );
  }]);


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
 * Created by Boli Guan on 15-3-12.
 */

/**
 * @ngdoc function
 * @name oh.controllers:settings.controller
 * @description
 * # settings.controller
 * Controller of the settings.controller
 */
angular.module('oh.controllers')
  .controller('settings.controller', ["$scope", "$cookieStore", "$state", "API", function ($scope, $cookieStore, $state, API) {
    $scope.type = 'ut';
    var User = $cookieStore.get('User') || '';
    if (!User) {
      $state.go('index');
    } else if (!User.register_state) {
      $state.go('notregister');
    } else if (User.experiments.length > 0) {
      $state.go('index.hackathon');
    }
    $scope.submit = function () {
      API.user.experiment.post(JSON.stringify({cid: $scope.type, hackathon: $scope.config.name}), function (data) {
        $state.go('index.hackathon');
      });
    }
  }]);

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
  .directive('hackathonNav', ["$interval", "$cookieStore", "$templateCache", "API", function ($interval, $cookieStore,$templateCache, API) {
    return {
      restrict: 'E',//'AEMC'
      templateUrl: 'views/tpls/hackathon-nav.html', //<div ng-transclude></div>
      replace: true,
      link: function (scope, elemten, attr) {
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
            var name = a.attr('id')
            var ifrem = work_center.find('#' + name);
            work_center.find('iframe').addClass('invisible');
            if (ifrem.length > 0) {
              ifrem.removeClass('invisible');
            } else {
              ifrem = $('<iframe>').attr({
                src: url + "&token=" + ($cookieStore.get('User') || '').token,
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

        var temp = $templateCache.get('hackathon-vm.html');
        API.user.experiment.post(JSON.stringify({cid: 'windows10', hackathon: scope.config.name}), function (data) {
          var stop;
          var list = [];
          var loopstart = function () {
            API.user.experiment.get({id: data.expr_id}, function (data) {
              if (data.status == 2) {
                var dockers = []
                for (var i in data.public_urls) {
                  dockers.push({
                    purl: data.public_urls[i].url,
                    name: data.remote_servers[i].name,
                    surl: data.remote_servers[i].url
                  })
                  list.push(temp.format(dockers[i]));
                }
                $('.hackathon-nav').append(list.join(''))
                bindTemp(data);
                $('.hackathon-nav a.vm-box:eq(0)').trigger('click');
                $interval.cancel(stop);
              } else if (data.status == 1) {
                stop = $interval(loopstart, 60000, true);
              } else {
                showErrorMsg()
                $interval.cancel(stop);
              }
            });
          }
          loopstart();
          scope.$on('$destroy',
            function (event) {
              $interval.cancel(stop);
            }
          );
        });
      }
    }
  }])
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
  .directive('countdown', ["$interval", function ($interval) {
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
  }])
  .directive('headdropdownMenu', ["$cookieStore", "API", function ($cookieStore, API) {
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
        },{
          name: '我的黑客松挑战',
          link: ''
        }, {
          name: '使用帮助',
          link: 'https://github.com/msopentechcn/open-hackathon/wiki/OpenXML-SDK-在线编程黑客松平台《使用帮助》'
        }]
        scope.logout = function () {
          API.user.login.del({});
          $cookieStore.remove('User');
          location.replace('/#/');
        }
        scope.user = $cookieStore.get('User');
      }
    }
  }])
  .directive('ohOline', ["$rootScope", "$interval", "API", function ($rootScope, $interval, API) {
    return {
      scope: {},
      restrict: 'E',
      templateUrl: 'views/tpls/online-total.html',
      link: function (scope, element) {
        API.hackathon.list.get({name: $rootScope.config.name}, function (data) {
          var getStat = function () {
            API.hackathon.stat.get({hid: $.parseJSON(data).id}, function (data) {
              element.find('[oh-online]').text(data.online);
              element.find('[oh-total]').text(data.total);
            });
          }
          getStat();
          var stop = $interval(function () {
            getStat(0)
          }, 10000);
          scope.$on('$destroy', function (event) {
              $interval.cancel(stop);
            }
          );
        });
      }
    }
  }])
  .directive('endCountdown', ["$rootScope", "$interval", "API", function ($rootScope, $interval, API) {
    return {
      scope: {},
      restrict: 'EA',
      templateUrl: 'views/tpls/end-countdown.html',
      link: function (scope, element, attr) {
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

        var timerTmpe = '{day}天{hour}小时{minute}分钟{second}秒';
        API.hackathon.list.get({name: $rootScope.config.name}, function (data) {
          data = $.parseJSON(data);
          var countDown = {
            time_server: new Date().getTime(),
            time_end: new Date(data.end_time.replace(/-/g, '/')).getTime()
          }
          var showCountDown = function () {
            var timing = show_time.apply(countDown);
            if (!timing) {
              element.find('#timer').text('本次活动已结束，非常感谢您的参与。')
              $interval.cancel(stop);
            } else {
              element.find('#end_timer').text(timerTmpe.format(timing))
            }
          }
          showCountDown();
          var stop = $interval(showCountDown, 1000);
          scope.$on('$destroy', function (event) {
              $interval.cancel(stop);
            }
          );
        })
      }
    }
  }])
  .directive('ohTooltip', ["$timeout", function ($timeout) {
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
  }])
