/*
 * This file is covered by the LICENSING file in the root of this project.
 */

(function ($, oh) {
    'use strict';

    var hackathon_name = oh.comm.getCurrentHackathon();

    function init() {
        $('#templates').on('click', 'button[data-value]', function (e) {
            var template_name = $(this).data('value');
            window.location.href = '/site/' + hackathon_name + '/workspace?t='+template_name;      
            // oh.api.user.experiment.post({
            //     body: {template_name: template_name, hackathon_name: hackathon_name}
            // }, function (data) {
            //     if(data.error){
            //         // todo Set experiment error
            //     }else{
            //          window.location.href = '/site/' + hackathon_name + '/workspace';
            //     }
            // });
        });
    };

    $(function () {
        init();
    });

})(window.jQuery, window.oh);
