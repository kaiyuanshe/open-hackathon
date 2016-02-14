/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   manage.app.js                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: anonymous <anonymous@student.42.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2016/01/27 20:11:57 by anonymous         #+#    #+#             */
/*   Updated: 2016/02/05 16:46:03 by anonymous        ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

angular.module('manageView', [
    'ngCookies',
    'ngSanitize',
    'bootstrap',
    'oh.manage.router',
    'ui.router',
    'oh.pages',
    'oh.api',
    'oh.controllers',
    'oh.directives',
    'ui.bootstrap.dropdown',
    'pascalprecht.translate',
    'bw.paging'
  ])
  .config(['$locationProvider', '$translateProvider', '$stateProvider', '$urlRouterProvider', 'MANAGE_PAGES', function($locationProvider,
    $translateProvider,
    $stateProvider,
    $urlRouterProvider,
    MANAGE_PAGES) {
    $translateProvider.useStaticFilesLoader({
        prefix: '/static/languages/',
        suffix: '.json'
      }).preferredLanguage('zh-de')
      .useSanitizeValueStrategy()
      .useLocalStorage();

    $urlRouterProvider.otherwise('/main');

    $stateProvider.state('main', {
      url: '/main',
      templateUrl: '/static/partials/manage/main.html'
    });
    $stateProvider.state('create', {
      url: '/create',
      templateUrl: '/static/partials/manage/create.html'
    });
    $stateProvider.state('404', {
      url: '/404',
      templateUrl: '/static/partials/manage/404.html'
    });

    $locationProvider.html5Mode(true).hashPrefix('!');

  }]).run(function($rootScope, $state, api, activityService) {
    $rootScope.$on('showTip', function(event, obj) {
      $rootScope.tip = obj;
      event.preventDefault();
      event.stopPropagation();
    });
  });



angular.module('oh.providers ', [])
  .provider();



