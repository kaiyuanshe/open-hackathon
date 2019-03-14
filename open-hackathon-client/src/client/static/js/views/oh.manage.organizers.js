/*
 * This file is covered by the LICENSING file in the root of this project.
 */

(function ($, oh) {
    var hackathonName = '',
        hackathonID = 0;

    var currentHackathon = oh.comm.getCurrentHackathon();

    function bindOrganizerList() {
        var list = $('#organizerlist');
        oh.api.admin.hackathon.get({
            header: {hackathon_name: currentHackathon}
        }, function (data) {
            if (!data.error) {
                hackathonID = data.id;
                hackathonName = data.name;
                list.empty().append($('#hackathon_organizer').tmpl(data.organizer || [], {
                    substring: function (str, length) {
                        return oh.comm.stripTags(markdown.toHTML(str), length);
                    },
                    get_organization_type: function (organization_type) {
                        switch(organization_type){
                            case 2: return "合作伙伴"; break;
                            default: return "主办方";
                        }
                    }
                }));
                oh.comm.removeLoading();
            }
        });
    }

    function toggleTable() {
        if ($('#organizertable').css('display') == 'none') {
            $('#organizertable').show();
            $('#organizerform').hide()
        } else {
            $('#organizertable').hide();
            $('#organizerform').show()
        }
    }

    function getFormData() {
        var organizationtype = $('#organization_type').val()=="主办方"? 1:2;
        var formData = {
            id: $('#organizerform').data('id') || 0,
            name: $.trim($('#name').val()),
            organization_type: organizationtype,
            description: $('#description').val(),
            homepage: $('#homepage').val(),
            logo: $('#logo').val()
        }
        return formData;
    }

    function setFormData(data) {
        $('#organizerform').data({id: data.id});
        $('#name').val(data.name);
        switch(data.organization_type){
            case 1: $('#organization_type').val("主办方"); break;
            case 2: $('#organization_type').val("合作伙伴"); break;
            default: alert("no such organization_type");
        }
        $('#description').val(data.description);
        $('#homepage').val(data.homepage);
        $('#logo').val(data.logo);
    }

    function getOrganizers() {
        var organizers = [];
        $('#organizertable tbody>tr').each(function (i, tr) {
            var data = $(tr).data('tmplItem').data;
            if (data) {
                organizers.push($(tr).data('tmplItem').data);
            }
        })
        return organizers;
    }

    function createOrganizers(data) {
        return oh.api.admin.hackathon.organizer.post(data, function (data) {
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                bindOrganizerList();
                resetForm();
            }
        });
    }

    function updateOrganizers(data) {
        return oh.api.admin.hackathon.organizer.put(data, function (data) {
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                bindOrganizerList();
                resetForm();
            }
        });
    }

    function deleteOrganizers(data){
        return oh.api.admin.hackathon.organizer.delete(data, function(data){
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                bindOrganizerList();
            }
        });
    }

    function resetForm() {
        var form = $('#organizerform');
        form.data({id: 0});
        form.data('bootstrapValidator').resetForm(true);
        $('#description').val('');
    }

    function init() {
        var organizerform = $('#organizerform');
        organizerform.bootstrapValidator().on('success.form.bv', function (e) {
            e.preventDefault();
            var itemData = getFormData();
            var data = {body: itemData, header: {hackathon_name: currentHackathon}};
            (itemData.id == 0 ? createOrganizers(data) : updateOrganizers(data)).then(function () {
                toggleTable();
            })
        });

        $('#organizertable').on('click', '[data-type="edit"]', function (e) {
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
            var data_organizer_id = editLi.data('tmplItem').data.id;
            var data = {header: {hackathon_name: currentHackathon}, query: {id: data_organizer_id}};
            deleteOrganizers(data);
            confirmModal.modal('hide');
        });

        $('#description').markdown({
            hiddenButtons: 'cmdCode',
            language: 'zh'
        });

        bindOrganizerList();
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);