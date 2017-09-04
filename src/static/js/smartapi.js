function check_user(){
    $.ajax({url: "/user", success: function(result){
        var html = "";
        var side_html = "";
        if (result.login){
            side_html = '<a href="/logout?next=' + window.location.pathname + '">Logout</a>';
            if (result.avatar_url){
                html += '<img class="avatar tooltipped" src="' + result.avatar_url +
                        '" alt="avatar" data-tooltip="' + result.name + '" />';
          }
          html += '<a style="display: inline-block;" href="/logout?next=' + window.location.pathname + '">Logout</a>';
        }else{
            html += '<a href="/login">Login</a>';
            side_html = html;
        }
        $("#user_link").html(html).promise().done(function(){
            $('.tooltipped').tooltip();
        });
        $("#side_user_link").html(side_html);
    }});
};


/* for reg_form.html */
function save_api(form, overwrite){
    $("#submit_mask").modal("open");
    var data = $(form).serialize();
    if (overwrite){
      data += "&overwrite=true";
    }
    $.ajax({
        url: "/api",
        type: "post",
        data: data,
        success: function(response) {
            $("#submit_mask").modal("close");
            console.log(response);
            if (response.success){
                var msg = 'API metadata saved!';
                if (response.dryrun){
                  msg += ' <p class="blue-text text-darken-2">Well, not really, because this is a dryrun.';
                  msg += ' If you do want to register your API, uncheck "dry run" and try again. </p>';
                }
                swal('Good job!', msg, 'success');
            }
            else{
              if (response.error.indexOf("API exists") != -1){
                  swal({
                      title: 'API exists. Overwrite?',
                      text: "You won't be able to revert this!",
                      type: 'warning',
                      showCancelButton: true,
                      confirmButtonColor: '#3085d6',
                      cancelButtonColor: '#d33',
                      confirmButtonText: 'Yes, Overwrite it!'
                  }).then(function() {
                      save_api(form, true);
                  }, function(){});
              }
              else{
                  swal(
                      response.valid==false?'ValidationError':'Error',
                      response.error,
                      'error'
                  );
              }
            }
        }
    });
};

function initialize_form() {
    // initialize API registration form
    $('#apireg_form').validate({
        rules: {
            url: {
                required: true
            }
        },
        submitHandler: function(form){
            save_api(form);
        }
    });
};


$(function(){
    // Initialize collapse button
    $('.button-collapse').sideNav({
          menuWidth: 240, // Default is 240
          edge: 'left', // Choose the horizontal origin
          closeOnClick: true // Closes side-nav on <a> clicks, useful for Angular/Meteor
        }
      );

    // Initialize dropdown button
    $(".dropdown-button").dropdown();
    // Initialize modal
    $('.modal').modal({dismissible: false});
    // Check user status
    check_user();

    // for reg_form.html
    initialize_form();
  });
