$(document).ready(function(){
    var code = getParameterByName("code")

    gitcafe_post_local("/ui/login", {
            "provider": "gitcafe",
            "code": code
        },
        function(resp){
            save_token(resp.token)
            if(resp.experiments.length > 0)
                location.href = "/hackathon"
            else
                location.href = "/settings"
        },
        function(){
            alert("login failed")
        }
    )
});
