$(document).ready(function(){
    var code = getParameterByName("code")

    hpost_local("/ui/login", {
            "provider": "github",
            "code": code
        },
        function(resp){
            save_token(resp.token)
            if(resp.experiments.length > 0)
                location.href = ":5000/hackathon"
            else
                location.href = ":5000/settings"
        },
        function(){
            alert("login failed")
        }
    )
});
