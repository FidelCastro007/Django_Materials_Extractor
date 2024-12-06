setInterval(function() {
    $.ajax({
        url: '/api/get_processing_data/1/',  // Example URL
        method: 'GET',
        success: function(response) {
            $('#processing_status').text(response.status);
            $('#progress_bar').css('width', response.status_percent + '%');
        }
    });
}, 5000);  // Update every 5 seconds
