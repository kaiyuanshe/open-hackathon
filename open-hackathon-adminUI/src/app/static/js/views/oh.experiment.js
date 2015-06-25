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

 ;
(function($, oh) {

//    var isupdate = false;
//
//    function toggleTable(){
//        if($('#adminlisttable').css('display') == 'none' ){
//            $('#adminlisttable').show();
//            $('#adminform').hide()
//        }else{
//            $('#adminlisttable').hide();
//            $('#adminform').show()
//        }
//    }
//
    //get form-data for submit
    function getFilterData(){
        var Data = {
            user_name:$.trim($('#expr_user_name').val()),
            status:$.trim($('#status').val())
         }
        return Data;
    }


    // initial table to show admin list
    function pageLoad(){
        var list = $('#experiment_list');
        var currentHackathon = oh.comm.getCurrentHackathon();
        var data = getFilterData()
        oh.api.admin.experiment.list.get({
            query: data
            header: {
                hackathon_name: currentHackathon.name
            }
        }, function(data) {
            list.empty().append($('#experiment_list_template').tmpl(data,{
                getStatus:function(status){
                    if(status == 0){
                        return '初始化中'
                    }
                    if(status == 1){
                        return '准备中'
                    }
                    if(status == 2){
                        return '运行中'
                    }
                    if(status == 3){
                        return '已停止'
                    }
                    if(status == 4){
                        return '已删除'
                    }
                    if(status == 5){
                        return '已失败'
                    }
                    if(status == 6){
                        return '回收中'
                    }
                    return '已回收';
                },
                getRole:function(role_type){
                    if(role_type == 2){
                        return '裁判'
                    }
                    return '管理员';
                },
                getEmails:function(emails){
                    return getPriEmail(emails);
                }
            }));
            oh.comm.removeLoading();
        });
        $('#expr_list_filter').find('[type="submit"]').removeAttr('disabled')
    }


    // call api to get experiment list by filter
    function getExprListByFilter(data){
        var currentHackathon = oh.comm.getCurrentHackathon();
        return oh.api.admin.experiment.list.get({
            query: data,
            header: {
                hackathon_name: currentHackathon.name
            }
        });
    }
//
//    // call api to update a admin
//    function updateAdmin(itemData){
//        var currentHackathon = oh.comm.getCurrentHackathon();
//        return oh.api.admin.hackathon.administrator.put({
//            body: itemData,
//            header: {
//                hackathon_name: currentHackathon.name
//            }
//        }, function(data) {
//            if(data.error){
//                alert(data.error.message)
//            }else{
//            }
//        });
//    }
//


    // initial submit button events
    function forminit(){
        var filter = $('#expr_list_filter');
        filter.bootstrapValidator().on('success.form.bv', function(e) {
            e.preventDefault();
            var data = getFilterData();
            getExprListByFilter(data).then(function(){
                pageLoad()
            })
        });
    }

    function init(){
        var editLi = undefined;
        pageLoad();
        forminit();

//        $('[data-type="new"],[data-type="cancel"]').click(function(e){
//            isupdate = false ;
//            $('#adminform').data({id:undefined}).find('[type="submit"]').removeAttr('disabled')
//            $('#adminform').data({id:undefined}).find('#admin_email').removeAttr('disabled')
//            resetForm();
//            toggleTable();
//        });
//
//        $('#adminlisttable').on('click','[data-type="edit"]',function(e){
//            editLi = $(this).parents('tr');
//            var item = editLi.data('tmplItem').data;
//            setFormData(item);
//            isupdate = true ;
//            toggleTable();
//        });
//
//        var confirmModal = $('#confirm_modal').on('show.bs.modal',function(e){
//            console.log(e);
//            editLi = $(e.relatedTarget).parents('tr');
//        }).on('click','[data-type="ok"]',function(e){
//            var item = editLi.data('tmplItem').data;
//            deleteAdmin(item.id).then(function(){
//                pageLoad()
//            });
//            confirmModal.modal('hide');
//        });
    }

    $(function() {
        init();
    });

})(jQuery, window.oh);