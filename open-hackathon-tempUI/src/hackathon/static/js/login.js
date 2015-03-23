$(document).ready(function(){

    $('#githublogin').click(function() {
        location.href = CONFIG.github.authorize_url;
    });

    $('#qqlogin').click(function() {
        location.href = CONFIG.qq.authorize_url;
    });

    $('#gitcafelogin').click(function() {
        location.href = CONFIG.gitcafe.authorize_url;
    });

     $('#weibologin').click(function() {
        location.href = CONFIG.weibo.authorize_url;
    });

});