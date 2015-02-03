$(function() {
    var list = $('.services-list').hide().eq(0).show();
    $('input:radio').iCheck({
        checkboxClass: 'icheckbox_square-blue',
        radioClass: 'iradio_square-blue',
        increaseArea: '20%' // optional
    }).on('ifChecked', function(event) {
        var parent = $(this).parents('.text-center');
        list.hide();
        list= parent.find('ul');
        list.show();
    });
    $("#submit").click(function() {
        var radio = $('input:radio:checked');
        var cid = radio.val();
        window.location.href = "/hackathon?hackathon=" + CONFIG.hackathon.name + "&cid=" + cid
    });
});
