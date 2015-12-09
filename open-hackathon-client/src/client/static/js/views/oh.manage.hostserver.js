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
    var isUpdateOperation = false;
    var updateHostserverId = 0;

    function toggleTable() {
        if ($('#hostserverlisttable').css('display') == 'none') {
            $('#hostserverlisttable').show();
            $('#hostserverform').hide()
        } else {
            $('#hostserverlisttable').hide();
            $('#hostserverform').show()
        }
    }

    function setFormData(data) {
        $('#vm_name').val(data.vm_name);
        $('#public_dns').val(data.public_dns);
        $('#public_ip').val(data.public_ip);
        $('#public_docker_api_port').val(data.public_docker_api_port);
        $('#private_ip').val(data.private_ip);
        $('#private_docker_api_port').val(data.private_docker_api_port);
        $('#container_max_count').val(data.container_max_count);
        $('#disabled').val(data.disabled == 0 ? "启用":"禁用");
    }

    function clearFormData() {
        $('#vm_name').val("");
        $('#public_dns').val("");
        $('#public_ip').val("");
        $('#public_docker_api_port').val("4243");
        $('#private_ip').val("");
        $('#private_docker_api_port').val("4243");
        $('#container_max_count').val("10");
    }

    function getFormData() {
        data = {};
        data.vm_name = $('#vm_name').val();
        data.public_dns = $('#public_dns').val();
        data.public_ip = $('#public_ip').val();
        data.public_docker_api_port = $('#public_docker_api_port').val();
        data.private_ip = $('#private_ip').val();
        data.private_docker_api_port = $('#private_docker_api_port').val();
        data.container_max_count = parseInt($('#container_max_count').val(), 10);
        data.disabled = $('#disabled').val() == '启用'? 0:1; //0:abled 1:disabled
        data.is_auto = 2 //auto=1, manual=2;
        return data;
    }

    function createHostServer(data) {
        oh.comm.alert("提示", "该请求需要测试Host Server的Docker服务是否可用，请等待最多5秒");
        return oh.api.admin.hostserver.post({
            header: {
                hackathon_name: currentHackathon
            },
            body: data
        }, function (response) {
            if (response.error) {
                oh.comm.alert('错误', data.error.friendly_message);
            } else {
                clearFormData();
                toggleTable();
                reload_host_server();
                $("#submit_button").removeAttr("disabled")
            }
        });
    }

    function updateHostServer(data) {
        oh.comm.alert("提示", "该请求需要测试Host Server的Docker服务是否可用，请等待最多5秒");
        return oh.api.admin.hostserver.put({
            header: {
                hackathon_name: currentHackathon
            },
            body: data
        }, function(response){
            if(response.error) {
                oh.comm.alert('错误', response.error.friendly_message);
            } else{
                clearFormData();
                toggleTable();
                reload_host_server();
                $("#submit_button").removeAttr("disabled")
            }
        });
    }

    function deleteHostServer(host_server_id) {
        return oh.api.admin.hostserver.delete({
            header: {hackathon_name: currentHackathon},
            query: {id: host_server_id}
        }, function(response) {
            if(response.error){
                oh.comm.alert('错误', response.error.friendly_message);
            }else{
                reload_host_server();
            }
        });
    }

    //refresh and check the container_count of a hostserver
    function refreshHostServerContainerCount(host_server_id) {
        var hostServerInfo = oh.api.admin.hostserver.get({
            header: {hackathon_name: currentHackathon},
            query: {id: host_server_id}
        },function(response){
            if(response.error){
                oh.comm.alert('错误', response.error.friendly_message);
            }else{
                reload_host_server();
            }
        });
        return hostServerInfo.container_count;
    }

    // reload and show host_server list
    function reload_host_server() {
        var list = $('#host_server_list');

        oh.api.admin.hostserver.list.get({
            header: {
                hackathon_name: currentHackathon
            }
        }, function(data) {
            if (!data.error) {
                list.empty().append($('#hostserver_list_template').tmpl(data,{
                    getState:function(state){
                        if(state == 0){
                            return 'VM初始化中'
                        }
                        if(state == 1){
                            return 'Docker初始化中'
                        }
                        if(state == 2){
                            return '就绪'
                        }
                        return '不可用';
                    },
                    getIsAuto:function(is_auto){
                        if(is_auto == 1){
                            return '自动'
                        }
                        return '手动';
                    },
                   getDisabled:function(disabled){
                        if(disabled == 0){
                            return '启用'
                        }
                        return '禁用';
                    }
                }));
                oh.comm.removeLoading();
            }
        });
    }


    function init(){
        reload_host_server();

        var deleteconfirmModal = $('#confirm_delete_modal').on('show.bs.modal',function(e){
            editLi = $(e.relatedTarget).parents('tr');
        }).on('click', '[data-type="ok"]', function (e) {
            var data_hostserver_id = editLi.data('tmplItem').data.id;
            deleteHostServer(data_hostserver_id)
            deleteconfirmModal.modal('hide');
        });

        var refreshconfirmModal = $('#confirm_refresh_modal').on('show.bs.modal',function(e){
            editLi = $(e.relatedTarget).parents('tr');
        }).on('click', '[data-type="ok"]', function (e) {
            var data_hostserver_id = editLi.data('tmplItem').data.id;
            refreshconfirmModal.modal('hide');
            refreshHostServerContainerCount(data_hostserver_id);
        });

        // create new host_server
        $('#new_hostserver').click(function (e) {
            isUpdateOperation = false;
            toggleTable();
        });

        // cancel edit and go back
        $('[data-type="cancel"]').click(function(e){
            toggleTable();
            clearFormData();
        });

        //submit create/edit host_server
        $('#hostserverform').bootstrapValidator().on('success.form.bv', function (e) {
            $("#submit_button").attr("disabled","disabled")
            e.preventDefault();

            var data = getFormData();
            data.id = updateHostserverId;
            isUpdateOperation ? updateHostServer(data) : createHostServer(data);
        });

        //edit host_server
        $('#hostserverlisttable').on('click', '[data-type="edit"]', function (e) {
            isUpdateOperation = true;
            editLi = $(this).parents('tr');
            var formData = editLi.data('tmplItem').data;
            setFormData(formData);
            updateHostserverId = formData.id;
            toggleTable();
        });
    }

    $(function() {
        init();
    });

})(jQuery, window.oh);