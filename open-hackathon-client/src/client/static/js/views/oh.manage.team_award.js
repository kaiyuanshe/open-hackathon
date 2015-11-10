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
    var team_id = 0;

    var currentHackathon = oh.comm.getCurrentHackathon();

    function bindScoreList() {
        var list = $('#scorelist');
        oh.api.admin.team.score.list.get({
            query: {team_id: team_id},
            header: {hackathon_name: currentHackathon}
        }, function (data) {
            if (!data.error) {
                list.empty().append($('#team_award').tmpl(data.all));
            }
        });
    }

    function postAward(data) {
        return oh.api.admin.team.award.post({
            body: data,
            header: {hackathon_name: currentHackathon}
        })
    }

    function deleteAward(data) {
        return oh.api.admin.team.award.delete({query: {id: data}});
    }


    function init() {
        team_id = $('[data-team]').data('team');
        var awardform = $('#awardform');
        awardform.bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var award_id = $('#award').val();
                (award_id == '0' ? deleteAward(team_id) : postAward({
                    team_id: team_id,
                    award_id: award_id
                })).then(function (data) {
                        if (data.error) {
                            oh.comm.alert('错误', data.error.friendly_message);
                        } else {
                            oh.comm.alert('提示', '保存成功！');
                        }
                        awardform.find('button').removeAttr('disabled')
                    })
            });

        bindAward();
        bindScoreList();

    }

    function bindAward() {
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

    $(function () {
        init();
    })
})(window.jQuery, window.oh);