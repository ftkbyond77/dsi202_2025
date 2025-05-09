// Create a new file: app1/static/app1/community.js

// CSRF token setup for Ajax requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function Community() {
  const [posts, setPosts] = React.useState([]);
  // ... state อื่นๆ คงเดิม

  React.useEffect(() => {
    fetch('/api/community/posts/')
      .then(response => response.json())
      .then(data => {
        console.log('Posts fetched:', data);
        setPosts(data);
      })
      .catch(error => console.error('Error fetching posts:', error));
  }, []);

  // ... คงโค้ดอื่นๆ ไว้
}

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the community page
    if (document.getElementById('community-root')) {
        console.log('Community page loaded');
        
        // This could be used to add any non-React functionality
        // For example, analytics tracking or interactions with other parts of the page
        
        // Example of how to interact with the React app from outside
        window.shareToExternal = function(postId, platform) {
            // You could implement sharing to different platforms here
            const postTitle = document.querySelector(`[data-post-id="${postId}"] h2`).textContent;
            const shareUrl = window.location.origin + '/community/post/' + postId;
            
            let shareWindow;
            
            switch(platform) {
                case 'facebook':
                    shareWindow = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
                    break;
                case 'twitter':
                    shareWindow = `https://twitter.com/intent/tweet?text=${encodeURIComponent(postTitle)}&url=${encodeURIComponent(shareUrl)}`;
                    break;
                default:
                    console.error('Unknown sharing platform');
                    return;
            }
            
            window.open(shareWindow, '_blank', 'width=600,height=400');
        };
        
        // In a real implementation, you would set up Ajax endpoints for the community features
        // For example:
        
        /*
        // Like a post
        function likePost(postId) {
            fetch('/api/community/like/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ post_id: postId })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                // Update the UI with the new like count
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        
        // Add a comment
        function addComment(postId, commentText) {
            fetch('/api/community/comment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    post_id: postId,
                    comment: commentText
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Comment added:', data);
                // Update the UI with the new comment
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        */
    }
});