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
        oh.api.user.profile.get({}, function (data) {
            if (!data.error) {
                setFormData(data);
                isProfile = true;
            } else {
                console.log(data.error);
            }
        });
    }

    function setFormData(data) {
        var pform = $('#profileForm');
        $.each(data, function (key, value) {
            pform.find('input[name="' + key + '"]').val(value);
        })
    }

    function getFormData() {
        var pform = $('#profileForm');
        var data = {};
        pform.find('input,select,textarea').each(function (i, elm) {
            var input = $(elm);
            var val = input.val().trim();
            if(val.length)
              data[input.attr('name')] = input.val();
        });
        return data;
    }

    function profileFormValidator() {
        var pform = $('#profileForm').bootstrapValidator()
            .on('success.form.bv', function (e, ok) {
                e.preventDefault();
                var data = getFormData()
                if (isProfile) {
                    oh.api.user.profile.put({body: data}).then(callback);
                } else {
                    oh.api.user.profile.post({body: data}).then(callback);
                }
                function callback(data) {
                    //console.log(data);
                    $('#alert').modal('show')
                }
            });
    }

    function updatePicture(url) {
        return oh.api.user.picture.put({body: {url: url}});
    }

    function init() {
        pageload();
        profileFormValidator();
        var alert = $('#alert').on('click', ' [data-type="ok"]', function (e) {
            var url = $.getUrlParam('return_url');
            if (url) {
                window.location.href = url;
            } else {
                alert.modal('hide');
            }
        });
        var picture_form = $('#pictureForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var picture = $('#picture').val();
                updatePicture(picture).then(function (data) {
                    if (data.error) {
                        oh.comm.alert('����', data.error.friendly_message);
                    } else {
                        $('img[data-role="picture"]').attr({src: picture});
                        $.ajax({
                            url: '/user/picture',
                            method: 'POST',
                            data: {url: picture}
                        });
                    }
                });
                picture_form.data().bootstrapValidator.resetForm();
                pictureModal.modal('hide');
            });

        var pictureModal = $('#pictureModal').on('hide.bs.modal', function (e) {
            picture_form.get(0).reset();
            picture_form.data().bootstrapValidator.resetForm();
        });
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);
