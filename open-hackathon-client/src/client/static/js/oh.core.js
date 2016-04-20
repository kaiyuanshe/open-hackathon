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
            var text = html.replace(/(<([^>]+)>)/ig, '').replace(/&nbsp;/ig, '');
            return limit ? text.substr(0, limit) : text;
        },
        alert: function (title, text, fun, hideFun) {
            fun = fun || new Function();
            var alert = $('body').Dialog({
                title: title,
                body: text,
                footer: $('<button class="btn btn-primary">确定</button>').click(function (e) {
                    fun();
                    alert.hide();
                }),
                hidefun: hideFun,
                modal: 'alert'
            });
        },
        confirm: function (title, text, fun) {
            fun = fun || new Function();
            var ok = $('<button class="btn btn-primary">确定</button>').click(function (e) {
                alert.hide();
                fun();
            })
            var cancel = $('<button class="btn btn-warning">取消</button>').click(function (e) {
                alert.hide();
            });
            var alert = $('body').Dialog({
                title: title,
                body: text,
                footer: [ok, cancel],
                modal: 'alert'
            });
        }
        , imgLoad: function (img) {
            var parent = $(img).parents('[data-parent]');
            var FitWidth = parent.width();
            var FitHeight = parent.height();
            var image = {width: img.naturalWidth, height: img.naturalHeight}
            var height = (image.height * FitWidth) / image.width;
            var width = (image.width * FitHeight) / image.height;
            if (height > FitHeight) {
                var h = (height - FitHeight) / 2;
                img.width = FitWidth;
                if (h < FitHeight) {
                    img.style.marginTop = -h + 'px';
                }
            } else {
                img.style.marginLeft = -(width - FitWidth ) / 2 + 'px';
                img.height = FitHeight
            }
            $(img).removeClass('v-hidden');
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

    function mainBindEvent() {
        $('body').on('click', '[role="oh-like"]', function (e) {
            var like = $(this);
            var hackathon_name = like.data('name');
            var is_active = like.is('.active');
            var like_api = is_active ? oh.api.user.hackathon.like.delete : oh.api.user.hackathon.like.post;
            like_api({header: {hackathon_name: hackathon_name}}).then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    $('[data-likes="' + hackathon_name + '"]').each(function (i, e) {
                        var element = $(e);
                        var likes = Number(element.text());
                        element.text(is_active ? likes - 1 : likes + 1);
                    });
                    $('[role="oh-like"][data-name="' + hackathon_name + '"]')[(is_active ? 'remove' : 'add') + 'Class']('active');
                }
            });
        });

        $('body').on('load', 'img[data-role="img-load"]', function (e) {
            console.log(e.target);
        });
        $('[data-toggle="tooltip"]').tooltip();
        if (location.pathname.search('logout', 'i') != -1) {
            location.href = '/login';
            return;
        }
        w.oh.comm.createLoading('[loading]');
        addTabsEvent();
        var menu = $('#sidebar-left .main-menu').on('click', '.dropmenu', function (e) {
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

        menu.find('a').each(function () {
            if ($($(this))[0].href == String(window.location)) {
                $(this).parent().addClass('active');
                $(this).parents('ul').add(this).each(function () {
                    $(this).show();
                    $(this).prev('a').find('.chevron').removeClass('closed').addClass('opened')
                })
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

        $('[data-toggle="bindtemp"]').each(function (i, o) {
            bindData($(o));
        });

        var getUserUnreadNotice = function () {
            oh.api.hackathon.notice.list.get({
                query: {
                    filter_by_user: "unread" //"unread": list current user's unread notice; "all": list current user's all notices
                }
            }, function (data) {
                if (!data.error) {
                    data = data.items;
                    var message_num = data.length;
                    $('[data-mq]').text(message_num);
                    var nothing = $('.m-nothing');
                    if (message_num > 0) {
                        $('.m-count').addClass('active');
                        $('.m-messages').remove();
                        nothing.hide();
                        for (var i = 0; i < message_num; ++i) {
                            nothing.after('<li class="m-messages" data-id="' + data[i].id + '"><div><a target="_blank" href="' + data[i].link + '">' + data[i].content + '</a></div></li>');
                        }
                    }
                    else {
                        $('.m-count').removeClass('active');
                        $('.m-messages').remove();
                        nothing.removeAttr('style');
                    }
                }
            });
        };

        $('body').on('click', '.m-messages', function () {
            var id = $(this).data('id');
            oh.api.user.notice.read.put({
                body: {
                    id: id
                }
            }, function (data) {
                getUserUnreadNotice();
            });
        });

        //if user login, get its unread notice
        if($('.messages').length > 0) {
            getUserUnreadNotice();
        };
    }

    $(function () {
        mainBindEvent();
        if (window.moment) {
            moment.locale('zh-cn', {
                months: '一月_二月_三月_四月_五月_六月_七月_八月_九月_十月_十一月_十二月'.split('_'),
                monthsShort: '1月_2月_3月_4月_5月_6月_7月_8月_9月_10月_11月_12月'.split('_'),
                weekdays: '星期日_星期一_星期二_星期三_星期四_星期五_星期六'.split('_'),
                weekdaysShort: '周日_周一_周二_周三_周四_周五_周六'.split('_'),
                weekdaysMin: '日_一_二_三_四_五_六'.split('_'),
                longDateFormat: {
                    LT: 'Ah点mm分',
                    LTS: 'Ah点m分s秒',
                    L: 'YYYY-MM-DD',
                    LL: 'YYYY年MMMD日',
                    LLL: 'YYYY年MMMD日Ah点mm分',
                    LLLL: 'YYYY年MMMD日ddddAh点mm分',
                    l: 'YYYY-MM-DD',
                    ll: 'YYYY年MMMD日',
                    lll: 'YYYY年MMMD日Ah点mm分',
                    llll: 'YYYY年MMMD日ddddAh点mm分'
                },
                meridiemParse: /凌晨|早上|上午|中午|下午|晚上/,
                meridiemHour: function (hour, meridiem) {
                    if (hour === 12) {
                        hour = 0;
                    }
                    if (meridiem === '凌晨' || meridiem === '早上' ||
                        meridiem === '上午') {
                        return hour;
                    } else if (meridiem === '下午' || meridiem === '晚上') {
                        return hour + 12;
                    } else {
                        // '中午'
                        return hour >= 11 ? hour : hour + 12;
                    }
                },
                meridiem: function (hour, minute, isLower) {
                    var hm = hour * 100 + minute;
                    if (hm < 600) {
                        return '凌晨';
                    } else if (hm < 900) {
                        return '早上';
                    } else if (hm < 1130) {
                        return '上午';
                    } else if (hm < 1230) {
                        return '中午';
                    } else if (hm < 1800) {
                        return '下午';
                    } else {
                        return '晚上';
                    }
                },
                calendar: {
                    sameDay: function () {
                        return this.minutes() === 0 ? '[今天]Ah[点整]' : '[今天]LT';
                    },
                    nextDay: function () {
                        return this.minutes() === 0 ? '[明天]Ah[点整]' : '[明天]LT';
                    },
                    lastDay: function () {
                        return this.minutes() === 0 ? '[昨天]Ah[点整]' : '[昨天]LT';
                    },
                    nextWeek: function () {
                        var startOfWeek, prefix;
                        startOfWeek = _moment__default().startOf('week');
                        prefix = this.unix() - startOfWeek.unix() >= 7 * 24 * 3600 ? '[下]' : '[本]';
                        return this.minutes() === 0 ? prefix + 'dddAh点整' : prefix + 'dddAh点mm';
                    },
                    lastWeek: function () {
                        var startOfWeek, prefix;
                        startOfWeek = _moment__default().startOf('week');
                        prefix = this.unix() < startOfWeek.unix() ? '[上]' : '[本]';
                        return this.minutes() === 0 ? prefix + 'dddAh点整' : prefix + 'dddAh点mm';
                    },
                    sameElse: 'LL'
                },
                ordinalParse: /\d{1,2}(日|月|周)/,
                ordinal: function (number, period) {
                    switch (period) {
                        case 'd':
                        case 'D':
                        case 'DDD':
                            return number + '日';
                        case 'M':
                            return number + '月';
                        case 'w':
                        case 'W':
                            return number + '周';
                        default:
                            return number;
                    }
                },
                relativeTime: {
                    future: '%s内',
                    past: '%s前',
                    s: '几秒',
                    m: '1 分钟',
                    mm: '%d 分钟',
                    h: '1 小时',
                    hh: '%d 小时',
                    d: '1 天',
                    dd: '%d 天',
                    M: '1 个月',
                    MM: '%d 个月',
                    y: '1 年',
                    yy: '%d 年'
                },
                week: {
                    // GB/T 7408-1994《数据元和交换格式·信息交换·日期和时间表示法》与ISO 8601:1988等效
                    dow: 1, // Monday is the first day of the week.
                    doy: 4  // The week that contains Jan 4th is the first week of the year.
                }
            });
        }
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
            hidefun: function () {
            },
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
            var _seft = this;
            this.layout.on('hidden.bs.modal', function (e) {
                e.target.remove();
                if (_seft.params.hidefun) {
                    _seft.params.hidefun();
                }
            });
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