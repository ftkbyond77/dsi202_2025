// app1/static/app1/community.js

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

// Main Community Component
function CommunityApp() {
    const [posts, setPosts] = React.useState([]);
    const [categories, setCategories] = React.useState([]);
    const [selectedCategory, setSelectedCategory] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    // Fetch posts and categories on component mount
    React.useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch categories first
                const categoriesResponse = await fetch('/api/categories/');
                if (!categoriesResponse.ok) throw new Error('Failed to load categories');
                const categoriesData = await categoriesResponse.json();
                setCategories(categoriesData);

                // Then fetch posts
                const postsResponse = await fetch('/api/community/posts/');
                if (!postsResponse.ok) throw new Error('Failed to load posts');
                const postsData = await postsResponse.json();
                setPosts(postsData);

            } catch (err) {
                console.error('Error:', err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, []);

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        // Validate category selection
        if (!selectedCategory) {
            alert('กรุณาเลือกหมวดหมู่');
            return;
        }

        try {
            const response = await fetch('/api/community/posts/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Failed to create post');

            // Add new post to the list
            setPosts([data, ...posts]);
            e.target.reset(); // Reset form
            alert('โพสต์สำเร็จ!');

        } catch (err) {
            console.error('Error:', err);
            alert('เกิดข้อผิดพลาด: ' + err.message);
        }
    };

    if (isLoading) return <div>กำลังโหลด...</div>;
    if (error) return <div>เกิดข้อผิดพลาด: {error}</div>;

    return (
        <div className="community-container">
            <h1>ชุมชน</h1>
            
            {/* Post Form */}
            <form onSubmit={handleSubmit} className="post-form">
                <div className="form-group">
                    <label htmlFor="title">หัวข้อ</label>
                    <input type="text" id="title" name="title" required />
                </div>
                
                <div className="form-group">
                    <label htmlFor="content">เนื้อหา</label>
                    <textarea id="content" name="content" required></textarea>
                </div>
                
                <div className="form-group">
                    <label htmlFor="category">หมวดหมู่</label>
                    <select 
                        id="category" 
                        name="category" 
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                        required
                    >
                        <option value="">-- กรุณาเลือกหมวดหมู่ --</option>
                        {categories.map(category => (
                            <option key={category.id} value={category.name}>
                                {category.name}
                            </option>
                        ))}
                    </select>
                </div>
                
                <div className="form-group">
                    <label htmlFor="image">รูปภาพ (ไม่บังคับ)</label>
                    <input type="file" id="image" name="image" accept="image/*" />
                </div>
                
                <button type="submit" className="submit-btn">โพสต์</button>
            </form>

            {/* Posts List */}
            <div className="posts-list">
                {posts.map(post => (
                    <div key={post.id} className="post-card">
                        <h2>{post.title}</h2>
                        <p className="post-meta">
                            โดย {post.username} • {post.timestamp} • {post.category}
                        </p>
                        <p className="post-content">{post.content}</p>
                        {post.image && (
                            <img src={post.image} alt={post.title} className="post-image" />
                        )}
                        <div className="post-actions">
                            <span>❤️ {post.likes}</span>
                            <span>💬 {post.comments}</span>
                            <button onClick={() => sharePost(post.id)}>แชร์</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const communityRoot = document.getElementById('community-root');
    if (communityRoot) {
        ReactDOM.render(<CommunityApp />, communityRoot);
    }
});

// Helper function for sharing posts
function sharePost(postId) {
    const postTitle = document.querySelector(`[data-post-id="${postId}"] h2`)?.textContent || 'โพสต์ชุมชน';
    const shareUrl = `${window.location.origin}/community/post/${postId}`;
    
    const shareWindow = window.open('', '_blank', 'width=600,height=400');
    shareWindow.location.href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(postTitle)}`;
}