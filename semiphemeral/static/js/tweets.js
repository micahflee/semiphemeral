$(function(){
  $('.tweets-to-delete').html('loading please wait...');

  // Load all tweets to delete
  $.get('/api/tweets-to-delete', function(tweets){
    $('.tweets-to-delete').empty();

    // Make a list of tweet ids
    var ids = [];
    for(var id in tweets) {
      ids.push(id);
    }

    count = 0;
    for(var id in tweets) {
      $('.tweets-to-delete').append('<div class="tweet" id="tweet-'+id+'"></div>');
      twttr.widgets.createTweet(id, $('#tweet-'+id)[0], {
        'dnt': true
      });

      count++;
      if(count == 20) { break; }
    }
  })
})
