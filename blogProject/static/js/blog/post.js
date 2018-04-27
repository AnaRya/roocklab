$(function() {
  var savePost = function (event) {
    var form = $(this);
    $.ajax({
      url: form.attr('data-url'),
      data: form.serialize(),
      type: form.attr('method'),
      dataType: 'json',
      beforeSend: function() {
        $('#post-text').val('');
        alert("Function beforeSend");
      },
      success: function (data) {
        $('#post-text')[0].value ='';
        if (data.form_is_valid) {
          event.preventDefault();
          $('#post-text').val('');
          alert("Post created!");
        }
        else {
          alert("Sorry!");
        }
      },
    });
  return false
};

$(".js-create-post-form").submit(savePost);

});
