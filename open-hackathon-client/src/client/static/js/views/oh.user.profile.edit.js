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
        oh.api.user.get({}, function (data) {
            if (!data.error) {
                setFormData(data.profile || {});
                if(data.profile) {
                  isProfile = true;
                }
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

    function disableItems(list) {
        for (var index in list)
            $(list[index]).attr('disabled', true);
    }

    function enableItems(list) {
        for (var index in list)
            $(list[index]).removeAttr('disabled');
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
                var picture = $('#user_logo_input').val();
                updatePicture(picture).then(function (data) {
                    if (data.error) {
                        oh.comm.alert('错误', data.error.friendly_message);
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

        // upload file about user logo
        $("#user_logo_upload").fileupload({
            type: 'POST',
            url: CONFIG.apiconfig.proxy + '/api/user/file?file_type=user_file',
            dataType: 'json',
            beforeSend: function (xhr, data) {
                xhr.setRequestHeader('token', $.cookie('token'));
            },
            start: function () {
                $('#user_logo_upload_span').text('文件上传中，上传成功将会自动跳转，请稍等...');
                disableItems(['#user_logo_input', '#user_logo_upload_btn', '#user_logo_submit', '#user_logo_cancel']);
            },
            done: function (e, obj) {
                var data = obj.result;
                if (data.error || ! "files" in data || data.files.length == 0) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    var url = data.files[0].url;
                    oh.api.user.picture.put({body: {url: url}}).then(function (data) {
                        if (data.error) {
                            oh.comm.alert('错误', data.error.friendly_message);
                        } else {
                            $('#user_logo').attr({src: url});
                            $('#user_logo_input').val("");
                            $('#pictureModal').modal('hide');
                            $('#user_logo_upload_span').text('上传文件');
                            enableItems(['#user_logo_input', '#user_logo_upload_btn', '#user_logo_submit',
                                         '#user_logo_cancel']);
                            oh.comm.alert("提示", "设置成功!");
                        }
                    });
                }
            }
        });
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);
