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

(function($, oh) {

    var image_ratio = 1.3148148148148149;

    function openWindow(url, width) {
    //    width = width || 600;
    //    var l, t;
    //    l = (screen.width - width ) / 2;
    //    t = (screen.height - 400) / 2;
    //    window.open(url, '_blank', 'toolbar=no, directories=no, status=yes,location=no, menubar=no, width=' + width + ', height=500, top=' + t + ', left=' + l);
        window.location.href = url
    };

    function pageLoad(){
        var resbgimg = $('[oh-resizebgimage]').load(function (e) {
            $(window).trigger('resize');
        });
        setTimeout(function(){
            $(window).trigger('resize');
        },0)
        $(window).resize(function () {
            resbgimg.css(scale());
        });

        $('[data-login]').click(function(e){
            var key = $(this).data('login');
            switch(key){
                case 'live':
                    openWindow(CONFIG.live.authorize_url);
                    break;
                case 'github':
                    openWindow(CONFIG.github.authorize_url);
                    break;
                case 'qq':
                    openWindow(CONFIG.qq.authorize_url);
                    break;
                case 'weibo':
                    openWindow(CONFIG.weibo.authorize_url);
                    break;
                case 'wechat':
                    openWindow(CONFIG.wechat.authorize_url);
                    break;
                case 'alauda':
                    openWindow(CONFIG.alauda.authorize_url);
                    break;
            }
        })
    };

    function scale() {
        var width = $(window).width() - 400,
            height = $(window).height(),
            dWidth = width,
            dheight = Math.round(dWidth / image_ratio),
            css = {width: dWidth, height: dheight};
        if (dheight < height && (dheight = height,  dWidth = Math.round(dheight * image_ratio))) {
            css.width = dWidth;
            css.height = dheight;
        }
        return css;
    };

    function init(){
        pageLoad();
    };

    $(function() {
        init();
    });

})(window.jQuery,window.oh);
