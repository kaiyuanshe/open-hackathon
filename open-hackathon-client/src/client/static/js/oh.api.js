/*
 * This file is covered by the LICENSING file in the root of this project.
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
                    options.header.Authorization = "token " + $.cookie('token');
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