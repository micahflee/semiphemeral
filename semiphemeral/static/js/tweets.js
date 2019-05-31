function change_state(q, page, count) {
  var new_state = { q:q, page:page, count:count };
  window.location = '#'+JSON.stringify(new_state);
}

function display_tweets() {
  var q = window.semiphemeral.state.q;
  var page = window.semiphemeral.state.page;
  var count = window.semiphemeral.state.count;

  var ids;
  if(q == "") {
    ids = window.semiphemeral.ids;
  } else {
    ids = [];
    for(var i=0; i<window.semiphemeral.ids.length; i++) {
      var id = window.semiphemeral.ids[i];
      if(window.semiphemeral.tweets[id].includes(q)) {
        ids.push(id);
      }
    }
  }

  console.log('display_tweets', window.semiphemeral);

  // Empty what previous page
  $('.info').empty();
  $('.tweets-to-delete').empty();
  $('.pagination').empty();

  // Display info
  var num_pages = Math.ceil(ids.length / count);
  var info_string = 'Page '+comma_formatted(page)+' of '+comma_formatted(num_pages)+' - ';
  if(ids.length != window.semiphemeral.ids.length) {
      info_string += 'filtering to '+comma_formatted(ids.length)+' tweets - '
  }
  info_string += comma_formatted(window.semiphemeral.ids.length)+' tweets are staged for deletion';
  $('.info').append($('<div/>').html(info_string));

  // Pagination controls
  function add_pagination_item(text, new_page) {
    var $item = $('<span/>').addClass('pagination-item');
    if(new_page == page) {
      $item.addClass('pagination-item-current').text(text);
    } else {
      var new_state = { q:q, page:new_page, count:count };
      var $link = $('<a/>').attr('href', '#'+JSON.stringify(new_state)).text(text);
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
        window.semiphemeral.state = JSON.parse(hash);
        $('.filter input').val(window.semiphemeral.state.q);
      } catch {
        console.log('parsing hash failed', hash);
        return false;
      }

      display_tweets();
      return true;
    }

    // Watch for changes in the URL hash
    $(window).on('hashchange', function(e) {
      parse_hash();
    });

    // Filter search results
    $('.filter input').change(function(){
      var q = $(this).val();
      console.log('filtering on', q);
      change_state(q, window.semiphemeral.state.page, window.semiphemeral.state.count);
    });

    // Display tweets
    if(!parse_hash()) {
      change_state("", 0, 50);
    }
  })
})
