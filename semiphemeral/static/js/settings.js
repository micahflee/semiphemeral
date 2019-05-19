$(function(){
  function update_ui() {
    if($('.delete-tweets-checkbox').prop('checked')) {
      $('.delete-tweets-fieldset').show();
    } else {
      $('.delete-tweets-fieldset').hide();
    }

    if($('.retweets-likes-checkbox').prop('checked')) {
      $('.retweets-likes-fieldset').show();
    } else {
      $('.retweets-likes-fieldset').hide();
    }
  }

  $('.delete-tweets-checkbox').change(update_ui);
  $('.retweets-likes-checkbox').change(update_ui);
  update_ui();
})
