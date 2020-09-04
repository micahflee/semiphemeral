$(function () {
  function update_ui() {
    if ($('.log-to-file-checkbox').prop('checked')) {
      $('.log-to-file-fieldset').show();
    } else {
      $('.log-to-file-fieldset').hide();
    }

    if ($('.delete-tweets-checkbox').prop('checked')) {
      $('.delete-tweets-fieldset').show();
    } else {
      $('.delete-tweets-fieldset').hide();
    }

    if ($('.retweets-likes-checkbox').prop('checked')) {
      $('.retweets-likes-fieldset').show();
    } else {
      $('.retweets-likes-fieldset').hide();
    }

    if ($('.dms-checkbox').prop('checked')) {
      $('.dms-fieldset').show();
    } else {
      $('.dms-fieldset').hide();
    }

    if ($('.use-tor-checkbox').prop('checked')) {
      $('.proxy-text').val('socks5://localhost:9050').attr('readonly', 'readonly');
    } else{
      $('.proxy-text').removeAttr('readonly', 'false');
    }
  }

  $('.log-to-file-checkbox').change(update_ui);
  $('.delete-tweets-checkbox').change(update_ui);
  $('.retweets-likes-checkbox').change(update_ui);
  $('.use-tor-checkbox').change(update_ui);
  $('.dms-checkbox').change(update_ui);
  update_ui();
})
