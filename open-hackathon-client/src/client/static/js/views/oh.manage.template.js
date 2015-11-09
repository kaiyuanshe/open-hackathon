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
    var currentHackathon = oh.comm.getCurrentHackathon();
    var hackathon_templates = [];

    function getStatus(status) {
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

    function getHackathonTemplates() {
        return oh.api.admin.hackathon.template.list.get({
            header: {hackathon_name: currentHackathon}
        }, function (data) {
            if (data.error) {
                // todo Get Hackathon tempalte list error
            } else {
                hackathon_templates = data;
                $('#templatelist').empty().append($('#table_template').tmpl(data, {
                    hackathon_name: currentHackathon,
                    getStatus: getStatus
                }));
            }
        });
    };

    function getPublictTempates() {
        return oh.api.template.list.get({
            query: {}
        }, function (data) {
            var classStatus = {0: 'default', 1: 'success', 2: 'failure'};
            $('#template_list').empty().append($('#template_item').tmpl(data, {
                getStatus: getStatus,
                getItemClass: function (id, status) {
                    var class_name = '';
                    $.each(hackathon_templates, function (i, item) {
                        if (item.template_id == id) {
                            class_name += 'active ';
                            return false;
                        }
                    });
                    class_name += classStatus[status];
                    return class_name;
                }
            }));
        });
    }

    function addHackathonTemplate(data) {
        return oh.api.admin.hackathon.template.post({
            body: data,
            header: {hackathon_name: currentHackathon}
        });
    };

    function removeHackathonTemplate(data) {
        return oh.api.admin.hackathon.template.delete({
            query: data,
            header: {hackathon_name: currentHackathon}
        });
    }

    function pageLoad() {
        getHackathonTemplates();
    }

    function toggleTable() {
        if ($('#templatetable').is('.hide')) {
            $('#templatetable').removeClass('hide');
            $('#templates').addClass('hide');
        } else {
            $('#templatetable').addClass('hide');
            $('#templates').removeClass('hide');
        }
    }

    function init() {
        bingEvent();
        pageLoad();
    }

    function bingEvent() {
        var confirm_modal = $('#confirm_modal').on('show.bs.modal', function (e) {
            confirm_modal.data({callback: e.relatedTarget})
        }).on('click', '[data-type="ok"]', function (e) {
            confirm_modal.data('callback')();
        })

        $('[data-type="add_template"]').click(function (e) {
            getPublictTempates();
            toggleTable();
        });

        $('[data-type="return"]').click(function (e) {
            getHackathonTemplates();
            toggleTable();
        });

        $('#templatelist').on('click', 'a[data-role="delete"]', function (e) {
            var tr = $(this).parents('tr')
            var data = tr.data('tmplItem').data;
            confirm_modal.find('.modal-body p').text('确定是否移除该模板？');
            confirm_modal.modal('show', function () {
                removeHackathonTemplate({template_id: data.id}).then(function (data) {
                    if (data.error) {
                        //todo remove hackathon template error;
                    } else {
                        tr.detach();
                    }
                    confirm_modal.modal('hide');
                });
            });
        });
        $('#template_list').on('click', '.oh-tempitem', function (e) {
            var item = $(this);
            var data = item.parent().data('tmplItem').data;

            if (item.is('.active')) {
                confirm_modal.find('.modal-body p').text('确定是否移除该模板？');
                confirm_modal.modal('show', function () {
                    removeHackathonTemplate({template_id: data.id}).then(function (data) {
                        if (data.error) {
                            //todo remove hackathon template error;
                        } else {
                            item.removeClass('active');
                        }
                        confirm_modal.modal('hide');
                    });
                });
            } else if (data.status == 1) {
                addHackathonTemplate({template_id: data.id}).then(function (data) {
                    if (data.error) {
                        //todo add hackathon template error;
                    } else {
                        item.addClass('active');
                    }
                    confirm_modal.modal('hide');
                });
            } else {
                confirm_modal.find('.modal-body p').text('该模板还未诊断成功，是否确定该模板？');
                confirm_modal.modal('show', function () {
                    addHackathonTemplate({template_id: data.id}).then(function (data) {
                        if (data.error) {
                            //todo add hackathon template error;
                        } else {
                            item.addClass('active');
                        }
                        confirm_modal.modal('hide');
                    });
                });
            }
        })
    }

    $(function () {
        init();
    })

})
(window.jQuery, window.oh);