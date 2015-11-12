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
        hackathonID = 0;

    var currentHackathon = oh.comm.getCurrentHackathon();

    function bindAwardList() {
        var list = $('#awardlist');
        oh.api.admin.team.list.get({
            header: {hackathon_name: currentHackathon}
        }, function (data) {
            if (!data.error) {
                list.empty().append($('#hackathon_award').tmpl(data || [], {
                    hackathon_name: currentHackathon
                }));
                oh.comm.removeLoading();
            }
        });
    }

    function toggleTable() {
        if ($('#awardtable').css('display') == 'none') {
            $('#awardtable').show();
            $('#awardform').hide()
        } else {
            $('#awardtable').hide();
            $('#awardform').show()
        }
    }

    function getFormData() {
        var formData = {
            id: $('#awardform').data('id') || 0,
            name: $.trim($('#name').val()),
            level: $('#level').val(),
            quota: $('#quota').val(),
            description: $('#description').val()
        }
        return formData;
    }

    function setFormData(data) {
        $('#awardform').data({id: data.id});
        $('#name').val(data.name);
        $('#level').val(data.level);
        $('#quota').val(data.quota);
        $('#description').val(data.description);
    }

    function getAward() {
        var list = [];
        $('#awardtable tbody>tr').each(function (i, tr) {
            var data = $(tr).data('tmplItem').data;
            if (data) {
                list.push($(tr).data('tmplItem').data);
            }
        })
        return list;
    }

    function createAward(data) {
        return oh.api.admin.hackathon.award.post(data, function (data) {
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                bindAwardList();
                resetForm();
            }
        });
    }

    function updateAward(data) {
        return oh.api.admin.hackathon.award.put(data, function (data) {
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                bindAwardList();
                resetForm();
            }
        });
    }

    function deleteAward(data) {
        return oh.api.admin.hackathon.award.delete(data);
    }

    function resetForm() {
        var form = $('#awardform');
        form.data({id: 0});
        form.find('bootstrapValidator').resetForm(true);
        $('#level').val(5);
        $('#quota').val(1);
        $('#description').val('');
    }

    function init() {
        var awardform = $('#awardform');
        awardform.bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var itemData = getFormData();
                var data = {body: itemData, header: {hackathon_name: currentHackathon}};
                (itemData.id == 0 ? createAward(data) : updateAward(data)).then(function () {
                    toggleTable();
                })
            });

        $('#awardtable').on('click', '[data-type="edit"]', function (e) {
            editLi = $(this).parents('tr')
            var item = editLi.data('tmplItem').data;
            setFormData(item)
            toggleTable();
        });

        $('[data-type="cancel"]').click(function (e) {
            resetForm();
            toggleTable();
        });

        $('[data-type="new"]').click(function (e) {
            toggleTable();
        })

        var confirmModal = $('#confirm_modal').on('show.bs.modal', function (e) {
            console.log(e);
            editLi = $(e.relatedTarget).parents('tr');
        }).on('click', '[data-type="ok"]', function (e) {
            var id = editLi.data('tmplItem').data.id;
            confirmModal.modal('hide');
            deleteAward({query: {id: id}, header: {hackathon_name: currentHackathon}}).then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    editLi.detach();
                }
            });

        });

        bindAwardList();
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);