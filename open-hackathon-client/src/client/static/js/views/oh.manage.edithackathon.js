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
    var hackathonName = '',
        hackathonID = 0,
        files = [];

    var currentHackathon = oh.comm.getCurrentHackathon();

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

    function gethackathon() {
        oh.api.admin.hackathon.get({
            header: {hackathon_name: currentHackathon}
        }, function (data) {
            if (!data.error) {
                setFormData(data);
                oh.comm.removeLoading();
            }
        });
    }

    //setup ckeditor
    function ckeditorSetup() {
        var editorElement = CKEDITOR.document.getById( 'markdownEdit' );
        CKEDITOR.replace(editorElement, {
            language: 'zh-cn',
            width:  'auto',
            height: '220'
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
        gethackathon();
        $('.bootstrap-tagsinput input:text').removeAttr('style');

        var banner_form = $('#addBannerForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var banner = banner_form.find('#banner');
                addFile({guid: oh.comm.guid(), url: banner.val()});
                banner_form.data().bootstrapValidator.resetForm();
                bannerModal.modal('hide');
            });

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
    }

    function setDaterange(elem, value) {
        elem.val(value).daterangepicker({
            timePicker: true,
            format: 'YYYY/MM/DD HH:mm',
            timePickerIncrement: 30,
            timePicker12Hour: false,
            timePickerSeconds: false,
            locale: oh.daterangepickerLocale
        });
    }

    function setFormData(data) {
        hackathonID = data.id;
        hackathonName = data.name;
        data.basic_info = data.basic_info || {};
        $('#name').text(data.name);
        $('#hackathon_switch').val(data.status);
        $('#display_name').val(data.display_name);
        $('#short_description').val(data.short_description);
        $('#ribbon').val(data.ribbon);
        //ckeditor may be either ready or not ready here.
        CKEDITOR.instances["markdownEdit"].on('instanceReady', function() {
            CKEDITOR.instances["markdownEdit"].setData(data.description);
        }); //if ckeditor is not ready, wait 'instanceReady' signal and setFormData, else not effective
        CKEDITOR.instances["markdownEdit"].setData(data.description); //if ckeditor is ready, setFormData, else not effective
        setDaterange($('#event_time'), startTimeAndEndTimeTostring(data.event_start_time, data.event_end_time));
        setDaterange($('#register_time'), startTimeAndEndTimeTostring(data.registration_start_time, data.registration_end_time));
        setDaterange($('#judge_time'), startTimeAndEndTimeTostring(data.judge_start_time, data.judge_end_time));
        $('#tags').tagsinput('add', data.tag);
        $('#location').val(data.config.location);
        $('#max_enrollment').val(data.config.max_enrollment);
        $('#auto_approve').attr({checked: Number(data.config.auto_approve) == 1});
        $('#alauda_enabled').attr({checked: Number(data.config.alauda_enabled) == 1});
        $('#freedom_team').attr({checked: Number(data.config.freedom_team) == 1});
        setLoginPprovider(Number(data.config.login_provider || 0))
        initFilesData(data.banners);
    }

    function setLoginPprovider(value) {
        $('[data-role="login_provider"]').each(function (i, ele) {
            var box = $(ele);
            var v = Number(box.val());
            box.attr({checked: (value & v) == v});
        });
    }

    function initFilesData(banners) {
        var images = banners ? banners.split(';') : [];
        $.each(images, function (i, url) {
            addFile({guid: oh.comm.guid(), url: url});
        });
    }

    function startTimeAndEndTimeTostring(startTime, endTime) {
        if (!startTime && !endTime) {
            return ''
        }
        return moment(startTime).format('YYYY/MM/DD HH:mm ') + '- ' + moment(endTime).format('YYYY/MM/DD HH:mm');
    }

    function getHackathonData() {
        var event_time = $('#event_time').data('daterangepicker');
        var register_time = $('#register_time').data('daterangepicker');
        var judge_time = $('#judge_time').data('daterangepicker');
        var data = {
            id: hackathonID,
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

    function update_hackathon(data) {
        return oh.api.admin.hackathon.put(data);
    }

    function update_config(data) {
        return oh.api.admin.hackathon.config.put(data);
    }

    function update_tags(data) {
        return oh.api.admin.hackathon.tags.put(data);
    }

    function initControls() {
        $('#editHackathonForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();

                ckeditorUpdateTextarea();

                var hack_data = getHackathonData();
                var config_data = getConfig();
                var tags_data = getTags();

                update_hackathon({body: hack_data, header: {hackathon_name: hackathonName}}).then(function (data) {
                    if (data.error) {
                        oh.comm.alert('错误', data.error.friendly_message);
                    } else {
                        update_config({
                            header: {hackathon_name: hackathonName},
                            body: config_data
                        }).then(function (data) {
                            if (data.error) {
                                oh.comm.alert('错误', data.error.friendly_message);
                            } else {
                                update_tags({
                                    header: {hackathon_name: hackathonName},
                                    body: tags_data
                                }).then(function (data) {
                                    if (data.error) {
                                        oh.comm.alert('错误', data.error.friendly_message);
                                    } else {
                                        oh.comm.alert('提示', '修改成功');
                                    }
                                });
                            }
                        });
                    }
                });
            });

        $('#hackathon_switch').change(function (e) {
            var status = $(this).val();
            oh.api.admin.hackathon.put({
                body: {
                    id: hackathonID,
                    name: hackathonName,
                    status: status
                },
                header: {
                    hackathon_name: hackathonName
                }
            }, function (data) {
                if (data.error) {
                    console.log(data);
                }
            });
        })
    }

    function init() {
        pageload();
        initControls();
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);