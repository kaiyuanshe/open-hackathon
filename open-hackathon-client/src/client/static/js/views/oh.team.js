/*
 * This file is covered by the LICENSING file in the root of this project.
 */

(function ($, oh) {
    'use strict';

    function pageLoad(){
        oh.api.user.team.list.get().then(function(data){
            console.log(data);
        })
    }

    function bindEvent(){

    }

    function init(){
        bindEvent();
        pageLoad();
    }

    $(function () {
        init();
    });

})(window.jQuery, window.oh);