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

    // true: PUT to update; false: POST to create
    var is_update = false;
    var currentHackathon = oh.comm.getCurrentHackathon();

    // Get created template list
    function bindTemplateList(){

        var list = $('#templatelist');
        oh.api.admin.template.list.get({
            header:{hackathon_name:currentHackathon}
        }, function(data){
            var index = 0;
            list.empty().append($('#template_item').tmpl(data,{
                hackathon_name:currentHackathon,
                getIndex:function(){ return ++index;}
            }));
        });
    }

    // clear template form after create/update template
    function clearTemplateForm(){
        $('[data-type="temp-unit-list"]').empty();
        var form = $('#templateform');
        form[0].reset();
        form.data('bootstrapValidator').resetForm(true);
    }

    // add bootstrap validator when create template unit form and create port form dynamically
    function addFieldValidate(element){
         $(element).find('[data-validate="true"]').each(function(i,input){
            $('#templateform').bootstrapValidator('addField',$(input));
         })
    }

    // create template unit form dynamically
    // data is None: create; empty form
    // data is not None: update; fill data to form
    function createTemplateUnit(data){
        var templist= $('[data-type="temp-unit-list"]');
        var template_unit = $($('#template_unit_item').html());
        if(data){
            template_unit.find('[name="name"]').val(data['name']);
            template_unit.find('[name="type"]').val(data['type']);
            template_unit.find('[name="description"]').val(data['description']);
            template_unit.find('[name="image"]').val(data['Image']);
            template_unit.find('[name="env"]').val(data['Env'].join(";"));
            template_unit.find('[name="cmd"]').val(data['Cmd'].join(" "));
            for(var i = 0; i < data['ports'].length; i++)
                if(data['ports'][i]['port'] == data['remote']['port']){
                    template_unit.find('[name="remote-name"]').val(data['ports'][i]['name']);
                    break;
                }
            template_unit.find('[name="remote-provider"]').val(data['remote']['provider']);
            template_unit.find('[name="remote-protocol"]').val(data['remote']['protocol']);
            template_unit.find('[name="remote-port"]').val(data['remote']['port']);
            template_unit.find('[name="remote-username"]').val(data['remote']['username']);
            template_unit.find('[name="remote-password"]').val(data['remote']['password']);
            for(var i = 0; i < data['ports'].length; i++)
                if(data['ports'][i]['port'] != data['remote']['port'])
                    createPort(template_unit.find('[data-type="port-list"]'), data['ports'][i]);
        }
        template_unit.appendTo(templist);
        addFieldValidate(template_unit);
        return template_unit;
    }

    // delete template unit form dynamically
    function deleteTemplateUnit(element, data){
        $(element).parents('[data-type="template-unit-group"]').detach();
    }

    // create port form dynamically
    // data is None: create; empty form
    // data is not None: update; fill data to form
    function createPort(element, data){
        var portlist= $(element).parents('[data-type="template-unit-group"]').find('[data-type="port-list"]');
        var port = $($('#port_item').html());
        if(data){
            port.find('[name="name"]').val(data['name']);
            port.find('[name="port"]').val(data['port']);
            port.find('[name="public"]').val(data['public']);
            port.find('[name="protocol"]').val(data['protocol']);
            if('url' in data){
                var url_protocol = data['url'].substring(0, data['url'].indexOf(":"));
                port.find('[name="url-protocol"]').val(url_protocol);
                var url_path = data['url'].substring(data['url'].lastIndexOf("/") + 1, data['url'].length);
                port.find('[name="url-path"]').val(url_path);
            }
        }
        port.appendTo(portlist);
        addFieldValidate(port);
        return port;
    }

    // delete port form dynamically
    function deletePort(element, data){
        $(element).parents('[data-type="port-group"]').detach();
    }

    // remove empty string produced by split
    function removeEmptyString(data){
        var ans = [];
        for(var i = 0; i < data.length; i++)
            if(data[i] != '')
                ans.push(data[i]);
        return ans;
    }

    // compose PUT/POST data for back end api
    function getFormData(){
        var data = [];
        $('[data-type="template-unit-group"]').each(function(i,group){
            var $group = $(group);
            var remote = {
                provider: $group.find('[name="remote-provider"]').val(),
                protocol: $group.find('[name="remote-protocol"]').val(),
                username: $group.find('[name="remote-username"]').val(),
                password: $group.find('[name="remote-password"]').val(),
                port: Number($group.find('[name="remote-port"]').val())
            }
            var ports = []
            ports.push({
                name: $group.find('[name="remote-name"]').val(),
                port: remote['port'],
                public: true,
                protocol: 'tcp'
            })
            $group.find('[data-type="port-group"]').each(function(i,portgroup){
                var $portgroup = $(portgroup);
                var port = {
                    name: $portgroup.find('[name="name"]').val(),
                    port: Number($portgroup.find('[name="port"]').val()),
                    public: Boolean($portgroup.find('[name="public"]').val()),
                    protocol: $portgroup.find('[name="protocol"]').val()
                }
                if($portgroup.find('[name="url-protocol"]').val().length > 0)
                    port['url'] = $portgroup.find('[name="url-protocol"]').val() + '://{0}:{1}/' + $portgroup.find('[name="url-path"]').val()
                ports.push(port)
            })
            data.push({
                name: $group.find('[name="name"]').val(),
                type: $group.find('[name="type"]').val(),
                description: $group.find('[name="description"]').val(),
                ports: ports,
                remote: remote,
                Image: $group.find('[name="image"]').val(),
                Env: removeEmptyString($group.find('[name="env"]').val().split(";")),
                Cmd: removeEmptyString($group.find('[name="cmd"]').val().split(" "))
            })
        })
        return {
            template_name: $('#name').val(),
            description: $('#description').val(),
            provider: Number($('#provider').val()),
            virtual_environments: data
        };
    }

    // fill data to form
    function setFormData(item){
        data = item['data']
        $('#name').val(data['expr_name']).attr({disabled:'disabled'});
        $('#description').val(data['description']);
        $('#provider').val(item['provider']).attr({disabled:'disabled'});
        data['virtual_environments'].forEach(createTemplateUnit);
    }

    // POST to create
    function createTemplate(data){
        return oh.api.admin.template.post({
            body: data,
            header: {hackathon_name:currentHackathon}
        }, function(data){
            if(data.error){
                alert(data.error.message);
            }else{
            }
        })
    }

    // PUT to update
    function updateTemplate(data){
        return oh.api.admin.template.put({
            body: data,
            header: {hackathon_name:currentHackathon}
        }, function(data){
            if(data.error){
                alert(data.error.message);
            }else{
            }
        })
    }

    function toggleTable(){
        clearTemplateForm();
        if($('#templatetable').css('display') == 'none' ){
            $('#templatetable').show();
            $('#templateform').hide()
        }else{
            $('#templatetable').hide();
            $('#templateform').show()
        }
    }

    function init(){
        var templateform = $('#templateform');
        templateform.bootstrapValidator().on('success.form.bv', function(e) {
            e.preventDefault();
            var formData = getFormData();
            (is_update ? updateTemplate(formData) : createTemplate(formData)).then(function(){
                if(is_update)
                    is_update = false;
                bindTemplateList();
                toggleTable();
            })
        });

        templateform.on('click','[data-type="btn_add_port"]',function(e){
            createPort(this);
        });

        templateform.on('click','[data-type="btn_delete_port"]',function(e){
            deletePort(this);
        });

        var templatelist = $('#templatelist');
        templatelist.on('click','[data-type="template_item_edit"]',function(e){
            is_update = true;
            toggleTable();
            var item = $(this).parents('tr').data('tmplItem').data;
            setFormData(item);
        });

        var confirm_modal = $('#confirm_modal').on('show.bs.modal',function(e){
            var item = $(e.relatedTarget).parents('tr').data('tmplItem').data;
            confirm_modal.data({item:item});
        }).on('click','[data-type="ok"]',function(e){
            var item = confirm_modal.data('item');
             oh.api.admin.template.delete({
                query: {id:item.id},
                header: {hackathon_name:currentHackathon}
             },
             function(data){
                if(data.error){
                    alert(data.error.message);
                }else{
                    bindTemplateList();
                    confirm_modal.modal('hide');
                }
             })
        })

        var add_template_unit = $('#btn_add_template_unit').click(function(e){
            createTemplateUnit();
        })

        templateform.on('click','[data-type="btn_delete_template_unit"]',function(e){
            deleteTemplateUnit(this);
        });

        $('[data-type="template_item_add"]').click(function(e){
            $('#name').removeAttr('disabled');
            $('#provider').removeAttr('disabled');
            toggleTable();
            createTemplateUnit();
        });

        $('[data-type="cancel"]').click(function(e){
            toggleTable();
        });
    }

    $(function() {
        init();
        bindTemplateList();
        createTemplateUnit();
    })

})(window.jQuery,window.oh);