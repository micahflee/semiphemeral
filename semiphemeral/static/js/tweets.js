$(function(){

  function change_state(q, page, count, replies) {
    var new_state = { q:q, page:page, count:count, replies:replies };
    window.location = '#'+JSON.stringify(new_state);
  }

  function toggle_exclude(id, excluded) {
    function update_text(excluded) {
      if(excluded) {
        $('#toggle-exclude-label-'+id).addClass('excluded').text('Excluded from deletion');
      } else {
        $('#toggle-exclude-label-'+id).removeClass('excluded').text('Staged for deletion');
      }
    }

    // If excluded is the same as we already know, just update the text
    if(window.semiphemeral.tweets[id].excluded == excluded) {
      update_text(excluded);
      return;
    }

    // Otherwise make ajax request
    $('#toggle-exclude-label-'+id).removeClass('excluded').text('Saving...');
    var exclude_from_delete = (excluded ? 1 : 0);
    $.ajax('/api/exclude/'+id+'/'+exclude_from_delete, {
      method: 'POST',
      success: function() {
        // Update the tweets, and the text
        window.semiphemeral.tweets[id].excluded = excluded;
        update_text(excluded);
      },
      error: function() {
        alert('API error');
      }
    });
  }

  function display_tweets() {
    console.log('display_tweets', window.semiphemeral);

    var q = window.semiphemeral.state.q;
    var page = window.semiphemeral.state.page;
    var count = window.semiphemeral.state.count;
    var replies = window.semiphemeral.state.replies;

    // Build list of ids to filter
    var ids = [];
    for(var i=0; i<window.semiphemeral.ids.length; i++) {
      var id = window.semiphemeral.ids[i];
      if(window.semiphemeral.tweets[id].text.toLowerCase().includes(q.toLowerCase())) {
        if(replies || (!replies && !window.semiphemeral.tweets[id].is_reply)) {
            ids.push(id);
        }
      }
    }

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
      var $embed = $('<div/>').prop('id', 'tweet-'+ids[i]);
      var $info = $('<div/>').addClass('info')
        .append(
          $('<label/>')
            .append($('<input type="checkbox">')
              .prop('id', 'toggle-exclude-checkbox-'+ids[i])
              .data('tweet-id', ids[i])
              .change(function(){
                toggle_exclude($(this).data('tweet-id'), this.checked);
              }))
            .append($('<span/>').addClass('toggle-exclude-label').prop('id', 'toggle-exclude-label-'+ids[i]))
        )
        .append($('<div class="stats">'+window.semiphemeral.tweets[ids[i]].retweets+' retweets, '+window.semiphemeral.tweets[ids[i]].likes+' likes</div>'));

      var $tweet = $('<div/>').addClass('tweet').append($info).append($embed);

      $('.tweets-to-delete').append($tweet);

      // Set the text and checkbox initially
      toggle_exclude(ids[i], window.semiphemeral.tweets[ids[i]].excluded);
      if(window.semiphemeral.tweets[ids[i]].excluded) {
        $('#toggle-exclude-checkbox-'+ids[i]).prop('checked', true);
      }

      twttr.widgets.createTweet(ids[i], $('#tweet-'+ids[i])[0], {
        'dnt': true
      });
    }
  }

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
        $('.options input').prop('checked', window.semiphemeral.state.replies);
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
      if(q != window.semiphemeral.state.count) {
        change_state(q, 0, window.semiphemeral.state.count, window.semiphemeral.state.replies);
      }
    });

    // Toggling show replies
    $('.options input').change(function(){
      var replies = $('.options input').prop('checked') ? true : false;
      console.log('show replies', replies);
      if(replies != window.semiphemeral.state.replies) {
        change_state(window.semiphemeral.state.q, 0, window.semiphemeral.state.count, replies);
      }
    });

    // Display tweets
    if(!parse_hash()) {
      change_state("", 0, 50, true);
    }
  })
})
