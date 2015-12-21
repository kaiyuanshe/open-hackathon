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
        hackathonID = 0;

    function getHackthonData() {
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
            banners: '',//getFilesString(),
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
        data.push({key: 'location', value: ''});
        data.push({key: 'max_enrollment', value: 0});
        data.push({key: 'auto_approve', value: true});
        data.push({key: 'alauda_enabled', value: false});
        data.push({key: 'recycle_enabled', value: false});
        data.push({key: 'recycle_minutes', value: 0});
        data.push({key: 'pre_allocate_enabled', value: false});
        data.push({key: 'pre_allocate_number', value: 1});
        data.push({key: 'freedom_team', value: true});
        data.push({key: 'login_provider', value: 1 | 2 | 4 | 8 | 16 | 32});
        return data;
    }

    function getTemplateStatus(status) {
        var str = '';
        switch (status) {
            case 0:
                str = '未诊断';
                break;
            case 1:
                str = '诊断通过';
                break;
            case 2:
                str = '诊断失败';
                break;
        }
        return str;
    }

    function create_hackathon(data) {
        return oh.api.admin.hackathon.post(data);
    }

    function add_config(data) {
        return oh.api.admin.hackathon.config.post(data);
    }

    //
    //function getHackathonTemplates(hackathon_name) {
    //    var name = hackathon_name || hackathonName;
    //    if (name) {
    //        return oh.api.admin.hackathon.template.list.get({
    //            header: {hackathon_name: name}
    //        }, function (data) {
    //            if (data.error) {
    //            } else {
    //                hackathon_templates = data;
    //                $('#template_list').empty().append($('#template_item').tmpl(data, {
    //                    hackathon_name: name,
    //                    getStatus: getTemplateStatus
    //                }));
    //            }
    //        });
    //    }
    //};

    function getPublictTempates() {
        return oh.api.template.list.get({query: {}}, function (data) {
            if (data.error) {
            } else {
                var classStatus = {0: 'default', 1: 'success', 2: 'failure'};
                $('#template_list').empty().append($('#template_item').tmpl(data, {
                    getStatus: getTemplateStatus,
                    getItemClass: function (id, status) {
                        var class_name = '';

                        //class_name += classStatus[status];
                        return class_name;
                    }
                }));
            }
        });
    }

    function getAzureList() {
        var name = hackathon_name || hackathonName;
        if (name) {
            return oh.api.admin.azure.get({header: {hackathon_name: name}}, function (data) {
                $('#azure_list').empty().append($('#azure_cert_item').tmpl(data));
            });
        }

    }

    function init() {
        bindEvent();
        pageload();
    }

    function pageload() {
        $('#event_time,#register_time,#judge_time').daterangepicker({
            timePicker: true,
            format: 'YYYY/MM/DD HH:mm',
            timePickerIncrement: 30,
            timePicker12Hour: false,
            timePickerSeconds: false,
            locale: oh.daterangepickerLocale
        });

        $('.bootstrap-tagsinput input:text').removeAttr('style');

        $('#markdownEdit').markdown({
            hiddenButtons: 'cmdCode',
            language: 'zh'
        });
    }


    function bindEvent() {
        //var bannerModal = $('#bannerModal').on('hide.bs.modal', function (e) {
        //    banner_form.get(0).reset();
        //    banner_form.data().bootstrapValidator.resetForm();
        //});

        //$('.btn-upload').bind('click', function (e) {
        //    bannerModal.modal('show');
        //});
        //
        //$('.fileupload-buttonbar').on('click', '[data-action="close"]', function (e) {
        //    var a = $(this);
        //    var guid = a.data('guid');
        //    a.parents('.template-download').detach();
        //    removeFile(guid);
        //});

        //var banner_form = $('#addBannerForm').bootstrapValidator()
        //    .on('success.form.bv', function (e) {
        //        e.preventDefault();
        //        var banner = $('#banner');
        //        addFile({guid: oh.comm.guid(), url: banner.val()});
        //        banner_form.data().bootstrapValidator.resetForm();
        //        bannerModal.modal('hide');
        //    });

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

            var hack_data = getHackthonData();
            var config_data = getConfig();

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

                        }
                    });
                }
            })
        });

        $('#refresh_tmp').click(function (e) {
            getPublictTempates();
        }).trigger('click');
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);
