$(function(){
  function update_ui() {
    if($('.delete-tweets-checkbox').prop('checked')) {
      $('.delete-tweets-fieldset').show();
    } else {
      $('.delete-tweets-fieldset').hide();
    }

    if($('.delete-dms-checkbox').prop('checked')) {
      $('.delete-dms-fieldset').show();
    } else {
      $('.delete-dms-fieldset').hide();
    }
  }

  $('.delete-tweets-checkbox').change(update_ui);
  $('.delete-dms-checkbox').change(update_ui);
  update_ui();
})
