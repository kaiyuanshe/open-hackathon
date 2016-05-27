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
    var hackathon_detail = {};
    var tid = 0;
    var lid = 0;
    var uid = 0;
    var team_date = {};

    var templates = {
        video: '<div class="sub-item">{{html uri}}</div>',
        img: ' <div  class="sub-item"><a href="${uri}" title="${description}" data-parent><img src="${uri}" onload="oh.comm.imgLoad(this)" alt="${description}"></a>{{if $item.isEdit()}}<a title="删除" class="edit" data-role="work-del" href="javascrpit:;"><i class="fa fa-times"></i></a>{{/if}}</div>',
        doc: '<div class="sub-item"><iframe src="${uri}" seamless="seamless" frameborder="0" scrolling="yes"></iframe>{{if $item.isEdit()}}<a title="删除" class="edit" data-role="work-del" href="javascrpit:;"><i class="fa fa-times"></i></a>{{/if}}</div>',
        pdf: '<div class="sub-item"><object data="${uri}" type="application/pdf" width="100%" height="470px"><p>您的浏览器不支持PDF查看。请安装PDF阅读器插件!</p></object>{{if $item.isEdit()}}<a title="删除" class="edit" data-role="work-del" href="javascrpit:;"><i class="fa fa-times"></i></a>{{/if}}</div>',
        code: '<div class="sub-item"><span>${description}：</span><a href="${uri}" target="_blank">${uri}</a>{{if $item.isEdit()}}<a title="删除" class="edit" data-role="work-del" href="javascrpit:;"><i class="fa fa-times"></i></a>{{/if}}</div>',
        other: '<div class="sub-item"><span>${description}：</span><a href="${uri}" target="_blank">${uri}</a>{{if $item.isEdit()}}<a title="删除" class="edit" data-role="work-del" href="javascrpit:;"><i class="fa fa-times"></i></a>{{/if}}</div>'
    };

    function office_app(team_show) {
        if (team_show.type == 3 || team_show.type == 4 || team_show.type == 5) {
            team_show.uri = "https://view.officeapps.live.com/op/embed.aspx?src=" + encodeURIComponent(team_show.uri)
        }
        return team_show
    }

    function splitShow(data) {
        var _data = {video: [], img: [], code: [], doc: [], pdf: [], other: []};
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
                case 6:
                    _data.pdf.push(o)
                    break;
                case 3:
                case 4:
                case 5:
                    _data.doc.push(office_app(o))
                    break;
                default:
                    _data.other.push(o)
                    break;
            }
        });
        return _data;
    }

    function showMember() {
        getMemberList().then(function (data) {
            $('#team_member h2 span').text('(' + data.length + ')');
            $('#talent_list').empty().append($('#team_item').tmpl(data, {
                getTitle: function (id, status) {
                    if (id == lid) {
                        return '队长';
                    } else if (status != 1) {
                        return '等待加入';
                    }
                    return '成员';
                },
                isNotLeader: function (id) {
                    return id != lid;
                },
                getUserLogo: function (logo) {
                    return (logo == null || logo.length == 0) ? '/static/pic/anon_user.png' : logo;
                }
            }));
        });
    }

    function isEdit() {
        return value;
    }

    function bindShow(data, isedit) {
        if (!(data.img.length == 0 && data.video.length == 0 && data.code.length == 0 && data.doc.length == 0 &&
              data.pdf.length == 0 && data.other.length == 0))
            $('#no_show').hide();

        if (data.video.length > 0) {
            $('#videos').show();
            $('#videos .nothing').addClass('hide');
            $.tmpl(templates.video, data.video, {
                isEdit: function () {
                    return isedit;
                }
            }).appendTo('#videos .w-videos');
        } else {
            if(!isedit)
                $('#videos').hide();
            if ($('#videos .w-videos>.sub-item').length == 0) {
                $('#videos .nothing').removeClass('hide');
            }
        }
        if (data.img.length > 0) {
            $('#images').show();
            $('#images .nothing').addClass('hide');
            $.tmpl(templates.img, data.img, {
                isEdit: function () {
                    return isedit;
                }
            }).appendTo('#work_images');
        } else {
            if(!isedit)
                $('#images').hide();
            if ($('#work_images>.sub-item').length == 0) {
                $('#images .nothing').removeClass('hide');
            }
        }
        if (data.doc.length == 0 && data.pdf.length == 0) {
            if(!isedit)
                $('#docs').hide();
            if ($('#docs .w-doc>.sub-item').length == 0) {
                $('#docs .nothing').removeClass('hide');
            }
        } else {
            $('#docs').show();
            $('#docs .nothing').addClass('hide');
            $.tmpl(templates.pdf, data.pdf, {
                isEdit: function () {
                    return isedit;
                }
            }).appendTo('#docs .w-doc');
            $.tmpl(templates.doc, data.doc, {
                isEdit: function () {
                    return isedit;
                }
            }).appendTo('#docs .w-doc');
        }

        if (data.code.length > 0) {
            $('#code').removeClass('hide');
            $.tmpl(templates.code, data.code, {
                isEdit: function () {
                    return isedit;
                }
            }).appendTo('#code .w-code');
        } else {
            if ($('#code .w-code>.sub-item').length == 0) {
                $('#code').addClass('hide');
            }
        }

        if (data.other.length > 0) {
            $('#other').removeClass('hide');
            $.tmpl(templates.other, data.other, {
                isEdit: function () {
                    return isedit;
                }
            }).appendTo('#other .w-other');
        } else {
            if ($('#other .w-other>.sub-item').length == 0) {
                $('#other').addClass('hide');
            }
        }
    }

    function pageload() {
        getHackathonDetail().then(function(data){
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                hackathon_detail = data;
            }
        });

        $('[data-loadsrc]').each(function (i, img) {
            var $img = $(img).load(function (e) {
                oh.comm.imgLoad(this);
            })
            $img.attr({src: $img.attr('data-loadsrc')});
        });

        $('.popup-gallery').magnificPopup({
            delegate: 'a[data-parent]',
            type: 'image',
            tLoading: '加载图片 #%curr%...',
            mainClass: 'mfp-img-mobile',
            gallery: {
                enabled: true,
                navigateByImgClick: true,
                preload: [0, 1]
            },
            image: {
                tError: '<a href="%url%">图片 #%curr%</a> 无法加载。',
                titleSrc: function (item) {
                    return item.el.attr('title');
                }
            }
        });

        tid = $('[data-tid]').data('tid');
        lid = $('[data-lid]').data('lid');
        uid = $('[data-uid]').data('uid');
        team_date.id = tid;
        showMember();

        getShow().then(function (data) {
            if (!data.error) {
                $("#show_count").val("（" + data.length + "）")
                var split_data = splitShow(data);
                bindShow(split_data, false);
            } else {
            }
        });


        if (uid !== '') {
            getScore().then(function (data) {
                if (data.my) {
                    $('#score_form').detach();
                    $('#score_list').append($('#score_item').tmpl(data.all)).parent().addClass('active');
                } else {
                    $('#score_form').removeClass('hide');
                }
            });
        }

        // edit team logo by input image address
        var editLogo_form = $('#editLogoForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                disableItems(['#team_logo_input', '#team_logo_upload_btn', '#team_logo_submit', '#team_logo_cancel']);
                var logo_url = editLogo_form.find('#team_logo_input').val();
                updateTeamLogo(logo_url);
            });

        var projectCover_Form = $('#projectCoverForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                disableItems(['#project_cover_input', '#project_cover_upload_btn', '#project_cover_submit',
                              '#project_cover_cancel']);
                var url = projectCover_Form.find('[name="cover"]').val();
                updateProjectCover(url)
            });

        // edit dev_plan by input resource address
        var projectPlan_Form = $('#projectPlanForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                $('#dev_plan_submit').text('感谢提交开发计划书，正在邮件通知中。。。稍等将自动跳转');
                disableItems(['#dev_plan_input', '#dev_plan_btn', '#dev_plan_submit', '#dev_plan_cancel']);
                var url = projectPlan_Form.find('[name="plan"]').val();
                updateTeamDevPlan(url);
            });
        var src = $('#plan').data('src');
        if (src) {
            $('#plan').attr({src: 'https://view.officeapps.live.com/op/embed.aspx?src=' + encodeURIComponent(src)}).removeClass('hide');
        }

        $('#score_form').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                var data = {
                    id: $('#score_form').data('score_id') || 0,
                    team_id: tid,
                    score: parseInt($('input:radio[name="trophies-rating"]:checked').val()),
                    reason: $('#comment').val()
                };

                (data.id == 0 ? submitScore(data) : updateScore(data)).then(function (data) {
                    if (data.error) {
                        oh.comm.alert('错误', data.error.friendly_message);
                    } else {
                        oh.comm.alert('提示', '评分成功');
                        $('#score_form').detach();
                        $('#score_list').append($('#score_item').tmpl(data.all)).parent().addClass('active');

                    }
                })
            });

        var worksForm = $('#addWorksForm').bootstrapValidator()
            .on('success.form.bv', function (e) {
                e.preventDefault();
                disableItems(['#dev_plan_input', '#dev_plan_btn', '#dev_plan_submit', '#dev_plan_cancel',
                              '#team_work_description']);
                var uri = worksForm.find('[data-gtype].active [data-name="uri"]').val()
                addTeamWork(uri)
            });


        var worktype = $('#worktype').change(function (e) {
            var type = parseInt(worktype.val());
            var gtypename = 'image';
            $('#team_work_upload').show();
            switch (type) {
                case 0:
                    gtypename = 'image';
                    break;
                case 1:
                    gtypename = 'video';
                    $('#team_work_upload').hide();
                    break;
                case 2:
                    gtypename = 'code';
                    $('#team_work_upload').hide();
                    break
                case 3:
                case 4:
                case 5:
                case 6:
                    gtypename = 'doc';
                    break
                case 99:
                    gtypename = 'other';
                    $('#team_work_upload').hide();
                    break;
            }
            worksForm.find('[data-gtype]').removeClass('active');
            worksForm.find('[data-gtype="' + gtypename + '"]').addClass('active');
            worksForm.data().bootstrapValidator.resetForm();
        });

        var works_Modal = $('#works_Modal')
            .on('hide.bs.modal', function (e) {
                $('#addWorksForm').get(0).reset();
                worksForm.data().bootstrapValidator.resetForm();
            });
    }

    function getHackathonDetail() {
        return oh.api.hackathon.get({header: {hackathon_name: hackathon_name}});
    }

    function getMemberList() {
        return oh.api.team.member.list.get({query: {team_id: tid}, header: {hackathon_name: hackathon_name}});
    }

    function joinTeam(data) {
        return oh.api.team.member.post({body: {team_id: tid}, header: {hackathon_name: hackathon_name}});
    }

    function leaveTeam(user_id) {
        return oh.api.team.member.delete({
            query: {user_id: user_id, team_id: tid},
            header: {hackathon_name: hackathon_name}
        });
    }

    function updateMemberStatus(rel_id, status) {
        var data = {
            user_id: rel_id,
            team_id: tid,
            status: status
        };
        return oh.api.team.member.put({body: data, header: {hackathon_name: hackathon_name}});
    }

    function deniedMember(rel_id) {
        return leaveTeam(rel_id);
    }

    function approvedMember(rel_id) {
        return updateMemberStatus(rel_id, 1);
    }

    function updateTeam(data) {
        return oh.api.team.put({body: data, header: {hackathon_name: hackathon_name}});
    }

    // upload any type of team files
    function uploadTeamFile(filter_str, start_func, update_func) {
        // upload file about team
        $(filter_str).fileupload({
            type: 'POST',
            url: CONFIG.apiconfig.proxy + '/api/user/file?file_type=team_file',
            dataType: 'json',
            beforeSend: function (xhr, data) {
                xhr.setRequestHeader('token', $.cookie('token'));
            },
            start: start_func,
            done: function (e, obj) {
                var data = obj.result;
                if (data.error || ! "files" in data || data.files.length == 0) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    var url = data.files[0].url;
                    update_func(url);
                }
            }
        });
    }

    function disableItems(list) {
        for (var index in list)
            $(list[index]).attr('disabled', true);
    }

    function enableItems(list) {
        for (var index in list)
            $(list[index]).removeAttr('disabled');
    }

    // modify the team logo
    function updateTeamLogo(url) {
        updateTeam({id: tid, logo: url}).then(function (data) {
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                $('#team_logo').attr({src: url});
                $('#editLogoForm').find('#team_logo_input').val("");
                $('#teamLogoModal').modal('hide');
                $('#team_logo_upload_span').text('上传文件');
                enableItems(['#team_logo_input', '#team_logo_upload_btn', '#team_logo_submit', '#team_logo_cancel']);
                oh.comm.alert("提示", "设置成功!");
            }
        });
    }

    // update the project cover
    function updateProjectCover(url) {
        updateTeam({id: tid, cover: url}).then(function (data) {
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                var c = $('#cover');
                var par = c.find('[data-parent]');
                var nothing = c.find('.nothing');
                if (par.length == 0) {
                    par = $('<div data-parent>').append($('<img>').load(function (e) {
                              oh.comm.imgLoad(this);
                          })).appendTo(c);
                }
                par.find('img').attr({src: url});
                nothing.addClass('hide');

                $('#projectCoverModal').modal('hide');
                $('#projectCoverForm').find('#project_cover_input').val("");
                $('#project_cover_upload_span').text('上传文件');
                enableItems(['#project_cover_input', '#project_cover_upload_btn', '#project_cover_submit',
                             '#project_cover_cancel']);
                oh.comm.alert("提示", "设置成功!");
            }
        });
    }

    // update the team dev_plan to this url
    function updateTeamDevPlan(url) {
        updateTeam({id: tid, dev_plan: url}).then(function (data) {
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                $('#projectPlanModal').modal('hide');
                $('#dev_plan_span').text('上传文件');
                $('#dev_plan_submit').text('确定');
                enableItems(['#dev_plan_input', '#dev_plan_btn', '#dev_plan_submit', '#dev_plan_cancel']);
                var p = $('#plan');
                p.attr({src: 'https://view.officeapps.live.com/op/embed.aspx?src=' +
                        encodeURIComponent(url)}).removeClass('hide');
                oh.comm.alert("提示", "设置成功!");
            }
        });
    }

    // add new team works
    function addTeamWork(uri) {
        var data = {
            team_id: tid,
            type: +$('#addWorksForm').find('#worktype').val(),
            note: $('#addWorksForm').find('[name="note"]').val(),
            uri: uri
        };
        addShow(data).then(function (data) {
            if (data.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                bindShow(splitShow([data]), true);
                $('#works_Modal').modal('hide');
                $('#addWorksForm').data().bootstrapValidator.resetForm();
                $('#worktype').trigger('change');

                $('#team_work_upload_span').text('上传文件');
                enableItems(['[data-name="uri"]', '#team_work_upload_btn', '#team_work_submit', '#team_work_cancel',
                             '#team_work_description']);
                oh.comm.alert("提示", "设置成功!");
            }
        });
    }

    function addShow(data) {
        return oh.api.team.show.post({body: data, header: {hackathon_name: hackathon_name}});
    }

    function deleteShow(data) {
        return oh.api.team.show.delete({query: data, header: {hackathon_name: hackathon_name}});
    }

    function getShow() {
        return oh.api.team.show.get({query: {team_id: tid}, header: {hackathon_name: hackathon_name}});
    }

    function getScore() {
        return oh.api.team.score.get({query: {team_id: tid}, header: {hackathon_name: hackathon_name}});
    }

    function submitScore(data) {
        return oh.api.team.score.post({body: data, header: {hackathon_name: hackathon_name}});
    }

    function updateScore(data) {
        return oh.api.team.score.pus({body: data, header: {hackathon_name: hackathon_name}});
    }

    function bindEvent() {
        $('.oh-team-edit').on('click', '[data-role="leave"]', function (e) {
            oh.comm.confirm('提示', '确定离队吗？', function () {
                leaveTeam(uid).then(function (data) {
                    if (data.error) {
                        oh.comm.alert('错误', data.error.friendly_message);
                    } else {
                        window.location.reload();
                    }
                });
            });
        });

        var addWork = $('[data-role="addworks"]').click(function (e) {
            $('#works_Modal').modal('show');
        });


        $('[data-role="join"]').click(function (e) {
            joinTeam().then(function (data) {
                if (data.error) {
                    if (data.error.code == 412) {
                        oh.comm.alert('错误', '请报名后才能加入该团队！');
                    } else {
                        oh.comm.alert('错误', data.error.friendly_message);
                    }
                } else {
                    showMember();
                    $('.oh-team-edit').empty().append('<a href="javascript:void(0);" class="btn btn-danger btn-sm" data-role="leave" ><i class="fa fa-unlink"></i> 离队</a>');
                }
            });
        });

        var edit_btn = $('[data-role="edit"]').click(function (e) {
            edit_btn.addClass('hide');
            seva_btn.removeClass('hide');
            addWork.removeClass('hide');
            var input_name = $('<input>').attr({
                type: 'text',
                placeholder: '团队名称',
                value: $.trim($('#team_name').text())
            });
            var input_des = $('<textarea>').attr({
                row: '4',
                placeholder: '团队简介'
            }).val($.trim($('#team_description').text()));

            var pro_name = $('<input>').attr({
                type: 'text',
                placeholder: '项目名称',
                value: $.trim($('#pro_name').text())
            });

            var pro_desc = $('<textarea>').attr({
                row: '4',
                placeholder: '项目简介'
            }).val($.trim($('#pro_desc').text()));

            $('#pro_name').addClass('edit').empty().append(pro_name);
            $('#pro_desc').addClass('edit').empty().append(pro_desc);
            $('#team_name').addClass('edit').empty().append(input_name);
            $('#team_description').addClass('edit').empty().append(input_des);
            $('#cover').addClass('edit').prepend($('<a>').attr({'data-role': 'cover'}).text('编辑展示图'));

            var dev_plan_template_url = "config" in hackathon_detail && "dev_plan_template_url" in hackathon_detail["config"] && hackathon_detail["config"]["dev_plan_template_url"] ?
                                        hackathon_detail["config"]["dev_plan_template_url"] :
                                        'http://opentech0storage.blob.core.chinacloudapi.cn/ohp/%E4%BA%91%E4%B8%AD%E9%BB%91%E5%AE%A2%E6%9D%BE%E5%BC%80%E5%8F%91%E8%AE%A1%E5%88%92%E4%B9%A6%E6%A8%A1%E6%9D%BF.pptx'
            $('#plan').before($('<a>').attr({'data-role': 'plan', 'class': 'btn btn-sm btn-info'}).text('添加开发计划书'),
                $('<a id="down_plan"><i class="fa fa-download"></i></a>')
                    .attr({class:'link',href: dev_plan_template_url})
                    .append('下载开发计划书模板'));

            $('#show_works .sub-item').each(function (i, item) {
                $(item).append($('<a>').attr({
                    title: '删除',
                    class: 'edit',
                    'data-role': 'work-del',
                    href: 'javascrpit:;'
                }).html('<i class="fa fa-times"></i>'))
            })
        });
        if (edit_btn.length > 0) {
            $('#show_works').on('click', 'a[data-role="work-del"]', function (e) {
                var item = $(this).parent();
                var id = item.data('tmplItem').data.id
                deleteShow({team_id: tid, id: id}).then(function (data) {
                    if (data.error) {
                        oh.comm.alert('错误', data.error.friendly_message);
                    } else {
                        var sublist = item.parent();
                        item.detach();
                        if (sublist.find('.sub-item').length == 0) {
                            sublist.find('.nothing').removeClass('hide');
                        }
                    }
                });
            });
        }

        $('.team-header').on('click', 'a[data-role]', function (e) {
            var role = $(this).data('role');
            switch (role) {
                case 'cover':
                    $('#projectCoverModal').modal('show');
                    return;
                case 'plan':
                    $('#projectPlanModal').modal('show');
                    return;
            }
        });

        var seva_btn = $('[data-role="save"]').click(function (e) {
            seva_btn.addClass('hide');
            edit_btn.removeClass('hide');
            addWork.addClass('hide');
            $('.team-pic').removeClass('edit').find('inner-edit').detach();
            team_date.name = $('#team_name').removeClass('edit').find('input').val();
            team_date.description = $('#team_description').removeClass('edit').find('textarea').val();
            team_date.project_name = $('#pro_name').removeClass('edit').find('input').val();
            team_date.project_description = $('#pro_desc').removeClass('edit').find('textarea').val();
            $('[data-role="team_name"]').text(team_date.name);
            $('#team_name').empty().text(team_date.name);
            $('#pro_name').empty().text(team_date.project_name);
            $('#pro_desc').empty().text(team_date.project_description);
            $('#cover').removeClass('edit').find('a').detach();
            $('a[data-role="plan"],#down_plan').detach();
            $('#team_description').empty().text(team_date.description);
            $('#show_works a.edit').detach();
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
            var rel_id = $(this).data('id');
            var userItem = $(this).parents('[data-user]');
            deniedMember(rel_id).then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    userItem.detach();
                    $('#team_member h2 span').text('(' + $('#talent_list>[data-user]').length + ')');
                }
            });
        }).on('click', '[data-role="approved"]', function (e) {
            var btn = $(this);
            var rel_id = btn.data('id');
            var userItem = btn.parents('[data-user]');
            approvedMember(rel_id).then(function (data) {
                if (data.error) {
                    oh.comm.alert('错误', data.error.friendly_message);
                } else {
                    btn.detach();
                    userItem.find('span').text('成员')
                }
            });
        });

        // upload file about team_logo
        uploadTeamFile('#team_logo_upload', function(){
            $('#team_logo_upload_span').text('文件上传中，上传成功将会自动跳转，请稍等...');
            disableItems(['#team_logo_input', '#team_logo_upload_btn', '#team_logo_submit', '#team_logo_cancel']);
        }, updateTeamLogo)

        // upload file about project_cover
        uploadTeamFile('#project_cover_upload', function(){
            $('#project_cover_upload_span').text('文件上传中，上传成功将会自动跳转，请稍等...');
            disableItems(['#project_cover_input', '#project_cover_upload_btn', '#project_cover_submit',
                          '#project_cover_cancel']);
        }, updateProjectCover)

        // upload file about dev_plan
        uploadTeamFile('#dev_plan_upload', function(){
            $('#dev_plan_span').text('文件上传中，上传成功将会自动跳转，请稍等...');
            disableItems(['#dev_plan_input', '#dev_plan_btn', '#dev_plan_submit', '#dev_plan_cancel']);
        }, updateTeamDevPlan)

        // upload file about team_work
        uploadTeamFile('#team_work_upload', function(){
            $('#team_work_upload_span').text('文件上传中，上传成功将会自动跳转，请稍等...');
            disableItems(['[data-name="uri"]', '#team_work_upload_btn', '#team_work_submit', '#team_work_cancel',
                          '#team_work_description']);
        }, addTeamWork)
    }

    function init() {
        bindEvent();
        pageload();
    };

    $(function () {
        init();
    });

})(window.jQuery, window.oh);