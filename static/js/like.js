$(document).ready(function(){
    let aLike = $('a.like');
    aLike.click(function(e){
        e.preventDefault();
        $.article('/blog/like/', {
            'article_id': aLike.data('article_id'),
            'action': aLike.data('action')
        },
        function(data){
            console.log(data['status']);
            if (data["status"] === 'ok'){
                let spanLikeCount = $('#like-count');
                let imgLike = $('img.img-like');
                let lastCount = Number(spanLikeCount.text());
                if (aLike.data('action') === 'like'){
                    aLike.data('action', 'unlike');
                    imgLike.attr('src', '/static/assets/unlike.svg');
                    spanLikeCount.text(lastCount + 1);
                }
                else{
                    aLike.data('action', 'like');
                    imgLike.attr('src', '/static/assets/like.svg');
                    spanLikeCount.text(lastCount - 1);
                }
            }
        })
    });
});
