$(document).ready(function(){
    $('#githublogin').click(function() {
        var arr = [CONFIG.github.clientID, CONFIG.github.redirect_uri, CONFIG.github.scope];
        var url = "https://github.com/login/oauth/authorize?" + arr.join("&");
        location.href = url;
    });

    $('#qqlogin').click(function() {
        var arr = [CONFIG.qq.clientID, CONFIG.qq.redirect_uri, CONFIG.qq.scope, CONFIG.qq.state, CONFIG.qq.response_type];
        var url = "https://graph.qq.com/oauth2.0/authorize?" + arr.join("&");
        location.href = url;
    });
    $('#gitcafelogin').click(function() {
        var arr = [CONFIG.gitcafe.clientID, CONFIG.gitcafe.redirect_uri, CONFIG.gitcafe.clientSecret, CONFIG.gitcafe.scope, CONFIG.gitcafe.response_type];
        var url = "https://api.gitcafe.com/oauth/authorize?" + arr.join("&");
        location.href = url;
    });
});