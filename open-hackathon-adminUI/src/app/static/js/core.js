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
;
(function($, w) {

    function FactoryAPI() {
        var _params = {
            query: null,
            body: null,
            header: {},
        };

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
                    callback = callback || new Function();
                    if ($.isFunction(options)) {
                        callback = options;
                        options = {};
                    }
                    $.extend(_params, options || {});
                    var url = name;
                    if (_params.query) {
                        url += '?' + ($.isPlainObject(_params.query) ? $.param(_params.query) : _params.query);
                    }
                    _params.header.token = $.cookie('token');
                    $.ajax({
                        method: obj,
                        url: url,
                        contentType: obj == 'get' ? 'application/x-www-form-urlencoded' : 'application/json',
                        headers: _params.header,
                        data: _params.body,
                        success: function(data) {
                            callback(data)
                        },
                        error: function(data) {
                            callback(data)
                        }
                    });
                }
            }
        }
        return API(apiconfig.api, apiconfig.proxy + '/api');
    }
    w.oh = w.oh || {};
    w.oh.api = FactoryAPI();

    $(function() {
        var menu = $('#sidebar-left .main-menu');
        menu.find('a').each(function() {
            if ($($(this))[0].href == String(window.location)) {
                $(this).parent().addClass('active');
                $(this).parents('ul').add(this).each(function() {
                    $(this).show();
                    $(this).prev('a').find('.chevron').removeClass('closed').addClass('opened')
                })
            }
        });

        menu.on('click', '.dropmenu', function(e) {
            e.preventDefault();
            var chevron = $(this).find('.chevron');
            if (chevron.hasClass('opened')) {
                chevron.removeClass('opened').addClass('closed');
                chevron.parents('li').find('ul').hide();
            } else {
                chevron.removeClass('closed').addClass('opened');
                chevron.parents('li').find('ul').show();
            }
        });
    })
})(jQuery, window);
