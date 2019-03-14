/*
 * This file is covered by the LICENSING file in the root of this project.
 */

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
