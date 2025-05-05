// Initialize wishlist count from sessionStorage (for initial display)
let wishlist = JSON.parse(sessionStorage.getItem('wishlist')) || [];

// Update wishlist count display
function updateWishlistCount(count) {
    const wishlistBadge = document.getElementById('wishlist-count');
    if (wishlistBadge) {
        wishlistBadge.textContent = count > 0 ? count : '';
        wishlistBadge.classList.toggle('hidden', count === 0);
    }
}

// Fetch initial wishlist count from server
fetch('/add-to-wishlist/', {
    method: 'GET',
    headers: {
        'X-Requested-With': 'XMLHttpRequest',
    },
})
.then(response => response.json())
.then(data => {
    updateWishlistCount(data.wishlist_count || 0);
})
.catch(error => console.error('Error fetching wishlist count:', error));

// Add product to wishlist via AJAX
function addToWishlist(productId) {
    fetch('/add-to-wishlist/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: `product_id=${productId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' || data.status === 'info') {
            // Removed alert(data.message)
            fetchWishlistCount();
        } else {
            // Removed alert(data.message || ...)
            console.error(data.message || 'An error occurred while adding to wishlist.');
        }
    })
    .catch(error => {
        console.error('Error adding to wishlist:', error);
        // Removed alert('Failed to add to wishlist...')
    });
}

// Remove product from wishlist via AJAX
function removeFromWishlist(productId) {
    fetch('/remove-from-wishlist/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: `product_id=${productId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Remove the item from the DOM without alert
            const item = document.querySelector(`li[data-product-id="${productId}"]`);
            if (item) item.remove();
            // Update wishlist count
            fetchWishlistCount();
        } else if (data.status === 'info') {
            // Optionally handle if item wasn't in wishlist
            console.log(data.message);
        } else {
            console.error(data.message || 'An error occurred while removing from wishlist.');
        }
    })
    .catch(error => {
        console.error('Error removing from wishlist:', error);
    });
}

// Fetch updated wishlist count from server
function fetchWishlistCount() {
    fetch('/add-to-wishlist/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        updateWishlistCount(data.wishlist_count || 0);
    })
    .catch(error => console.error('Error fetching wishlist count:', error));
}

// Link to wishlist or cart page
document.addEventListener('click', (e) => {
    if (e.target.id === 'view-wishlist') {
        window.location.href = '/wishlist/';
    } else if (e.target.id === 'wishlist-to-cart') {
        window.location.href = '/view-cart/';
    }
});

// Get CSRF token for POST requests
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

// Expose functions for global use
window.addToWishlist = addToWishlist;
window.removeFromWishlist = removeFromWishlist;