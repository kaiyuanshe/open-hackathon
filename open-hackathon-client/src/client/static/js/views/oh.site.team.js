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
    'use strict';

    var hackathon_name = oh.comm.getCurrentHackathon();
    var tid = 0;
    var lid = 0;
    var team_date = {};


    function splitShow(data) {
        var _data = {video: [], img: [], code: []};
        $.each(data, function (i, o) {
            switch (o.type) {
                case 0:
                    _data.img.push(o);
                    break;
                case 1:
                    _data.video.push(o);
                    break;
                case 2:
                    _data.code.push(o);
                    break;
            }
        });
        return _data;
    }

    function pageload() {
        tid = $('[data-tid]').data('tid');
        lid = $('[data-tid]').data('lid');
        team_date.id = tid;
        getMemberList().then(function (data) {
            $('#talent_list').append($('#team_item').tmpl(data, {
                getTitle: function (id, status) {
                    if (id == lid) {
                        return '队长';
                    } else if (status != 1) {
                        return '等待加入';
                    }
                    return '成员';
                },
                getUserLogo: function (logo) {
                    return logo.length == 0 ? '/static/pic/anon_user.png' : logo;
                }
            }));
        });

        getShow().then(function (data) {
            if (!data.error) {
                var slipt_data = splitShow(data);
                var temp = $('#show_item');
                $('#works_video').append(temp.tmpl(slipt_data.video));
                $('#works_img').append(temp.tmpl(slipt_data.img));
                $('#works_code').append(temp.tmpl(slipt_data.code));
            } else {

            }
        });

        getScore().then(function (data) {

        });

        var editLogo_form = $('#editLogoForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                team_date.logo = editLogo_form.find('#logo').val();
                $('#team_logo').attr({src: team_date.logo})
                $('#teamLogoModal').modal('hide');
            });

        $('#score_form').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var data = {
                    id: $('#score_form').data('score_id') || 0,
                    team_id: tid,
                    score: $('input:radio[name="trophies-rating"]:checked').val(),
                    reason: $('#comment').val()
                };

                (data.id == 0 ? submitScore(data) : updateScore(data)).then(function (data) {
                    if (data.error) {
                        oh.comm.alert('错误', data.error.friendly_message);
                    } else {
                        oh.comm.alert('提示', '评分成功');
                    }
                })
            });

        $('#teamLogoModal').on('hide.bs.modal', function (e) {
            editLogo_form.get(0).reset();
            editLogo_form.data().bootstrapValidator.resetForm();
        });
    }

    function getMemberList() {
        return oh.api.team.member.list.get({query: {team_id: tid}, header: {hackathon_name: hackathon_name}});
    }

    function joinTeam(data) {
        return oh.api.team.member.post({body: {team_id: tid}, header: {hackathon_name: hackathon_name}});
    }

    function updateMemberStatus(userid, status) {
        var data = {
            team_id: tid,
            user_id: userid,
            status: status
        };
        return oh.api.team.member.put({body: data, header: {hackathon_name: hackathon_name}});
    }

    function deniedMember(userid) {
        return updateMemberStatus(userid, 2);
    }

    function approvedMember(userid) {
        return updateMemberStatus(userid, 1);
    }

    function updateTeam(data) {
        return oh.api.team.put({body: data, header: {hackathon_name: hackathon_name}});
    }

    function addShow(data) {
        return oh.api.team.show.post({body: data, header: {hackathon_name: hackathon_name}});
    }

    function deleteShow(data) {
        return oh.api.team.show.delete({body: data, header: {hackathon_name: hackathon_name}});
    }

    function getShow() {
        return oh.api.team.show.get({body: {team_id: tid}, header: {hackathon_name: hackathon_name}});
    }

    function getScore() {
        return oh.api.team.score.get({body: {team_id: tid}, header: {hackathon_name: hackathon_name}});
    }

    function submitScore(data) {
        return oh.api.team.score.post({body: data, header: {hackathon_name: hackathon_name}});
    }

    function updateScore(data) {
        return oh.api.team.score.pus({body: data, header: {hackathon_name: hackathon_name}});
    }

    function bindEvent() {
        $('[data-role="leave"]').click(function (e) {

        });

        $('[data-role="join"]').click(function (e) {
            joinTeam().then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                }
            });
        });

        var edit_btn = $('[data-role="edit"]').click(function (e) {
            edit_btn.addClass('hide');
            seva_btn.removeClass('hide');
            var input_name = $('<input>').attr({type: 'text', value: $('#team_name').text()});
            var input_des = $('<textarea>').attr({row: '4'}).val( $('#team_description').text());
            $('#team_name').addClass('edit').empty().append(input_name);
            $('#team_description').addClass('edit').empty().append(input_des);
        });

        var seva_btn = $('[data-role="save"]').click(function (e) {
            seva_btn.addClass('hide');
            edit_btn.removeClass('hide');
            $('.team-pic').removeClass('edit').find('inner-edit').detach();
            team_date.name = $('#team_name').removeClass('edit').find('input').val();
            team_date.description = $('#team_description').removeClass('edit').find('textarea').val();
            $('[data-role="team_name"]').text(team_date.name);
            $('#team_name').empty().text(team_date.name);
            $('#team_description').empty().text(team_date.description);

            updateTeam(team_date).then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                }
            });
        });

        $('body').on('click', '[data-role="logo-edit"]', function (e) {
            $('#teamLogoModal').modal('show');
        });


        $('#talent_list').on('click', '[data-role="denied"]', function (e) {
            var uid = $(this).data('uid');
            var userItem = $(this).parents('[data-user]');
            deniedMember(uid).then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    userItem.detach();
                }
            });
        }).on('click', '[data-role="approved"]', function (e) {
            var uid = $(this).data('uid');
            var userItem = $(this).parents('[data-user]');
            approvedMember(uid).then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {

                }
            });
        });

    }

    function init() {
        bindEvent();
        pageload();
    };

    $(function () {
        init();
    });

})(window.jQuery, window.oh);