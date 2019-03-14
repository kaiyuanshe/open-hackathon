/*
 * This file is covered by the LICENSING file in the root of this project.
 */

;
(function ($, oh) {
    var currentHackathon = oh.comm.getCurrentHackathon();

    function pageLoad() {
        var list = $('#registe_list');
        oh.api.admin.registration.list.get({
            header: {
                hackathon_name: currentHackathon
            }
        }, function (data) {
            list.empty().append($('#register_list_template').tmpl(data));
            list.find('.editable').editable({
                url: function (params) {
                    var id = $(this).parents('tr').data('tmplItem').data.id;
                    var d = new $.Deferred;
                    oh.api.admin.registration.put({
                        body: {
                            id: id,
                            status: Number(params.value)
                        },
                        header: {
                            hackathon_name: currentHackathon
                        }
                    }, function (data) {
                        if (data.error) {
                            d.reject(data.error.friendly_message)
                        } else {
                            d.resolve();
                        }
                    });
                    return d.promise();
                }
            });
        });

    }

    function deleteuRegister(data) {
        return oh.api.admin.registration.delete(data);
    }

    function init() {
        pageLoad();
        var confirmModal = $('#confirm_modal').on('show.bs.modal', function (e) {
            console.log(e);
            editLi = $(e.relatedTarget).parents('tr');
        }).on('click', '[data-type="ok"]', function (e) {
            var id = editLi.data('tmplItem').data.id;
            confirmModal.modal('hide');
            deleteuRegister({query: {id: id}, header: {hackathon_name: currentHackathon}}).then(function (data) {
                if (data.error) {
                    oh.comm.alert('delete registered user fail: ', data.error.friendly_message);
                } else {
                    editLi.detach();
                }
            });
        });
    }

    $(function () {
        init();
    });
})(jQuery, window.oh);
