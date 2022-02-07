$(document).ready(function(){
    $('a.subscription').click(function(e){
        e.preventDefault();
        let username = $(this).data('name');
        $.article('/accounts/subscribe/', {
            'username': username,
            'action': $(this).data('action')
        },
        function(data){
            if (data['status'] === 'ok'){
                let aSubscriptionTag = $(`a.subscription[data-name=${username}]`);
                let spanSubscriptionTag = $(`span.subscribed[data-name=${username}]`);
                let lastAction = aSubscriptionTag.data('action');
                aSubscriptionTag.data('action', lastAction === 'add' ? 'delete' : 'add');
                aSubscriptionTag.text(lastAction === 'add' ? 'Отписаться' : 'Подписаться');
                lastAction === 'add' ?
                    spanSubscriptionTag.append('<p>Вы подписаны</p>') :
                    $(`span.subscribed[data-name=${username}] p`).remove();
            }
        });
    });
});