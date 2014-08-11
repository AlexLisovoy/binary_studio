$(function() {

    var ul = $('ul');

    $('#drop a').click(function() {
        // Simulate a click on the file input button
        // to show the file browser dialog
        $(this).parent().find('input').click();
    });

    // Initialize the jQuery File Upload plugin
    $('#upload').fileupload({

        // This element will accept file drag/drop uploading
        dropZone: $('#drop'),

        // This function is called when a file is added to the queue;
        // either via the browse button, or via drag/drop:
        add: function(e, data) {

            var tpl = $(
                    '<li class="uploading">' +
                    '<input type="text" value="0" data-width="48" data-height="48" data-fgColor="#0788a5" data-readOnly="1" data-bgColor="#3e4043" />' +
                    '<p></p>' +
                    '<span><i class="fa fa-times"></i></span>' +
                    '</li>'
            );

            // Append the file name and file size
            tpl.find('p').text(data.files[0].name)
                .append('<em>' + formatFileSize(data.files[0].size) + '</em>');

            // Add the HTML to the UL element
            data.context = tpl.prependTo(ul);

            // Initialize the knob plugin
            tpl.find('input').knob();

            // Listen for clicks on the cancel icon
            tpl.find('span').click(function() {

                if (tpl.hasClass('uploading')) {
                    jqXHR.abort();
                }
                tpl.remove();
            });
            // Automatically upload the file once it is added to the queue
            var jqXHR = data.submit();
        },

        progress: function(e, data) {

            // Calculate the completion percentage of the upload
            var progress = parseInt(data.loaded / data.total * 100, 10);

            // Update the hidden input field and trigger a change
            // so that the jQuery knob plugin knows to update the dial
            data.context.find('input').val(progress).change();

            if (progress == 100) {
                data.context.removeClass('uploading');
            }
        },

        done: function(e, data) {
            data.context.addClass('file-download');
            var number = $('li').length,
                tpl = $('<div class="formats">' +
                    '<input type="radio" name="format' + number + '" value="json" checked><label for="json">json</label>' +
                    '<input type="radio" name="format' + number + '" value="xml"><label for="xml">xml</label>' +
                    '<input type="radio" name="format' + number + '" value="csv"><label for="csv">csv</label>' +
                    '</div>' +
                    '<a class="btn download" href="' + data.result.access_url + '">' +
                    '<i class="fa fa-download"></i></a>');

            data.context.find('span').after(tpl);
            data.context.find('a.download').click(function(e) {
                e.preventDefault();

                // remove error message
                $(e.target).parents('.file-download').find('.error-message').remove();

                $.ajax({
                    url: e.target.href || e.target.parentElement.href,
                    data: {
                        format: $(e.target).parents('.file-download').find('.formats input:checked').val()
                    },
                    success: function(data) {
                        if(data.status){
                            downloadFile(data.url, data.filename);
                        }else{
                            $(e.target).parents('.file-download').append('<div class="error-message">' + data.error + '</div>');
                        }
                    }
                })
            });

        },

        fail: function(e, data) {
            // Something has gone wrong!
            data.context.addClass('upload-failed');

            var message = JSON.parse(data.jqXHR.responseText).errors.the_file[0];

            data.context.find('p').append('<b>' + message + '</b>');
        }

    });

    // Prevent the default action when a file is dropped on the window
    $(document).on('drop dragover', function(e) {
        e.preventDefault();
    });

    // Force download file
    function downloadFile(url, name) {

        //Creating new link node.
        var link = document.createElement('a');
        link.href = url;

        if (link.download !== undefined) {
            //Set HTML5 download attribute. This will prevent file from opening if supported.
            link.download = name;
        }

        //Dispatching click event.
        var e = document.createEvent('MouseEvents');
        e.initEvent('click', true, true);
        link.dispatchEvent(e);
        return true;
    }


    // Helper function that formats the file sizes
    function formatFileSize(bytes) {
        if (typeof bytes !== 'number') {
            return '';
        }

        if (bytes >= 1000000000) {
            return (bytes / 1000000000).toFixed(2) + ' GB';
        }

        if (bytes >= 1000000) {
            return (bytes / 1000000).toFixed(2) + ' MB';
        }

        return (bytes / 1000).toFixed(2) + ' KB';
    }

    // get cookie using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for(var i = 0; i < cookies.length; i++) {
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

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

});