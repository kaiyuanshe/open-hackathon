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
    var CURRENT_HACKATHON_COOKIE_NAME = 'current_hackathon';
    w.oh = w.oh || {};
    w.oh.comm = {
        DateFormat: function(milliseconds, formatstr) {
            formatstr = formatstr || 'yyyy-MM-dd';
            return new Date(milliseconds).format(formatstr);
        },
        getCurrentHackathon: function() {
            var route = '/manage/:hackathon_name';
            var routeMatcher = new RegExp(route.replace(/:[^\s/]+/g, '([\\w-]+)'));
            return window.location.pathname.match(routeMatcher)[1] || '';
        },
        createLoading:function(elemt){
            $(elemt).children().hide();
            $(elemt).append($('<div class="text-center" data-type="pageloading"><img src="/static/pic/spinner-lg.gif"></div>'))
        },
        removeLoading:function(){
            var pageloading = $('[data-type="pageloading"]')
            pageloading.siblings().show();
            pageloading.detach();
        }
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

    window.addEventListener("storage", function(e) {
        var key = e.key;
        var newValue = e.newValue;
        var oldValue = e.oldValue;
        var url = e.url;
        var storageArea = e.storageArea;
        console.log(e);
    });

    function addTabsEvent(){
        var tabs = $('[data-type="tabs"]').on('click','a',function(e){
            e.preventDefault();
            var a = $(this);
            var toTab = a.attr('href');
            var li =  a.parent();
            li.addClass('active').siblings().removeClass('active');
            $(toTab).addClass('active').siblings().removeClass('active');;
        })
    }

    $(function() {
        if(location.pathname.search('logout','i') != -1){
            location.href = '/login';
            return;
        }
        w.oh.comm.createLoading('[loading]');
        addTabsEvent();
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
