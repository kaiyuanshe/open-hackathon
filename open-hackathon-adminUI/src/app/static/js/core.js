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
                        query: null,
                        body: null,
                        header: {},
                    };
                    callback = callback || new Function();
                    if ($.isFunction(options)) {
                        callback = options;
                        options = {};
                    }
                    options = $.extend(_params, options);
                    var url = name;
                    var data = options.body == null ? '' : JSON.stringify(options.body);
                    if (options.query) {
                        url += '?' + ($.isPlainObject(options.query) ? $.param(options.query) : options.query);
                    }
                    options.header.token = $.cookie('token');
                    $.ajax({
                        method: obj,
                        url: url,
                        contentType: obj == 'get' ? 'application/x-www-form-urlencoded' : 'application/json',
                        headers: options.header,
                        data: data,
                        success: function(data) {
                            callback(data)
                        },
                        error: function(req, status, error) {
                            var data = {
                                error: error,
                                message: req.responseText,
                                status: req.status
                            };
                            callback(data);
                        }
                    });
                }
            }
        }
        return API(apiconfig.api, apiconfig.proxy + '/api');
    }
    w.oh = w.oh || {};
    w.oh.api = FactoryAPI();
    w.oh.comm = {
        DateFormat: function(milliseconds, formatstr) {
            formatstr = formatstr || 'yyyy-MM-dd';
            return new Date(milliseconds).format(formatstr);
        },
        getHackathon: function() {
            return JSON.parse(localStorage.hackathon);
        }
    };

    Date.prototype.format = function(mask) {
        var d = this;
        var zeroize = function(value, length) {
            if (!length) length = 2;
            value = String(value);
            for (var i = 0, zeros = ''; i < (length - value.length); i++) {
                zeros += '0';
            }
            return zeros + value;
        };
        var test = /"[^"]*"|'[^']*'|\b(?:d{1,4}|m{1,4}|yy(?:yy)?|([hHMstT])\1?|[lLZ])\b/g;
        return mask.replace(test, function(obj) {
            switch (obj) {
                case 'd':
                    return d.getDate();
                case 'dd':
                    return zeroize(d.getDate());
                case 'ddd':
                    return ['Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat'][d.getDay()];
                case 'dddd':
                    return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][d.getDay()];
                case 'M':
                    return d.getMonth() + 1;
                case 'MM':
                    return zeroize(d.getMonth() + 1);
                case 'MMM':
                    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getMonth()];
                case 'MMMM':
                    return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][d.getMonth()];
                case 'yy':
                    return String(d.getFullYear()).substr(2);
                case 'yyyy':
                    return d.getFullYear();
                case 'h':
                    return d.getHours() % 12 || 12;
                case 'hh':
                    return zeroize(d.getHours() % 12 || 12);
                case 'H':
                    return d.getHours();
                case 'HH':
                    return zeroize(d.getHours());
                case 'm':
                    return d.getMinutes();
                case 'mm':
                    return zeroize(d.getMinutes());
                case 's':
                    return d.getSeconds();
                case 'ss':
                    return zeroize(d.getSeconds());
                case 'l':
                    return zeroize(d.getMilliseconds(), 3);
                case 'L':
                    var m = d.getMilliseconds();
                    if (m > 99) m = Math.round(m / 10);
                    return zeroize(m);
                case 'tt':
                    return d.getHours() < 12 ? 'am' : 'pm';
                case 'TT':
                    return d.getHours() < 12 ? 'AM' : 'PM';
                case 'Z':
                    return d.toUTCString().match(/[A-Z]+$/);
                default:
                    return obj.substr(1, $0.length - 2);
            }
        });
    };
    $.getUrlParam = function(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]);
        return null;
    }

    function executeFunctionByName(functionName, context) {
        var args = [].slice.call(arguments).splice(2);
        var namespaces = functionName.split(".");
        var func = namespaces.pop();
        for (var i = 0; i < namespaces.length; i++) {
            context = context[namespaces[i]];
        }
        return context[func].apply(this, args);
    }

    function SessionStorageBindHackathon(data) {
        var hackathons = [];
        $.each(data, function(i, o) {
            hackathons.push({
                name: o.name,
                id: o.id
            })
        })
        sessionStorage.hackathons = JSON.stringify(hackathons)
    };

    window.addEventListener("storage", function(e) {
        var key = e.key;
        var newValue = e.newValue;
        var oldValue = e.oldValue;
        var url = e.url;
        var storageArea = e.storageArea;
        console.log(e);
    });
    $(function() {
        $.template('switc_hackathons_temp', '<li {{if $item.isAction(id ,$item.hid)}} class="active" {{/if}}>{{if $item.isAction(id,$item.hid) }}<i class="fa fa-check"></i>{{/if}}<a href="#" data-type="hackathon">${name}</a></li>');
        //$.template('switc_hackathons_temp', '<li><a href="#" data-type="hackathon">${name}</a></li>');
        // $.template('switc_hackathons_temp2','<li><a href="javascript:;">
        //                              <span class="icon blue"><i class="fa fa-check"></i></span>
        //                              <span class="message">${name}</span>
        //                          </a>
        //                      </li>')
        var hackathon_modal = $('#switc_hackathon_modal').on('show.bs.modal', function(e) {
            var ul = hackathon_modal.find('.modal-body ul').empty();
            oh.api.admin.hackathons.get(function(data) {
                ul.append($.tmpl('switc_hackathons_temp', data, {
                    isAction: function(id, hid) {
                        return id == hid
                    },
                    hid: JSON.parse(localStorage.hackathon || '{"id":"0"}').id
                }));
            });
        }).on('hide.bs.modal', function(e) {
            if (!localStorage.hackathon) {
                return false;
            }
        }).on('click', 'a[data-type="hackathon"]', function(e) {
            var li = $(this).parents('li');
            if (!li.hasClass('active')) {
                var data = li.data('tmplItem').data;
                localStorage.hackathon = JSON.stringify({
                    name: data.name,
                    id: data.id
                });
                hackathon_modal.data({
                    li: li
                });
                hackathon_modal.trigger('Reloadhackathon');
            }
        }).bind('Reloadhackathon', function(e) {
            var li = hackathon_modal.data('li');
            hackathon_modal.find('ul>li').removeClass('active');
            hackathon_modal.find('ul>li>i').detach();
            li.addClass('active').prepend('<i class="fa fa-check"></i>');
            location.reload()
        });

        if (!localStorage.hackathon) {
            hackathon_modal.modal('show')
        }

        /*if(!sessionStorage.hackathons){
            oh.api.admin.hackathons.get(function(data){
                 SessionStorageBindHackathon(data);
            });
        } */

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

        function bindData(obj) {
            var _params = {
                header: {},
                body: {},
                query: {}
            }
            $.extend(_params, obj.data('options') || {});
            executeFunctionByName(obj.data('api'), w, _params, function(data) {
                obj.empty().append($(obj.data('target')).tmpl(data));
                if (obj.editable) {
                    obj.find('.edit').editable();
                }
                if (obj.data('change')) {
                    obj.trigger('oh.change');
                }
            });
        }

        $('[data-change]').bind('oh.change', function(e) {
            var obj = $(this);
            var tar = $(obj.data('change-target'));
            var data = {
                query: {},
                body: {}
            };
            data.query[tar.data('query')] = obj.val();
            tar.data({
                options: data
            });
            bindData(tar);
        }).change(function(e) {
            $(this).trigger('oh.change');
        });

        var confirm_modal = $('#confirm_modal').on('show.bs.modal', function(e) {
            confirm_modal
                .data({
                    item: $(e.relatedTarget).parents('tr').data('tmplItem').data,
                    target: $(e.relatedTarget).parents('tbody')
                });
        }).on('click', '[data-type="delete"]', function(e) {
            executeFunctionByName(confirm_modal.data('api'), w, {
                query: {
                    id: confirm_modal.data('item').id
                },
                header: {
                    hackathon_id: confirm_modal.data('item').hackathon_id
                }
            }, function(data) {
                bindData(confirm_modal.data('target'));
                confirm_modal.modal('hide');
            });
        });

        $('[data-toggle="bindtemp"]').each(function(i, o) {
            bindData($(o));
        });
    })
})(jQuery, window);
