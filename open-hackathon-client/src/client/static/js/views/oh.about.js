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
