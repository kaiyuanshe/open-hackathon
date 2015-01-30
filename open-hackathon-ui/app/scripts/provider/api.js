'use strict';

angular
    .module('open-hackathon', ['ngCookies'])
    .factory('api', ['$resource ', function($resource) {
        var api = {};

        var methods = {
            find: 'get',
            remove: 'delete',
            save: 'post'
        };

        var apiModules = ['course', 'registerlist', 'announcement', 'login'];
        var resource = $resource('/api/:m', {
            m: '@m'
        });

        var getCmd = function(module) {
            var objCmd = {};

            var createCmd = function(key, value) {
                return function(query, callback) {
                    resource[value]({
                        m: module
                    }, query, function(res) {
                        callback(res);
                    });
                };
            };

            for (var key in methods) {
                objCmd[key] = createCmd(key, methods[key]);
            }

            objCmd.cmd = function(name) {
                return function(query, callback) {
                    resource[key]({
                        m: name
                    }, query, function(res) {
                        callback(res);
                    });
                };
            };

            return objCmd;
        };

        api.module = function(name) {
            return getCmd(name);
        };

        var createModule = function(module) {
            return getCmd(module);
        };

        for (var i in apiModules) {
            api[apiModules[i]] = createModule(apiModules[i]);
        }

        return api;
    }]);
