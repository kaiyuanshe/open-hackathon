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

    var isupdate = false;

    function toggleTable(){
        if($('#adminlisttable').css('display') == 'none' ){
            $('#adminlisttable').show();
            $('#adminform').hide()
        }else{
            $('#adminlisttable').hide();
            $('#adminform').show()
        }
    }


     //get form-data for submit
     function getFormData(){
        var formData = {
            id:$('#adminform').data('id'),
            email:$.trim($('#admin_email').val()),
            role_type:$.trim($('#role_type').val()),
            remarks:$.trim($('#remarks').val())
         }
        return formData;
     }


    //set form-data for edit
    function setFormData(data){
        $('#admin_email').val(getPriEmail(data.user_info.email)).attr({disabled:'disabled'});
        $('#role_type').val(data.role_type);
        $('#remarks').val(data.remarks);
        $('#adminform').data({id:data.id}).find('[type="submit"]').removeAttr('disabled')
    }


    // set an empty form for new
    function resetForm(){
         $('#adminform').data('bootstrapValidator').resetForm(true);
         remarks:$.trim($('#remarks').val())
    }



    // initial table to show admin list
    function pageLoad(){
        var list = $('#hackathon_admin_list');
        var currentHackathon = oh.comm.getCurrentHackathon();
        oh.api.admin.hackathon.administrator.list.get({
            header: {
                hackathon_name: currentHackathon.name
            }
        }, function(data) {
            list.empty().append($('#hackathon_admin_list_template').tmpl(data,{
                getOnline:function(online){
                    if(online == 1){
                        return '在线'
                    }
                    return '下线';
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
    }


    function getPriEmail(emails){
        var els = '';
        $.each(emails,function(i,email){
            if(email.primary_email == 1){
                els = email.email;
                return false;
            }
        });
        return els
    }


    // call api to add a admin
    function createAdmin(itemData){
        var currentHackathon = oh.comm.getCurrentHackathon();
        return oh.api.admin.hackathon.administrator.post({
            body: itemData,
            header: {
                hackathon_name: currentHackathon.name
            }
        }, function(data) {
            if(data.error){
                alert(data.error.message)
            }else{
            }
        });
    }


    // call api to update a admin
    function updateAdmin(itemData){
        var currentHackathon = oh.comm.getCurrentHackathon();
        return oh.api.admin.hackathon.administrator.put({
            body: itemData,
            header: {
                hackathon_name: currentHackathon.name
            }
        }, function(data) {
            if(data.error){
                alert(data.error.message)
            }else{
            }
        });
    }


    // call api to delete a admin
    function deleteAdmin(id){
        var currentHackathon = oh.comm.getCurrentHackathon();
        return oh.api.admin.hackathon.administrator.delete({
            query: {id:id},
            header: {
                hackathon_name: currentHackathon.name
            }
        }, function(data) {
            if(data.error){
                alert(data.error.message)
            }else{
            }
        });
    }


    // initial submit button events
    function forminit(){
        var adminform = $('#adminform');
        adminform.bootstrapValidator().on('success.form.bv', function(e) {
            e.preventDefault();
            var itemData = getFormData();
            (isupdate ? updateAdmin(itemData): createAdmin(itemData)).then(function(){
                pageLoad()
                toggleTable()
            })
        });
    }


    function init(){
        var editLi = undefined;
        pageLoad();
        forminit();

        $('[data-type="new"],[data-type="cancel"]').click(function(e){
            isupdate = false ;
            $('#adminform').data({id:undefined}).find('[type="submit"]').removeAttr('disabled')
            resetForm();
            toggleTable();
        });

        $('#adminlisttable').on('click','[data-type="edit"]',function(e){
            editLi = $(this).parents('tr');
            var item = editLi.data('tmplItem').data;
            setFormData(item);
            isupdate = true ;
            toggleTable();
        });

        var confirmModal = $('#confirm_modal').on('show.bs.modal',function(e){
            console.log(e);
            editLi = $(e.relatedTarget).parents('tr');
        }).on('click','[data-type="ok"]',function(e){
            var item = editLi.data('tmplItem').data;
            deleteAdmin(item.id).then(function(){
                pageLoad()
            });
            confirmModal.modal('hide');
        });




    }

    $(function() {
        init();
    });

})(jQuery, window.oh);