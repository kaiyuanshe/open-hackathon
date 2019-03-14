/*
 * This file is covered by the LICENSING file in the root of this project.
 */

$(document).ready(function(){

    $('#githublogin').click(function() {
        location.href = CONFIG.github.authorize_url;
    });

    $('#qqlogin').click(function() {
        location.href = CONFIG.qq.authorize_url;
    });

    $('#wechatlogin').click(function() {
        location.href = CONFIG.wechat.authorize_url;
    });

     $('#weibologin').click(function() {
        location.href = CONFIG.weibo.authorize_url;
    });
     $('#livelogin').click(function() {
        location.href = CONFIG.live.authorize_url;
    });

});