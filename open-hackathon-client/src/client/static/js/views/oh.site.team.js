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

    function pageload() {
        GetHackathonTeams().then(function (data) {
            if (data.error) {

            } else {

            }
        });
    }

    function getFormDate() {
        var form = $('#createteam');
        var data = {};
        form.find('input,select,textarea').each(function (i, elm) {
            var input = $(elm);
            data[input.attr('name')] = input.val();
        });
        return data;
    }

    function CreateTeam(data) {
        return oh.api.team.post({
            body: data,
            header: {
                hackathon_name: hackathon_name
            }
        });
    }

    function GetHackathonTeams() {
        return oh.api.team.member.list.get({
            header: {
                hackathon_name: hackathon_name
            }
        });
    }

    function JoinHackathonTeam(team_name) {
        return oh.api.team.member.post({
            body: {
                team_name: team_name
            },
            header: {
                hackathon_name: hackathon_name
            }
        });
    }

    function bindEvent() {
        $('#createteam').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var data = getFormDate();
                CreateTeam(data).then(function (data) {
                    if (data.error) {
                        oh.comm.alert('´íÎó',data.friendly_message);
                    } else {
                        window.location.href = '/site/' + hackathon_name+'/settings';
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