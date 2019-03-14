/*
 * This file is covered by the LICENSING file in the root of this project.
 */

(function ($, oh) {

    function bind_event() {
        var wallpaper = $('.wallpaper');
        var activity1 = $('.activity').hover(function () {
            activity2.addClass('opacity');
            wallpaper.addClass('active');
        }, function () {
            activity2.removeClass('opacity');
            wallpaper.removeClass('active');
        }).click(function () {
            $.cookie("ohplpv", "true");
            return true
        });

        var activity2 = $('.activity-create').hover(function () {
            activity1.addClass('opacity');
            wallpaper.addClass('active');
        }, function () {
            activity1.removeClass('opacity');
            wallpaper.removeClass('active');
        }).click(function () {
            $.cookie("ohplpv", "true")
            return true
        });
        ;
    }

    function init() {
        bind_event();
    };

    $(function () {
        init();
    });

})(window.jQuery, window.oh);