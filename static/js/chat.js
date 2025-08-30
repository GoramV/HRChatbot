// JavaScript for HR Chatbot

$(document).ready(function() {
    // Function to scroll to bottom of chat
    function scrollToBottom() {
        const chatContainer = $('#chatContainer');
        if (chatContainer.length) {
            chatContainer.scrollTop(chatContainer[0].scrollHeight);
        }
    }
    
    // Scroll to bottom on page load
    scrollToBottom();

    // Handle chat form submission via AJAX
    $('#chatForm').submit(function(e) {
        e.preventDefault();
        
        const form = $(this);
        const url = form.attr('action');
        const formData = form.serialize();
        const submitButton = form.find('button[type="submit"]');
        const inputField = form.find('input[name="content"]');
        
        // Don't submit empty messages
        if (inputField.val().trim() === '') {
            return false;
        }
        
        // Disable button and input during submission
        submitButton.prop('disabled', true);
        inputField.prop('disabled', true);
        
        // Send message to server
        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            dataType: 'json',
            success: function(data) {
                if (data.status === 'success') {
                    // Add user message
                    const userMessageHTML = `
                        <div class="message user-message">
                            ${data.user_message.content}
                            <div class="message-time">${data.user_message.timestamp}</div>
                        </div>
                    `;
                    $('#chatContainer').append(userMessageHTML);
                    
                    // Add bot message
                    const botMessageHTML = `
                        <div class="message bot-message">
                            ${data.bot_message.content}
                            <div class="message-time">${data.bot_message.timestamp}</div>
                        </div>
                    `;
                    $('#chatContainer').append(botMessageHTML);
                    
                    // Clear input field
                    inputField.val('');
                    
                    // Scroll to bottom
                    scrollToBottom();
                } else {
                    console.error('Error:', data.errors);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                // Show error message
                const errorMessageHTML = `
                    <div class="message bot-message">
                        Sorry, there was an error processing your request. Please try again.
                        <div class="message-time">${new Date().toLocaleTimeString('en-US', {hour: '2-digit', minute:'2-digit', hour12: false})}</div>
                    </div>
                `;
                $('#chatContainer').append(errorMessageHTML);
            },
            complete: function() {
                // Re-enable button and input
                submitButton.prop('disabled', false);
                inputField.prop('disabled', false);
                inputField.focus();
            }
        });
    });

    // No duplicate function needed
});