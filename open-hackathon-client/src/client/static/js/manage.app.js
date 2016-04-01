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

angular.module('manageView', [
    'ngCookies',
    'ngSanitize',
    'ngMessages',
    'ngMessageFormat',
    'ngAnimate',
    'pascalprecht.translate',
    'ui.router',
    'ui.bootstrap',
    'ui.bootstrap.datetimepicker',
    'ngTagsInput',
    'angularFileUpload',
    'oh.manage.router',
    'oh.pages',
    'oh.providers',
    'oh.filters',
    'oh.controllers',
    'oh.directives',
    'oh.templates',
    'oh.api'
  ])
  .config(function($translateProvider) {
    $translateProvider.useStaticFilesLoader({
        prefix: '/static/languages/',
        suffix: '.json'
      }).preferredLanguage('zh-de')
      .useSanitizeValueStrategy()
      .useLocalStorage();

  }).run(function($rootScope, $state, authService, api, activityService, uiDatetimePickerConfig) {
    uiDatetimePickerConfig.buttonBar = {
      show: true,
      now: {
        show: true,
        text: '现在'
      },
      today: {
        show: true,
        text: '今天'
      },
      clear: {
        show: true,
        text: '取消'
      },
      date: {
        show: true,
        text: '日期'
      },
      time: {
        show: true,
        text: '时间'
      },
      close: {
        show: true,
        text: '关闭'
      }
    };
    authService.getUser();
    $rootScope.$on('showTip', function(event, obj) {
      $rootScope.tip = obj;
      event.preventDefault();
      event.stopPropagation();
    });

  });
