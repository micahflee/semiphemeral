function comma_formatted(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

$(function(){
  $.get('/api/statistics', function(data){
    is_configured = (data.is_configured ? 'yes' : 'no');
    $('.statistics .is_configured').text(is_configured);
    $('.statistics .last_fetch').text(data.last_fetch);
    $('.statistics .my_tweets').text(comma_formatted(data.my_tweets));
    $('.statistics .my_retweets').text(comma_formatted(data.my_retweets));
    $('.statistics .my_likes').text(comma_formatted(data.my_likes));
    $('.statistics .deleted_tweets').text(comma_formatted(data.deleted_tweets));
    $('.statistics .deleted_retweets').text(comma_formatted(data.deleted_retweets));
    $('.statistics .unliked_tweets').text(comma_formatted(data.unliked_tweets));
    $('.statistics .excluded_tweets').text(comma_formatted(data.excluded_tweets));
    $('.statistics .other_tweets').text(comma_formatted(data.other_tweets));
    $('.statistics .threads').text(comma_formatted(data.threads));
  })
})
