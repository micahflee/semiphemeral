function display_tweets(values) {
  var ids = window.semiphemeral.ids;
  var page = values.page;
  var count = values.count;

  console.log('display_tweets', 'ids=' + ids.length + ', page='+page+', count='+count);

  // Empty what previous page
  $('.info').empty();
  $('.tweets-to-delete').empty();
  $('.pagination').empty();

  // Display info
  var num_pages = Math.ceil(ids.length / count);
  $('.info').append($('<div/>').html('Page '+comma_formatted(page)+' of '+comma_formatted(num_pages)+' - '+comma_formatted(ids.length-1)+' tweets are staged for deletion'));

  // Pagination controls
  function add_pagination_item(text, new_page) {
    console.log('add_pagination_item', text)

    var $item = $('<span/>').addClass('pagination-item');
    if(new_page == page) {
      $item.addClass('pagination-item-current').text(text);
    } else {
      var values = { q:"", page:new_page, count:count };
      var $link = $('<a/>').attr('href', '#'+JSON.stringify(values)).text(text);
      $item.append($link);
    }

    $('.pagination').append($item);
  }
  if(page > 0) {
    add_pagination_item('Previous', page-1);
  }
  for(var i=page-5; i<page+5; i++) {
    if(i >= 0 && i <= num_pages-1) {
      add_pagination_item(i, i);
    }
  }
  if(page < num_pages-1) {
    add_pagination_item('Next', page+1);
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
    $('.controls').show();

    var ids = [];
    for(var id in tweets) {
      ids.push(id);
    }

    window.semiphemeral = {
      tweets: tweets,
      ids: ids
    }

    // When the hash contains a JSON object, pass it into display_tweets
    function parse_hash() {
      if(window.location.hash == "") return false;
      try {
        var hash = decodeURIComponent(window.location.hash).substr(1);
        var values = JSON.parse(hash);
        display_tweets(values);
        return true;
      } catch {
        return false;
      }
    }

    // Watch for changes in the URL hash
    $(window).on('hashchange', function(e) {
      parse_hash();
    });

    // Display tweets
    if(!parse_hash()) {
      display_tweets({ q: "", page: 0, count: 20 });
    }
  })
})
