function check_user(){
    $.ajax({url: "/user", success: function(result){
        var html = "";
        var side_html = "";
        if (result.login){
            // side_html = '<li><a href="/logout?next=' + window.location.pathname + '">Logout</a></li>';
            if (result.avatar_url){
              $('#navPhoto').attr("src", result.avatar_url);
              html += "<li><a class='tooltipped' data-tooltip='My Dashboard' id='navPhotoLink' href='/dashboard'><img id='navPhoto' class='circle responsive-img' src='"+result.avatar_url+"' alt='user photo'></a></li>";
          }
          html += "<li><a class='btn red' href='/logout?next=" + window.location.pathname + "'>Logout</a></li>";
          side_html += "<li><a class='blue-text' href='/dashboard'>My Dashboard</a></li><li><a class='red-text' href='/logout?next=" + window.location.pathname + "'>Logout</a></li>";
        }else{
            html += "<li><a class='btn green' href='/oauth'>Login</a></li>";
            side_html += html;
        }
        // Append new items to navigation
        $("#user_link").append(html).promise().done(function(){
            $('.tooltipped').tooltip();
            $(".dropdown-button").dropdown();
        });
        $("#side_user_link").append(side_html);
    }});
};


/* for reg_form.html */
function save_api(form, overwrite, savev2){
    $("#submit_mask").modal("open");
    var data = $(form).serialize();
    if (overwrite){
      data += "&overwrite=true";
    }
    if (savev2){
      data += "&save_v2=true";
    }
    $.ajax({
        url: "/api",
        type: "post",
        data: data,
        success: function(response) {
            $("#submit_mask").modal("close");
            //console.log(response);
            if (response.success){
                var msg = 'API metadata saved!';
                if (response.dryrun){
                  msg += ' <p class="blue-text text-darken-2">Well, not really, because this is a dryrun.';
                  msg += ' If you do want to register your API, uncheck "dry run" and try again. </p>';
                }
                swal('Good job!', msg, 'success');

            }
            else{
              if ( response.hasOwnProperty("swagger_v2") && response.swagger_v2 ){
                // -----------
                swal({
                    title: "Version 2 Detected",
                    text: "Only V3 will experience full functionality. Continue saving anyway?",
                    icon: "warning",
                    showCancelButton: true,
                    buttons: true,
                    dangerMode: true,
                    confirmButtonText: 'Yes, save it!'
                  })
                  .then((willSave) => {
                    if (willSave) {
                      save_api(form, true, true);
                      swal("Your data has been saved!", {
                        icon: "success",
                      });
                    } else {
                      swal("Your data has not been saved");
                    }
                  });
                // ----------
              }
              if (response.error.indexOf("API exists") != -1){
                  swal({
                      title: 'API exists. Overwrite?',
                      text: "You won't be able to revert this!",
                      type: 'warning',
                      showCancelButton: true,
                      confirmButtonColor: '#3085d6',
                      cancelButtonColor: '#d33',
                      confirmButtonText: 'Yes, overwrite it!'
                  }).then(function() {
                      save_api(form, true);
                  }, function(){});
              }
              else if( !response.hasOwnProperty("swagger_v2") ){
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

    $('#api_search_form').validate({
        rules:{
            query: {
                required: true
            }
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
    $('.modal').modal({dismissible: true});
    // Check user status
    check_user();

    // for reg_form.html
    initialize_form();
  });

  // Particles
