var express = require('express')
var config = require('../config')
var request = require('request')

module.exports = (function factory() {
    var service = {}
    var methods = {
        post: 'post',
        del: 'del',
        put: 'put'
    }
    var api_modulse = config.api
    var getCmd = function(module, action) {
        var objCmd = {}
        for (var key in methods) {
            objCmd[key] = (function(key, value) {
                return function(query, callback) {
                    var options = {
                        method: key,
                        'content-type': 'application/json',
                        url: action == null ? [config.proxy, 'api', module].join('/') : [config.proxy, 'api', module, action].join('/'),
                        json: query
                    }
                    request(options, function(err, res, data) {
                        callback(res,data)
                    })
                }
            })(key, methods[key])
        }
        return objCmd
    }
    for (var key in api_modulse) {
        service[key] = (function(module) {
            return getCmd(module, null)
        })(key);
        for (var i in api_modulse[key]) {
            service[key][api_modulse[key][i]] = (function(module) {
                return getCmd(module)
            })(key, api_modulse[key][i])
        }
    }
    return service
})()