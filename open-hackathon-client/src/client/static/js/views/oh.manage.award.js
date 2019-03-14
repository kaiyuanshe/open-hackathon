/*
 * This file is covered by the LICENSING file in the root of this project.
 */

(function ($, oh) {
    var hackathonName = '',
        hackathonID = 0;

    var currentHackathon = oh.comm.getCurrentHackathon();

    function bindAwardList() {
        var list = $('#awardlist');
        oh.api.admin.hackathon.award.list.get({
            header: {hackathon_name: currentHackathon}
        }, function (data) {
            if (!data.error) {
                hackathonID = data.id;
                hackathonName = data.name;
                list.empty().append($('#hackathon_award').tmpl(data || [], {
                    substring: function (str, length) {
                        return oh.comm.stripTags(str, length);
                    }
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
            award_url:$('#award_url').val(),
            description: $('#description').val()
        }
        return formData;
    }

    function setFormData(data) {
        $('#awardform').data({id: data.id});
        $('#name').val(data.name);
        $('#level').val(data.level);
        $('#award_url').val(data.award_url);
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
        form.data('bootstrapValidator').resetForm(true);
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