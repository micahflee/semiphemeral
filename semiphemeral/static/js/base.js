$(function(){
  $.get('/api/statistics', function(data){
    is_configured = (data.is_configured ? 'yes' : 'no');
    $('.statistics .is_configured').text(is_configured);
    $('.statistics .last_fetch').text(data.last_fetch);
    $('.statistics .my_tweets').text(data.my_tweets);
    $('.statistics .my_retweets').text(data.my_retweets);
    $('.statistics .deleted_tweets').text(data.deleted_tweets);
    $('.statistics .deleted_retweets').text(data.deleted_retweets);
    $('.statistics .excluded_tweets').text(data.excluded_tweets);
    $('.statistics .other_tweets').text(data.other_tweets);
    $('.statistics .threads').text(data.threads);
  })
})
