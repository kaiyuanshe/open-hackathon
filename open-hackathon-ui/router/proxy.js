var express = require('express')
var router = express.Router()
var config = require('../config')
var  request = require('request')

function GetAPIPath(module,method){
    return [config.proxy,'api',module,method || ''].join('/')
}

router.get(config.sociallogin.router,function(req,res){
    var option = {
        url: GetAPIPath('user','login'),
        json:{
            provider:req.params.name,
            code: req.query.code
        }
    }
    request[config.api.user.login](option,function(err, response,body){
        if(err){
            log('err : sociallogin',err)
            log('err : body',body)
        }else{
            for(var key in body){
                  res.cookie(key,body[key]);
            }
            //res.cookie('rememberme','1',{ expires: new Date(Date.now() + 2592000000), httpOnly: true })
            res.redirect('/');
        }
    })
})

module.exports = router;