'use strict';

/**
 * @ngdoc overview
 * @name learnangularApp
 * @description
 * # learnangularApp
 *
 * Main module of the application.
 */
angular
    .module('learnangularApp', [
        'ngAnimate',
        'ngAria',
        'ngCookies',
        'ngMessages',
        'ngResource',
        'ui.router',
        'ngSanitize',
        'ngTouch'
    ])
    .config(function($stateProvider, $urlRouterProvider) {
        $urlRouterProvider.otherwise('/');
        $stateProvider
            .state('index', {
                url: '',
                views: {
                    '': {
                        templateUrl: 'views/master.html'
                    },
                    'header@index': {
                        templateUrl: 'views/header.html'
                    },
                    'main@index': {
                        templateUrl: 'views/main.html',
                        controller: 'MainCtrl'
                    },
                    'footer@index': {
                        templateUrl: 'views/footer.html'
                    }
                }
            })
            .state('index.about', {
                url: '/about',
                views: {
                    'main@index': {
                        templateUrl: 'views/about.html',
                        controller: 'AboutCtrl'
                    }
                }
            });
    });
