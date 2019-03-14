/*
 * This file is covered by the LICENSING file in the root of this project.
 */

;
(function($, oh) {
    function pageLoad(){
        oh.api.admin.hackathon.list.get(function(data){
            container = $("#hackathon_list");
            container.empty().append($('#hackathon_template').tmpl(data));
            container.find('.editable').editable({
                url: function(params) {
                    var data = $(this).parents('tr').data('tmplItem').data;
                    var d = new $.Deferred;
                    oh.api.admin.hackathon.put({
                        body: {
                            id: data.id,
                            name: data.name,
                            status: params.value
                        },
                        header: {
                            hackathon_name: data.name
                        }
                    }, function(data) {
                        if (data.error) {
                            d.reject(data.error.friendly_message)
                        } else {
                            d.resolve();
                        }
                    });
                    return d.promise();
                }
            });
        })
    }


    function init(){
        pageLoad();
    }

    $(function() {
        init();
    });
})(jQuery, window.oh);
