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

(function($, oh) {

    function bindTemplateList(){
        var currentHackathon = oh.comm.getCurrentHackathon();
        var list = $('#templatelist');
        oh.api.admin.hackathon.template.get({
            header:{hackathon_name:currentHackathon.name}
        },
        function(data){
            var index = 0;
            list.empty().append($('#template_item').tmpl(data,{getIndex:function(){ return ++index;}}));
        });
    }

    function createTemplateUnit(data){
        var templist= $('[data-type="temp-unit-list"]');
        var template_unit = $($('#template_unit_item').html());
        if(data){
            // todo
        }
        return template_unit.appendTo(templist);
    }

    function createPort(element, data){
        var portlist= $(element).parents('[data-type="template-unit-group"]').find('[data-type="port-list"]');
        var port = $($('#port_item').html());
        if(data){
            // todo
        }
        return port.appendTo(portlist);
    }

    function getFormData(){
        var data = [];
        $('[data-type="template-unit-group"]').each(function(i,group){
            var $group = $(group);
            var remote = {
                provider: $group.find('[name="remote-provider"]').val(),
                protocol: $group.find('[name="remote-protocol"]').val(),
                username: $group.find('[name="remote-username"]').val(),
                password: $group.find('[name="remote-password"]').val(),
                port: $group.find('[name="remote-port"]').val()
            }
            var ports = []
            ports.push({
                name: $group.find('[name="remote-name"]').val(),
                port: remote['port'],
                public: true,
                protocol: 'tcp'
            })
            $('[data-type="port-group"]').each(function(i,portgroup){
                var $portgroup = $(portgroup);
                ports.push({
                    name: $portgroup.find('[name="name"]').val(),
                    port: $portgroup.find('[name="port"]').val(),
                    public: $portgroup.find('[name="public"]').val(),
                    protocol: $portgroup.find('[name="protocol"]').val(),
                    url: $portgroup.find('[name="url"]').val()
                })
            })
            data.push({
                name: $group.find('[name="name"]').val(),
                port: ports,
                remote: remote,
                Image: $group.find('[name="image"]').val(),
                Env: $group.find('[name="env"]').val().split(";"),
                Cmd: $group.find('[name="cmd"]').val().split(" ")
            })
        })
        return {
            expr_name: $('#name').val(),
            description: $('#description').val(),
            virtual_environments: data
        };
    }

    function init(){
        var currentHackathon = oh.comm.getCurrentHackathon();
        var templateform = $('#templateform');
        templateform.bootstrapValidator()
            .on('success.form.bv', function(e) {
                e.preventDefault();
                oh.api.admin.hackathon.template.post({
                    body: getFormData(),
                    query:{},
                    header:{hackathon_name:currentHackathon.name}
                }, function(data){
                    if(data.error){
                        // todo
                    }else{
                        bindTemplateList();
                    }
                })
            });

        templateform.on('click','[data-type="btn_add_port"]',function(e){
            createPort(this);
         });


        var confirm_modal = $('#confirm_modal').on('show.bs.modal',function(e){
            var item = $(e.relatedTarget).parents('tr').data('tmplItem').data;
            confirm_modal.data({item:item});
        }).on('click','[data-type="ok"]',function(e){
            var item = confirm_modal.data('item');
             oh.api.admin.hackathon.template.delete({
                body:{certificate_id:item.id},
                header:{hackathon_name:currentHackathon.name}
             },
             function(data){
                if(data.error){
                    //todo;
                }else{
                    bindTemplateList();
                    confirm_modal.modal('hide');
                }
             })
        })

        var add_template_unit = $('#btn_add_template_unit').click(function(e){
            createTemplateUnit();
        })

    }

    $(function() {
        init();
        bindTemplateList();
    })

})(window.jQuery,window.oh);