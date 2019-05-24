function display_tweets(ids, page=0, count=100) {
  console.log('display_tweets', 'ids=' + ids.length + ', page='+page+', count='+count);

  // Display info
  $('.info').append($('<div/>').html('Page '+comma_formatted(page)+' of '+comma_formatted(ids.length-1)+' tweets are staged for deletion'));

  $('.tweets-to-delete').empty();
  $('.pagination').empty();
  num_pages = Math.ceil(ids.length / count);

  function add_item(text, action=null) {
    console.log('add_item', text)
    var $item = $('<span/>').addClass('item').text(text);
    if(action) {
      $item.click(action);
    } else {
      $item.addClass('item-current');
    }
    $('.pagination').append($item);

  }

  // Pagination controls
  if(page > 0) {
    add_item('Previous', function(){
      display_tweets(ids, page-1, count);
    });
  }

  for(var i=page-10; i<page; i++) {
    if(i >= 0) {
      add_item(i, function(){
        display_tweets(ids, i, count);
      });
    }
  }

  add_item(page);

  for(var i=page+1; i<page+10; i++) {
    add_item(i, function(){});
  }

  if(page < num_pages-1) {
    add_item('Next', function(){
      display_tweets(ids, page+1, count);
    });
  }

  // Display the page of tweets
  for(var i=page*count; i<(page+1)*count; i++) {
    $('.tweets-to-delete').append('<div class="tweet" id="tweet-'+ids[i]+'"></div>');
    twttr.widgets.createTweet(ids[i], $('#tweet-'+ids[i])[0], {
      'dnt': true
    });
  }
}

$(function(){
  // Ajax loader
  $('.tweets-to-delete').html('<img src="/static/img/loading.gif" alt="">');

  // Load all tweets to delete
  $.get('/api/tweets-to-delete', function(tweets){
    var ids = [];
    for(var id in tweets) {
      ids.push(id);
    }

    window.semiphemeral = {
      tweets: tweets,
      ids: ids
    }

    // Display tweets
    display_tweets(self.semiphemeral.ids);
  })
})
