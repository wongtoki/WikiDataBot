// INTERACTIVE FORMS //
// POST form recalculate_user events

var loading_time = "<div class='alert alert-warning alert-dismissible'><strong>Please be patient.</strong>" +
            " It might take some time to gather the answer. <button type='button' class='close' data-dismiss='alert'>&times;</button></div>";

var db_error = "<div class='alert alert-danger alert-dismissible'><strong>Our bad!</strong>" +
            " We have encountered an error, please try again. <button type='button' class='close' data-dismiss='alert'>&times;</button></div>";

var empty_form = "<div class='alert alert-warning alert-dismissible'><strong>Oops!</strong>" +
            " Please fill in the form fields using only words and digits. <button type='button' class='close' data-dismiss='alert'>&times;</button></div>";

var no_results = "<div class='alert alert-info alert-dismissible'><strong>Oops!</strong>" +
                        " There are no results to show. <button type='button' class='close' data-dismiss='alert'>&times;</button></div>";


// Loading and unloading spinner
function loading(dialog_id, input_field, submit_btn) {
    $(dialog_id).find(".spinner-border").show();
    $(input_field).prop('disabled', true);
    $(submit_btn).prop('disabled', true);
}
function done(dialog_id, input_field, submit_btn) {
    $(dialog_id).find(".spinner-border").hide();
    $(input_field).prop('disabled', false);
    $(submit_btn).prop('disabled', false);
}


// dropdown_select movie name options
$( document ).on('click', '#submit_movie_select', function(event){
    // use HTML5 form-validation check
    if($('#movie_select')[0].checkValidity()) {
        event.preventDefault();
        // show spinner loading icon
        loading('#qa_dialog', '#selected_movie', '#submit_movie_select');
        // console.log('prevented');
        $('#qa_response').html('');

        // convert the answer string to a JS array
        var answer_string = $('#post_selected_movie').val();
        var answer_list = answer_string.split("|");

        // Ajax call;
        var url_id = $('#movie_select').prop('action');
        var method_id = $('#movie_select').prop('method');
        var data_items = {
            post_entity: answer_list,
            post_entity_title: $('#post_selected_movie option:selected').text(),
            post_entity_link: $('#post_selected_movie option:selected').attr('link'),
            post_entity_string: $('#post_selected_movie option:selected').attr('string'),
        };
        form_response(url_id, method_id, data_items);

    }
    else {
        $('#qa_response').html(empty_form);
    }

} );


// normal dialog user input field where user can type
$('#submit_qa_query').click(function(event){
    // use HTML5 form-validation check
    if($('#qa_query')[0].checkValidity()) {
        event.preventDefault();
        // show spinner loading icon
        loading('#qa_dialog', '#post-search-query', '#submit_qa_query');

        // show response during loading
        $('#qa_response').html(loading_time);

        // items for AJAX call
        var url_id = $('#qa_query').prop('action');
        var method_id = $('#qa_query').prop('method');
        var data_items = {
            post_search: $('#post-search-query').val(),
        };
        // AJAX call
        form_response(url_id, method_id, data_items);
    }
    else {
        $('#qa_response').html(empty_form);
    }
});


// Send AJAX response to Django backend
function form_response(url_id, method_id, data_items) {
    const error_id = '#qa_response';
    const dialog_id = '#qa_dialog';

    // Inner Ajax function
    $.ajax({
        url: url_id,
        type: method_id,
        dataType: 'json',
        data : data_items,
        success: function( data ){
            if ( !$.trim( data.response )) {console.log("empty response..");
                $(error_id).html(no_results);
            }
            else {console.log("succes!");
                // remove the form
                $('#qa_dialog form:last').remove();
                // show response
                $(dialog_id).append(data.response);

                // change placeholder of input button
                $('#post-search-query').attr("placeholder", "Interact with the bot");

                var form = document.getElementById("movie_select");
                // disable question box if form returned
                if ( form ) {
                    $('#qa_dialog').find(".spinner-border").hide();
                    $('#post-search-query').prop('disabled', true);
                    $('#submit_qa_query').prop('disabled', true);
                }
                else {
                    // hide spinner loading icon
                    done('#qa_dialog', '#post-search-query', '#submit_qa_query');
                }

                // Scrolling to bottom of question-answering div
                var objDiv = document.getElementById("qa_dialog");
                objDiv.scrollTop = objDiv.scrollHeight;
                // empty the form field
                $('#post-search-query').val('');
            }
        },
        error : function(xhr) {console.log("error. see details below.");
            console.log(xhr.status + ": " + xhr.responseText);
            $(error_id).html(db_error);
        },
    }).done(function() {
        // Run code after AJAX call is done
        console.log("AJAX call is done");
        $(error_id).html('');
    });
}

// CSRF token
$(function() {
    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});