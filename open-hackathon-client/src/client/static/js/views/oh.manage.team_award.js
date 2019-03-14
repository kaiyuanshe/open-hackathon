/*
 * This file is covered by the LICENSING file in the root of this project.
 */

(function ($, oh) {
    var team_id = 0;

    var currentHackathon = oh.comm.getCurrentHackathon();

    function bindScoreList() {
        var list = $('#scorelist');
        oh.api.admin.team.score.list.get({
            query: {team_id: team_id},
            header: {hackathon_name: currentHackathon}
        }, function (data) {
            if (!data.error) {
                list.empty().append($('#team_score_tmpl').tmpl(data.all));
            }
        });
    }

    function bindAwardList(){
        var awardlist = $("#awardlist")
        oh.api.admin.team.award.get({
            query: {team_id: team_id}
        }, function(data){
            if(!data.error) {
                awardlist.empty().append($('#team_award_tmpl').tmpl(data));
            }
        })
    }


    function bindHackathonAward() {
        $.template('award_option', '<option value="${id}"> ${name} </option>');
        oh.api.admin.hackathon.award.list.get({
            header: {hackathon_name: currentHackathon}
        }, function (data) {
            $('#award').append($.tmpl('award_option', data));
            oh.api.admin.team.award.get({query: {team_id: team_id}}).then(function (data) {
                if (data.length > 0) {
                    $('#award').val(data[0].award_id);
                }
                oh.comm.removeLoading();
            });
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

    function postAward(data) {
        return oh.api.admin.team.award.post({
            body: data,
            header: {hackathon_name: currentHackathon}
        })
    }

    function resetForm() {
        $("#reason").val("")
    }

    function init() {
        team_id = $('[data-team]').data('team');

        var awardform = $('#awardform');
        awardform.bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var award_id = $('#award').val();
                var reason = $('#reason').val()
                postAward({
                    team_id: team_id,
                    award_id: award_id,
                    reason: reason
                }).then(function (data) {
                        if (data.error) {
                            oh.comm.alert('错误', data.error.friendly_message);
                        } else {
                            oh.comm.alert('提示', '设置成功！');
                            toggleTable()
                            resetForm()
                            bindAwardList()
                        }
                        awardform.find('button').removeAttr('disabled')

                    })
            });

        bindHackathonAward();
        bindScoreList();
        bindAwardList();

        $('#awardtable').on('click', '[data-type="edit"]', function (e) {
            editLi = $(this).parents('tr')
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
            oh.api.admin.team.award.delete({query: {id: id}, header: {hackathon_name: currentHackathon}}).then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    editLi.detach();
                }
            });

        });
    }

    $(function () {
        init();
    })
})(window.jQuery, window.oh);