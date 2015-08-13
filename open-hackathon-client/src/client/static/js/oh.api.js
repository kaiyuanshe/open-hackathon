/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

;
(function($, w) {
    function FactoryAPI() {
        function API(obj, name) {
            var key;
            var getCmd = {};
            if (obj instanceof Array) {
                for (key in obj) {
                    getCmd[obj[key]] = API(obj[key], name)
                }
                return getCmd;
            } else if (obj instanceof Object) {
                for (key in obj) {
                    if (obj.hasOwnProperty(key)) {
                        if (key == '') {
                            getCmd = API(obj[key], name)
                        } else {
                            getCmd[key] = API(obj[key], name + '/' + key);
                        }
                    }
                }
                return getCmd;
            } else {
                return getCmd[obj] = function(options, callback) {
                    var _params = {
                        query: {},
                        body: {},
                        header: {},
                    };
                    callback = callback || new Function();
                    if ($.isFunction(options)) {
                        callback = options;
                        options = {};
                    }
                    options = $.extend(_params, options);
                    var url = name;
                    var data = $.isEmptyObject(options.body) ? '':JSON.stringify(options.body);
                    if (!$.isEmptyObject(options.query)) {
                        url += '?'+$.param(options.query);
                    }
                    options.header.token = $.cookie('token');
                    return $.ajax({
                        method: obj,
                        url: url,
                        contentType: obj == 'get' ? 'application/x-www-form-urlencoded' : 'application/json',
                        headers: options.header,
                        data: data,
                        success: function(data) {
                            if(data.error){
                                if(data.error.code == 401){
                                    console.log(data)
                                    location.href = '/logout';
                                }else {
                                    callback(data)
                                }
                            }else{
                                callback(data)
                            }
                        },
                        error: function(req, status, error) {
                            var data = {
                                error : {
                                    error: error ,
                                    message: req.responseText,
                                    status: req.status
                                }
                            };
                            callback(data);
                        }
                    });
                }
            }
        }
        return API(CONFIG.apiconfig.api, CONFIG.apiconfig.proxy + '/api');
   }
   w.oh = w.oh || {};
   w.oh.api = FactoryAPI();
})(jQuery, window);