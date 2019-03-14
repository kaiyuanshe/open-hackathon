/*
 * This file is covered by the LICENSING file in the root of this project.
 */

(function ($, oh) {
    'use strict';

    var isProfile = false;

    function pageload() {
        $('body').scrollspy({
            target: '#lift',
            offset: 150
        })
    }

    function getFormData() {
        var form = $('#form');
        var data = {};
        form.find('input,select,textarea').each(function (i, elm) {
            var input = $(elm);
            var val = input.val().trim();
            if (val.length)
                data[input.attr('name')] = input.val();
        });
        return data;
    }

    function profileFormValidator() {
        var pform = $('#profileForm').bootstrapValidator()
            .on('success.form.bv', function (e, ok) {
                e.preventDefault();
                var data = getFormData()


            });
    }


    function init() {
        pageload();
        profileFormValidator();
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);
