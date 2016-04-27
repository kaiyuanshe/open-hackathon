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
        is_local = islocal,
        _create_data = {};

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
        data.push({key: 'login_provider', value: 1 | 2 | 4 | 8 | 32 | 64});
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

    function set_alauda_enabled() {
        return oh.api.admin.hackathon.config.put({
            header: {hackathon_name: hackathonName},
            body: [{key: 'alauda_enabled', value: 1}]
        });
    }

    function addHackathonTemplate(data) {
        return oh.api.admin.hackathon.template.post({
            body: data,
            header: {hackathon_name: hackathonName}
        });
    };

    function removeHackathonTemplate(data) {
        return oh.api.admin.hackathon.template.delete({
            query: data,
            header: {hackathon_name: hackathonName}
        });
    }

    function can_online() {
        return oh.api.admin.hackathon.canonline.get({header: {hackathon_name: hackathonName}});
    }

    function online() {
        return oh.api.admin.hackathon.put({
            body: {
                id: _create_data.id,
                name: hackathonName,
                status: 1
            },
            header: {
                hackathon_name: hackathonName
            }
        }, function (data) {
            if (data.error) {
                console.log(data);
            }
        });
    }

    function getPublictTempates() {
        return oh.api.template.list.get({query: {}}, function (data) {
            if (data.error) {
            } else {
                var classStatus = {0: 'default', 1: 'success', 2: 'failure'};
                var teml_list = $('#template_list').empty();
                teml_list.append($('#template_item').tmpl(data, {
                    getStatus: getTemplateStatus,
                    getItemClass: function (id, status) {
                        var items = teml_list.data('items') || [];
                        var class_name = '';
                        $.each(items, function (i, item) {
                            if (item.id == id) {
                                class_name += 'active ';
                                return false;
                            }
                        });
                        return class_name;
                    }
                }));
            }
        });
    }

    function getAzureList(hackathon_name) {
        var name = hackathon_name || hackathonName;
        if (name) {
            return oh.api.admin.azure.get({header: {hackathon_name: name}}, function (data) {
                $('#azure_list').empty().append($('#azure_cert_item').tmpl(data));
            });
        }
    }

    function postAzure() {
        return oh.api.admin.azure.post({
            body: {
                subscription_id: $('#subscription_id').val(),
                management_host: $('#management_host').val()
            },
            query: {},
            header: {hackathon_name: hackathonName}
        });
    }

    function deleteAzure(id) {
        return oh.api.admin.azure.delete({
            query: {certificate_id: id},
            header: {hackathon_name: hackathonName}
        });
    }

    //setup ckeditor
    function ckeditorSetup() {
        var editorElement = CKEDITOR.document.getById('markdownEdit');
        CKEDITOR.replace(editorElement, {
            language: 'zh-cn'
            , width: 'auto'
            , height: '220'
        });
    }

    //update before uploading, otherwise changes won't be saved
    function ckeditorUpdateTextarea() {
        for (instance in CKEDITOR.instances) {
            CKEDITOR.instances[instance].updateElement();
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

        ckeditorSetup();
    }


    function bindEvent() {
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
                            _create_data = data;
                            nextStep('step2', function () {
                                $('#refresh_tmp').trigger('click');
                            });
                        }
                    });
                }
            })
        });
        $('#stepform2').bootstrapValidator().on('success.form.bv', function (e) {
            e.preventDefault();
            var items = temp_list.data('items');
            if (items.length == 0) {
                oh.comm.alert('提示', '请选中image模板');
            } else {
                nextStep('step3');
            }
        });

        var form4 = $('#stepform4').bootstrapValidator().on('success.form.bv', function (e) {
            e.preventDefault();
            var check_btn = $('#azure_list a[data-type="check"]:eq(0)').trigger('click', [function (isPass) {
                if (isPass) {
                    nextStep('step5');
                }
            }]);
            if (check_btn.length == 0) {
                $('[data-target="#crate_azure_modal"]').trigger('click');
            }
            form4.removeAttr('disabled');
            form4.find('button:submit').removeAttr('disabled');
        });

        var azure_form = $('#new_azurecertform');
        azure_form.bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var azure_div = azure_list.find('.azure:eq(0)');
                if (azure_div.length > 0) {
                    deleteAzure(azure_div.data('tmplItem').data.id);
                }
                postAzure().then(function (data) {
                    if (data.error) {

                    } else {
                        getAzureList(hackathonName);
                        $('#crate_azure_modal').modal('hide');
                    }
                    azure_form.get(0).reset();
                    azure_form.data().bootstrapValidator.resetForm();
                });
            });

        $('#refresh_tmp').click(function (e) {
            getPublictTempates();
            $('#step2').find('from').attr({disabled: 'disabled'});
            $('#step2').find('button:submit').attr({disabled: 'disabled'});
        })

        var temp_list = $('#template_list').on('click', '.oh-tempitem', function (e) {
            var item = $(this);
            var items = temp_list.data('items')
            var data = item.parent().data('tmplItem').data;
            item.toggleClass('active', function (cla) {
                if ($(this).is('.active')) {
                    items.push(data);
                    addHackathonTemplate({template_id: data.id})
                } else {
                    var index = -1;
                    $.each(items, function (i, o) {
                        if (o.id == data.id) {
                            index = i;
                            return false;
                        }
                    });
                    items.splice(index, 1);
                    removeHackathonTemplate({template_id: data.id})
                }
                if (items.length == 0) {
                    $('#step2').find('from').attr({disabled: 'disabled'});
                    $('#step2').find('button:submit').attr({disabled: 'disabled'});
                } else {
                    $('#step2').find('from').removeAttr('disabled');
                    $('#step2').find('button:submit').removeAttr('disabled');
                }
            });
        }).data({'items': []});

        $('#step3').on('click', 'button[data-name]', function (e) {
            var name = $(this).data('name');
            if (name == 'alauda') {
                set_alauda_enabled().then(function (data) {
                    if (data.error) {
                        oh.comm.alert('错误', data.error.friendly_message);
                    } else {
                        nextStep('step5');
                    }
                });
            } else if (name == 'azure' && !is_local) {
                nextStep('step4');
            } else {
                nextStep('step5');
            }
        });

        var azure_list = $('#azure_list').on('click', 'a[data-type="check"]', function (e, fun) {
            var azure = $(this).parents('.azure').data('tmplItem').data;
            azure_list.data({'id': azure.id});
            can_online().then(function (data) {
                if (data.message) {
                    if (fun) {
                        fun(true);
                    } else {
                        oh.comm.alert('提示', '证书授权成功。');
                    }
                } else {
                    deleteAzure(azure.id);
                    oh.comm.alert('提示', '证书授权失败，请检验SUBSCRIPTION ID是否正确。');
                    if (fun) {
                        fun(false);
                    }
                }
            });
        }).data({id: 0});

        var online_btn = $('#online').click(function (e) {
            online().then(function (data) {
                oh.comm.alert('提示', '<p>活动已经上线。<a href="/site/' + hackathonName + '">前往活动页</a></p>', null, function () {
                    online_btn.detach();
                });
            });
        });
        $('#links').on('click', 'a', function (e) {
            var name = $(this).data('name');
            window.location.href = '/manage/' + hackathonName + '/' + name;
        })
    }

    var steps = {};

    function nextStep(id, fun) {
        fun = fun || new Function();
        var _index = 0;
        steps.each(function (i, step) {
            var s = $(step);
            if (s.attr('id') != id) {
                s.detach();
            } else {
                $('.step-content').append(s.addClass('active'));
                fun();
                _index = i + 2;
            }
        });
        return _index;
    }

    $(function () {
        steps = $('.step-pane');
        init();
        var i = nextStep('step1');
    })
})(window.jQuery, window.oh);
