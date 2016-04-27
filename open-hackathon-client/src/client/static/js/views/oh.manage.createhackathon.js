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

(function ($) {
    $.fn.bootstrapValidator.i18n.remote1 = $.extend($.fn.bootstrapValidator.i18n.remote1 || {}, {
        'default': 'Please enter a valid value'
    });

    $.fn.bootstrapValidator.validators.remote1 = {
        html5Attributes: {
            message: 'message',
            checkfun: 'checkfun'
        },
        destroy: function (validator, $field, options) {
            if ($field.data('bv.remote1.timer')) {
                clearTimeout($field.data('bv.remote1.timer'));
                $field.removeData('bv.remote1.timer');
            }
        },
        validate: function (validator, $field, options) {
            return options.checkfun(validator, $field);
        }
    };
}(window.jQuery));

(function ($, oh) {

    var hackathonName = '',
        hackathonID = 0,
        files = [];

    function addFile(file) {
        files.push(file);
        $('#banner_btn').before($('#banner_temp').html().format(file));
    }

    function removeFile(guid) {
        for (var i in files) {
            if (files[i].guid === guid) {
                files.splice(i, 1);
                break;
            }
        }
    }

    function getFilesString() {
        var filesUrls = [];
        for (var i in files) {
            filesUrls.push(files[i].url);
        }
        return filesUrls.join(';');
    }

    function wizard(step) {
        $('.step-content .step-pane').each(function (i, pane) {
            if (i + 1 == step) {
                $(pane).addClass('active');
            } else {
                $(pane).removeClass('active');
            }
        });
    }

    function getHackathonData() {
        var event_time = $('#event_time').data('daterangepicker');
        var register_time = $('#register_time').data('daterangepicker');
        var judge_time = $('#judge_time').data('daterangepicker');
        hackathonName = $.trim($('#name').val());
        var data = {
            id: hackathonID,
            name: hackathonName,
            display_name: $.trim($('#display_name').val()),
            ribbon: $.trim($('#ribbon').val()),
            short_description: $.trim($('#short_description').val()),
            banners: getFilesString(),
            description: $('#markdownEdit').val(),
            event_start_time: event_time.startDate.format(),
            event_end_time: event_time.endDate.format(),
            registration_start_time: register_time.startDate.format(),
            registration_end_time: register_time.endDate.format(),
            judge_start_time: judge_time.startDate.format(),
            judge_end_time: judge_time.endDate.format()
        };
        return data;
    }

    function getConfig() {
        var data = [];
        data.push({key: 'location', value: $.trim($('#location').val())});
        data.push({key: 'max_enrollment', value: $('#max_enrollment').val()});
        data.push({key: 'auto_approve', value: $('#auto_approve').is(':checked')});
        data.push({key: 'alauda_enabled', value: $('#alauda_enabled').is(':checked')});
        data.push({key: 'recycle_enabled', value: false});
        data.push({key: 'recycle_minutes', value: 0});
        data.push({key: 'pre_allocate_enabled', value: false});
        data.push({key: 'pre_allocate_number', value: 1});
        data.push({key: 'freedom_team', value: $('#freedom_team').is(':checked')});
        data.push({key: 'login_provider', value: getLoginProviderValue()});
        return data;
    }

    function getLoginProviderValue() {
        var value = 0;
        $('[data-role="login_provider"]:checked').each(function (i, ele) {
            var box = $(ele);
            value += Number(box.val());
        });
        return value;
    }

    function getTags() {
        var data = $('#tags').tagsinput('items');
        return data.join(',');
    }

    function create_hackathon(data) {
        return oh.api.admin.hackathon.post(data);
    }

    function add_config(data) {
        return oh.api.admin.hackathon.config.post(data);
    }

    function add_tags(data) {
        return oh.api.admin.hackathon.tags.post(data);
    }

    function init() {
        bindEvent();
        pageload();
    }

    //setup ckeditor
    function ckeditorSetup() {
        var editorElement = CKEDITOR.document.getById( 'markdownEdit' );
        CKEDITOR.replace(editorElement, {
            language: 'zh-cn'
            , width:  'auto'
            , height: '220'
        });
    }

    //update before uploading, otherwise changes won't be saved
    function ckeditorUpdateTextarea() {
        for (instance in CKEDITOR.instances ) {
            CKEDITOR.instances[instance].updateElement();
        }
    }

    function pageload() {
        ckeditorSetup();

        $('#event_time,#register_time,#judge_time').daterangepicker({
            timePicker: true,
            format: 'YYYY/MM/DD HH:mm',
            timePickerIncrement: 30,
            timePicker12Hour: false,
            timePickerSeconds: false,
            locale: oh.daterangepickerLocale
        });

        $('.bootstrap-tagsinput input:text').removeAttr('style');
    }


    function bindEvent() {
        var bannerModal = $('#bannerModal').on('hide.bs.modal', function (e) {
            banner_form.get(0).reset();
            banner_form.data().bootstrapValidator.resetForm();
        });

        $('.btn-upload').bind('click', function (e) {
            bannerModal.modal('show');
        });

        $('.fileupload-buttonbar').on('click', '[data-action="close"]', function (e) {
            var a = $(this);
            var guid = a.data('guid');
            a.parents('.template-download').detach();
            removeFile(guid);
        });

        var banner_form = $('#addBannerForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var banner = $('#banner');
                addFile({guid: oh.comm.guid(), url: banner.val()});
                banner_form.data().bootstrapValidator.resetForm();
                bannerModal.modal('hide');
            });

        $('#stepform1').bootstrapValidator({
            fields: {
                name: {
                    validators: {
                        remote1: {
                            message: '黑客松名称已被使用',
                            checkfun: function (validator, $field) {
                                var dfd = new $.Deferred();
                                oh.api.admin.hackathon.checkname.get({
                                    query: {
                                        name: $field.val()
                                    }
                                }, function (data) {
                                    var response = {valid: true};
                                    dfd.resolve($field, 'remote1', response);
                                });
                                return dfd;
                            }
                        }
                    }
                }
            }
        }).on('success.form.bv', function (e) {
            e.preventDefault();

            ckeditorUpdateTextarea();
            
            var hack_data = getHackathonData();
            var config_data = getConfig();
            var tags_data = getTags();
            
            create_hackathon({body: hack_data}).then(function (data) {
                if (data.error) {
                    if (data.error.code == 412) {
                        $('#stepform1').data('bootstrapValidator')
                            .updateStatus('name', 'INVALID', 'remote1')
                            .validateField('name');
                    } else {
                        oh.comm.alert('错误', data.error.friendly_message);
                    }
                } else {
                    add_config({
                        header: {hackathon_name: hackathonName},
                        body: config_data
                    }).then(function (data) {
                        if (data.error) {
                            oh.comm.alert('错误', data.error.friendly_message);
                        } else {
                            add_tags({
                                header: {hackathon_name: hackathonName},
                                body: tags_data
                            }).then(function (data) {
                                if (data.error) {
                                    oh.comm.alert('错误', data.error.friendly_message);
                                } else {
                                    $('#goto_org').attr({href: '/manage/' + hackathonName + '/organizers'});
                                    wizard(2);
                                }
                            });
                        }
                    });
                }
            })
        });
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);
