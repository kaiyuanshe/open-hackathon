/*
 * Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
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

(function($, oh) {
    var currentHackathon = oh.comm.getCurrentHackathon();

    function toggleTable(status){
        if(status == 0){
            $('#hackathon_notice_list_table').show();
            $('#hackathon_notice_add_table').hide();
        }else{
            $('#hackathon_notice_list_table').hide();
            $('#hackathon_notice_add_table').show();
        }
    }

    // call api to get hackathon notices
    function getHackathonNotices(){
        oh.api.hackathon.notice.list.get({
            query: {
                hackathon_name: currentHackathon,
                order_by: 'time'
            }
        }, function(data) {
            if(data.error){
                oh.comm.alert(data.error.message);
            }else{
                var noticeDescriptionByCategory = {
                    0: '黑客松信息',
                    1: '用户信息',
                    2: '实验信息',
                    3: '获奖信息',
                    4: '模板信息'
                };

                $('#hackathon_notice_list').empty().append($('#hackathon_notice_list_template').tmpl(data.items, {
                    getNoticeDescription: function(category){
                        return noticeDescriptionByCategory[category];
                    }
                }));
                oh.comm.removeLoading();
            }
        });
    }

    // call api to add hackathon notice
    function addHackathonNotice(){
        data = {};
        data.content = $.trim($('#add_notice_content').val());
        data.link    = $.trim($('#add_notice_link').val());

        return oh.api.admin.hackathon.notice.post({
            body: data,
            header: {
                hackathon_name: currentHackathon
            }
        }, function(data) {
            if(data.error){
                oh.comm.alert(data.error.message);
            }else{
                toggleTable(0);
                oh.comm.alert('提示', '发布成功');
            }
        });
    }

    // call api to update hackathon notice 
    function updateHackathonNotice(itemData){
        return oh.api.admin.hackathon.notice.put({
            body: itemData,
            header: {
                hackathon_name: currentHackathon
            }
        }, function(data) {
            if(data.error){
                oh.comm.alert(data.error.message);
            }else{
                oh.comm.alert('提示', '更新成功');
            }
        });
    }

    // call api to delete hackathon notice
    function deleteHackathonNotice(id){
        return oh.api.admin.hackathon.notice.delete({
            query: {id: id},
            header: {
                hackathon_name: currentHackathon
            }
        }, function(data) {
            if(data.error){
                oh.comm.alert(data.error.message);
            }else{
                oh.comm.alert('提示', '删除成功');
            }
        });
    }

    function setUpdateHackathonNotice(data) {
        data.content = $.trim($('#update_notice_content').val());
        data.link    = $.trim($('#update_notice_link').val());
    }

    function init(){
        getHackathonNotices();
        toggleTable(0);
        $('#hackathon_notice_update_form').bootstrapValidator().on('success.form.bv', function (e) {
            e.preventDefault();
            var data = updateHackathonNoticeModal.data('list').data('tmplItem').data;
            setUpdateHackathonNotice(data);
            updateHackathonNotice(data).then(function(){
                getHackathonNotices();
            });

            updateHackathonNoticeModal.modal('hide');
        });

        $('#hackathon_notice_add_form').bootstrapValidator().on('success.form.bv', function (e) {
            e.preventDefault();
            addHackathonNotice().then(function(){
                getHackathonNotices();
            });
        });

        $('[data-type="new"]').click(function(e){
            toggleTable(1);
            $('#hackathon_notice_add_form').data().bootstrapValidator.resetForm();
        });

        $('[data-type="cancel"]').click(function(e){
            toggleTable(0);
        });

        var deleteHackathonNoticeModal = $('#hackathon_notice_delete_modal').on('show.bs.modal',function(e){
            deleteHackathonNoticeModal.data({list: $(e.relatedTarget).parents('tr') });

        }).on('click','[data-type="ok"]',function(e){
            var data = deleteHackathonNoticeModal.data('list').data('tmplItem').data;
            deleteHackathonNotice(data.id).then(function(){
                getHackathonNotices();
            });

            deleteHackathonNoticeModal.modal('hide');
        });

        var updateHackathonNoticeModal = $('#hackathon_notice_update_modal').on('show.bs.modal',function(e){
            updateHackathonNoticeModal.data({list: $(e.relatedTarget).parents('tr') });
            var data = updateHackathonNoticeModal.data('list').data('tmplItem').data;
            $('#update_notice_content').val(data.content);
            $('#update_notice_link').val(data.link);

        });

    }

    $(function() {
        init();
    });

})(jQuery, window.oh);
