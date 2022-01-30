$(document).ready(function(){
    $('a.subscription').click(function(e){
        e.preventDefault();
        let username = $(this).data('name');
        $.post('/accounts/subscribe/', {
            'username': username,
            'action': $(this).data('action')
        },
        function(data){
            if (data['status'] === 'ok'){
                let a_subscription_tag = $(`a.subscription[data-name=${username}]`);
                let span_subscription_tag = $(`span.subscribed[data-name=${username}]`);
                let last_action = a_subscription_tag.data('action');
                a_subscription_tag.data('action', last_action === 'add' ? 'delete' : 'add');
                a_subscription_tag.text(last_action === 'add' ? 'Отписаться' : 'Подписаться');
                last_action === 'add' ?
                    span_subscription_tag.append('<p>Вы подписаны</p>') :
                    $(`span.subscribed[data-name=${username}] p`).remove();
            }
        });
    });
});