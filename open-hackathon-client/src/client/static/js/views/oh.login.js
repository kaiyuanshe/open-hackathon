/*
 * This file is covered by the LICENSING file in the root of this project.
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
                    if(isWechatBrowser()){
                        openWindow(CONFIG.wechat_mobile.authorize_url);
                        break;
                    } else {
                        openWindow(CONFIG.wechat.authorize_url);
                        break;
                    }
            }
        })
    };

    //判断是否是微信浏览器
    function isWechatBrowser() {
        var ua = window.navigator.userAgent.toLowerCase();
        if (ua.match(/MicroMessenger/i) == 'micromessenger') {
            return true;
        } else {
            return false;
        }
    }

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
