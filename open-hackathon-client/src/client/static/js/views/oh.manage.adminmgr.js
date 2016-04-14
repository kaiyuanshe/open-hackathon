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
            $('#adminlisttable').show();
            $('#adminsearchbartable').hide();
            $('#adminsearchlisttable').hide()
        }else if(status == 1){
            $('#adminlisttable').hide();
            $('#adminsearchbartable').show();
            $('#adminsearchlisttable').hide()
        }else{
            $('#adminlisttable').hide();
            $('#adminsearchbartable').show();
            $('#adminsearchlisttable').show()
        }
    }

    // initial table to show admin list
    function pageLoad(){
        var list = $('#hackathon_admin_list');

        oh.api.admin.hackathon.administrator.list.get({
            header: {
                hackathon_name: currentHackathon
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
                    else if(role_type == 1)
                        return '管理员'
                    else
                        return '普通用户';
                },
                getRoleStr(role_type){
                    return str(role_type);
                },
                getEmails:function(emails){
                    return getPriEmail(emails);
                }
            }));
            list.find('.editable').editable({
                url: function (params) {
                    var data = $(this).parents('tr').data('tmplItem').data;

                    if(data.user_info.name == "admin"){
                        alert("修改admin管理员权限是无效的");
                        pageLoad();
                    }
                    else{
                        switch(params.value){
                            case "1": data.role_type = 1; break;
                            case "2": data.role_type = 2; break;
                            default: data.role_type = 3;
                        }
                        updateAdmin(data).then(function(){
                            pageLoad();
                        });
                    }
                }
            });
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
        if(itemData.role_type != "3"){
            return oh.api.admin.hackathon.administrator.post({
                body: itemData,
                header: {
                    hackathon_name: currentHackathon
                }
            }, function(data) {
                if(data.error){
                    alert(data.error.message)
                }else{
                }
            });
        }
    }

    // call api to update a admin
    function updateAdmin(itemData){
        if(itemData.user_info.name != "admin" && itemData.role_type != "3"){
            return oh.api.admin.hackathon.administrator.put({
                body: itemData,
                header: {
                    hackathon_name: currentHackathon
                }
            }, function(data) {
                if(data.error){
                    alert(data.error.message)
                }else{
                }
            });
        }
    }

    // call api to delete a admin
    function deleteAdmin(id){
        return oh.api.admin.hackathon.administrator.delete({
            query: {id:id},
            header: {
                hackathon_name: currentHackathon
            }
        }, function(data) {
            if(data.error){
                alert(data.error.message)
            }else{
            }
        });
    }

    function getSearchBarData(){
        var formData = {
            keyword:$.trim($('#admin_searchbar').val()),
         };
        return formData;
    }

    // call api to fuzzy search related users
    function searchUser(formData){
        return oh.api.admin.user.list.get({
            header: {
                hackathon_name: currentHackathon,
            },
            query:{
                keyword: formData['keyword']
            }
        }, function(data){
            if(data.error){
                alert(data.error.message)
            }else{
                var list = $('#hackathon_search_list');
                list.empty().append($('#hackathon_admin_search_list_template').tmpl(data.items,{
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
                        else if(role_type == 1){
                            return '管理员'
                        }
                        else
                            return '普通用户';
                    },
                    getEmails:function(emails){
                        return getPriEmail(emails);
                    }
                }));
                list.find('.editable').editable({
                    url: function (params) {
                        var data = $(this).parents('tr').data('tmplItem').data;

                        if(data.role_type == 3){
                            switch(params.value){
                                case "1": data.role_type = 1; break;
                                case "2": data.role_type = 2; break;
                                default: data.role_type = 3;
                            }
                            createAdmin(data).then(function(){
                                pageLoad()
                            });
                        }
                        else{
                            alert("该用户已经是管理员或裁判，无须再次添加，如需修改或删除管理员，请返回前一页面操作。")
                        }
                    }
                });
                oh.comm.removeLoading();
            }
        });
    }

    function searchBarValidator() {
        var fromValidator = $(adminsearchbarform).bootstrapValidator().on('success.form.bv', function (e, ok){
            e.preventDefault();
            var formData = getSearchBarData();
            searchUser(formData);
            toggleTable(2);
        });
    }

    function init(){
        pageLoad();
        toggleTable(0);
        searchBarValidator();

        $('[data-type="new"]').click(function(e){
            toggleTable(1);
        });

        $('[data-type="cancel"]').click(function(e){
            $('#admin_searchbar').val("");
            toggleTable(0);
        });

        $('[data-type="search"]').click(function(e){
            var formData = getSearchBarData();
            searchUser(formData);
            toggleTable(2);
        });

        var editRemarkModal = $('#edit_remark_modal').on('show.bs.modal',function(e){
            data = $(e.relatedTarget).parents('tr').data('tmplItem').data;
            $('#remarks').val(data.remarks)
        }).on('click','[data-type="ok"]',function(e){
            data.remarks = $('#remarks').val();
            if(data.user_info.name != "admin"){
                updateAdmin(data).then(function(){
                    pageLoad()
                });
            }
            editRemarkModal.modal('hide');
        });

        var deleteAdminModal = $('#delete_admin_modal').on('show.bs.modal',function(e){
            list = $(e.relatedTarget).parents('tr');
        }).on('click','[data-type="ok"]',function(e){
            var data = list.data('tmplItem').data;
            if(data.user_info.name == "admin")
                alert("不允许删除admin管理员");
            else{
                deleteAdmin(data.id).then(function(){
                    pageLoad()
                });
            }
            deleteAdminModal.modal('hide');
        });

    }

    $(function() {
        init();
    });

})(jQuery, window.oh);