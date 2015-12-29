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
        //status 0:show all admin users, 1:show search bar, 2:show search results
        if(status == 0){
            $('#hackathon_notice_list_table').show();
            $('#hackathon_notice_add_table').hide();
        }else{
            $('#hackathon_notice_list_table').hide();
            $('#hackathon_notice_add_table').show();
        }
    }

    // initial table to show admin list
    function pageLoad(){
        var list = $('#hackathon_notice_list');

        var ALL_HACKATHON_NOTICE = 2;
        oh.api.admin.hackathon.notice.get({
            header: {
                hackathon_name: currentHackathon
            },
            query: {
                type: ALL_HACKATHON_NOTICE
            }
        }, function(data) {
            for(var i = 0; i < data.length; ++i) {
                if(data[i].type == '0') data[i].type = '在首页显示';
                else                    data[i].type = '在活动页显示';
            }
            list.empty().append($('#hackathon_notice_list_template').tmpl(data, {}));
            oh.comm.removeLoading();
        });
    }

    function clearNoticeVal() {
        $('#add_notice_content').val('');
        $('#add_notice_link').val('');
    }

    // call api to add hackathon notice
    function addHackathonNotice(){
        data = {};
        data.content = $.trim($('#add_notice_content').val());
        data.link    = $.trim($('#add_notice_link').val());
        data.type    = $.trim($('input[name="add_notice_type"]:checked').val());

        return oh.api.admin.hackathon.notice.post({
            body: data,
            header: {
                hackathon_name: currentHackathon
            }
        }, function(data) {
            if(data.error){
                alert(data.error.message);
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
                alert(data.error.message)
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
                alert(data.error.message)
            }else{
                oh.comm.alert('提示', '删除成功');
            }
        });
    }

    function getHackathonNoticeUpdate(data) {
        data.content = $.trim($('#update_notice_content').val());
        data.link    = $.trim($('#update_notice_link').val());
        data.type    = $.trim($('input[name="update_notice_type"]:checked').val());
    }

    function init(){
        pageLoad();
        toggleTable(0);
        $('#hackathon_notice_update_form').bootstrapValidator({
            submitButtons: 'button[data-type="submit"]'
        });

        $('#hackathon_notice_add_form').bootstrapValidator().on('success.form.bv', function (e) {
            e.preventDefault();
            addHackathonNotice().then(function(){
                pageLoad();
            });
        });

        $('[data-type="new"]').click(function(e){
            clearNoticeVal();
            toggleTable(1);
        });

        $('[data-type="cancel"]').click(function(e){
            toggleTable(0);
        });

        var deleteHackathonNoticeModal = $('#hackathon_notice_delete_modal').on('show.bs.modal',function(e){
            list = $(e.relatedTarget).parents('tr');
        }).on('click','[data-type="ok"]',function(e){
            var data = list.data('tmplItem').data;
            deleteHackathonNotice(data.id).then(function(){
                pageLoad();
            });

            deleteHackathonNoticeModal.modal('hide');
        });

        var updateHackathonNoticeModal = $('#hackathon_notice_update_modal').on('show.bs.modal',function(e){
            list = $(e.relatedTarget).parents('tr');
            var data = list.data('tmplItem').data;
            $('#update_notice_content').val(data.content);
            $('#update_notice_link').val(data.link);

            if(data.type == '0') {
                $('#update_notice_type_0').prop("checked", true);
            }
            else {
                $('#update_notice_type_1').prop("checked", true);
            }
            
        }).on('click','[data-type="submit"]',function(e){
            var data = list.data('tmplItem').data;
            getHackathonNoticeUpdate(data);
            updateHackathonNotice(data).then(function(){
                pageLoad();
            });

            updateHackathonNoticeModal.modal('hide');
        });

    }

    $(function() {
        init();
    });

})(jQuery, window.oh);