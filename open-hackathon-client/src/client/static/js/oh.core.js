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
(function ($, w) {
    w.oh = w.oh || {};
    w.oh.comm = {
        DateFormat: function (milliseconds, formatstr) {
            formatstr = formatstr || 'yyyy-MM-dd';
            return new Date(milliseconds).format(formatstr);
        },
        guid: function () {
            var S4 = function () {
                return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
            };
            return (S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() + S4() + S4());
        },
        getCurrentHackathon: function () {
            return $('meta[name="hackathon_name"]').attr('content');
        },
        createLoading: function (elemt) {
            $(elemt).children().hide();
            $(elemt).append($('<div class="text-center" data-type="pageloading"><img src="/static/pic/spinner-lg.gif"></div>'));
        },
        removeLoading: function () {
            var pageloading = $('[data-type="pageloading"]');
            pageloading.siblings().show();
            pageloading.detach();
        },
        stripTags: function (html, limit) {
            limit = limit || 60;
            var text = html.replace(/(<([^>]+)>)/ig, '');
            return limit ? text.substr(0, limit) : text;
        },
        alert: function (title, text, fun) {
            fun = fun || new Function();
            var alert = $('body').Dialog({
                title: title,
                body: text,
                footer: $('<button class="btn btn-primary">确定</button>').click(function (e) {
                    fun();
                    alert.hide();
                }),
                modal: 'alert'
            });
        }
    };

    $.getUrlParam = function (name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]);
        return null;
    };

    function executeFunctionByName(functionName, context) {
        var args = [].slice.call(arguments).splice(2);
        var namespaces = functionName.split(".");
        var func = namespaces.pop();
        for (var i = 0; i < namespaces.length; i++) {
            context = context[namespaces[i]];
        }
        return context[func].apply(this, args);
    }

    window.addEventListener("storage", function (e) {
        var key = e.key;
        var newValue = e.newValue;
        var oldValue = e.oldValue;
        var url = e.url;
        var storageArea = e.storageArea;
        console.log(e);
    });

    function addTabsEvent() {
        var tabs = $('[data-type="tabs"]').on('click', 'a', function (e) {
            e.preventDefault();
            var a = $(this);
            var toTab = a.attr('href');
            var li = a.parent();
            li.addClass('active').siblings().removeClass('active');
            $(toTab).addClass('active').siblings().removeClass('active');
        })
    }

    $(function () {
        $('body').on('click', '[role="oh-like"]', function (e) {
            var like = $(this);
            var hackathon_name = like.data('name');
            oh.api.user.hackathon.like.post({header: {hackathon_name: hackathon_name}}, function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    like.addClass('active');
                }
            });
        });


        $('[data-toggle="tooltip"]').tooltip();
        if (location.pathname.search('logout', 'i') != -1) {
            location.href = '/login';
            return;
        }
        w.oh.comm.createLoading('[loading]');
        addTabsEvent();
        var menu = $('#sidebar-left .main-menu');
        menu.find('a').each(function () {
            if ($($(this))[0].href == String(window.location)) {
                $(this).parent().addClass('active');
                $(this).parents('ul').add(this).each(function () {
                    $(this).show();
                    $(this).prev('a').find('.chevron').removeClass('closed').addClass('opened')
                })
            }
        });

        menu.on('click', '.dropmenu', function (e) {
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
            };
            $.extend(_params, obj.data('options') || {});
            executeFunctionByName(obj.data('api'), w, _params, function (data) {
                obj.empty().append($(obj.data('target')).tmpl(data));
                if (obj.editable) {
                    obj.find('.edit').editable();
                }
                if (obj.data('change')) {
                    obj.trigger('oh.change');
                }
            });
        }

        $('[data-change]').bind('oh.change', function (e) {
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
        }).change(function (e) {
            $(this).trigger('oh.change');
        });

        //var confirm_modal = $('#confirm_modal').on('show.bs.modal', function (e) {
        //    confirm_modal
        //        .data({
        //            item: $(e.relatedTarget).parents('tr').data('tmplItem').data,
        //            target: $(e.relatedTarget).parents('tbody')
        //        });
        //}).on('click', '[data-type="delete"]', function (e) {
        //    executeFunctionByName(confirm_modal.data('api'), w, {
        //        query: {
        //            id: confirm_modal.data('item').id
        //        },
        //        header: {
        //            hackathon_id: confirm_modal.data('item').hackathon_id
        //        }
        //    }, function (data) {
        //        bindData(confirm_modal.data('target'));
        //        confirm_modal.modal('hide');
        //    });
        //});

        $('[data-toggle="bindtemp"]').each(function (i, o) {
            bindData($(o));
        });
    })
})(jQuery, window);

String.prototype.format = function (args) {
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length == 1 && typeof(args) == 'object') {
            for (var key in args) {
                if (args[key] != undefined) {
                    var reg = new RegExp('({' + key + '})', 'g');
                    result = result.replace(reg, args[key]);
                }
            }
        } else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] != undefined) {
                    var reg = new RegExp('({[' + i + ']})', 'g');
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
    }
    return result;
};

(function ($) {
    var Dialog = function (select, options) {
        this.params = {
            title: '',
            body: '',
            footer: '',
            modal: ''
        }
        $.extend(true, this.params, options || {});
        this.layout = $('<div class="modal fade {modal}"  role="dialog" >\
                <div class="modal-dialog modal-sm">\
                    <div class="modal-content">\
                        <div class="modal-header">\
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
                            <h4 class="modal-title">{title}</h4>\
                        </div>\
                        <div class="modal-body">\
                            {body}\
                        </div>\
                        <div class="modal-footer">\
                        </div>\
                     </div>\
                </div>\
            </div>'.format(this.params));
        this.layout.find('.modal-footer').append(this.params.footer);
        this.init();
    }
    Dialog.prototype = {
        init: function () {
            this.layout.on('hidden.bs.modal', function (e) {
                e.target.remove();
            })
            this.layout.modal('show');
        },
        hide: function () {
            this.layout.modal('hide');
        }
    }
    $.fn.Dialog = function (options) {
        if ($(this).length > 1) {
            var _instances = [];
            $(this).each(function (i) {
                _instances[i] = new Dialog(this, options);
            });
            return _instances;
        } else {
            return new Dialog(this, options);
        }
    }
    if (!jQuery.fn.dialog) {
        $.fn.dialog = $.fn.Dialog;
    }
})(jQuery);