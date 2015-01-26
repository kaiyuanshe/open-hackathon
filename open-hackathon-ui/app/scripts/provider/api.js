'use strict';

angular
    .module('open-hackathon', ['ngCookies'])
    .factory('api', ['$resource ,$cookieStore', function($resource, $cookieStore) {
        var api = {}
        var methods = {
            find: 'get',
            remove: 'delete',
            save: 'post'
        }
        var _api_modules = ['course', 'registerlist', 'announcement', 'login']
        var resource = $resource('/api/:m', {
            m: '@m'
        })
        var getCmd = function(module) {
            var objCmd = {}
            for (var key in methods) {
                objCmd[key] = (function(key, value) {
                    return function(query, callback) {
                        resource[key]({
                            m: module
                        }, query, function(res) {
                            callback(res);
                        })
                    }
                })(key, methods[key])
                objCmd.cmd = function(name) {
                    return function(query, callback) {
                        resource[key]({
                            m: name
                        }, query, function(res) {
                            callback(res)
                        })
                    }
                }
            }
            return objCmd;
        }
        api.module = function(name) {
            return getCmd(name);
        }
        for (var i in _api_modules) {
            api[_api_modules[i]] = (function(module) {
                return getCmd(module);
            })(_api_modules[i])
        }
        return api;
    }])