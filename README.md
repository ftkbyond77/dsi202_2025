### Treevaq - Revolutionizing Sustainable E-Commerce Platform

Welcome to Treevaq, an innovative e-commerce platform designed to promote sustainable shopping. Built with Django and Django REST Framework, Treevaq allows users to browse and purchase eco-friendly products, track their carbon footprint savings, and manage their shopping experience through an intuitive dashboard. This project emphasizes environmental consciousness, offering a seamless blend of functionality and green living.

Treevaq isn’t just an e-commerce platform—it’s a powerful tool for positive environmental and social impact. By connecting consumers with verified eco-friendly products, Treevaq makes it easier than ever to shop with purpose. Every purchase through the platform contributes to reducing plastic waste, lowering carbon emissions, and supporting ethical producers around the world.

For individuals, Treevaq offers a clear, data-driven view of their environmental impact, helping users make informed decisions and track their personal contributions toward a greener future. Whether it's switching to zero-waste products or supporting local sustainable businesses, users are empowered to take meaningful action—without sacrificing convenience or quality.

On a global scale, Treevaq supports a circular economy, encourages responsible consumption, and fosters a growing community of conscious consumers. By scaling sustainable choices, Treevaq plays a vital role in addressing urgent climate challenges and building a healthier, more resilient planet for future generations.

## 3.1 Abstract

Treevaq is a web-based application that revolutionizes online shopping by prioritizing sustainability. It enables users to explore a curated selection of eco-friendly products, add them to a cart, and complete purchases while tracking the environmental impact of their choices. The platform includes a dashboard for administrators to monitor sales, user activity, and carbon savings, alongside a blog featuring educational content on sustainable living. Leveraging Django’s robust framework and RESTful APIs, Treevaq offers a scalable solution for eco-conscious consumers and sellers, fostering a community dedicated to reducing carbon footprints.

## 3.2 User Stories (at least 3 usage scenarios)

- **As a Shopper**, I want to browse and purchase sustainable products so that I can contribute to environmental conservation. I need to view product details, add items to my cart, and check out securely.
- **As an Administrator**, I want to monitor sales and user activity through a dashboard so that I can manage the platform effectively. I need to see total products, orders, revenue, and user statistics in real-time.
- **As a Content Creator**, I want to publish blog articles about sustainability so that I can educate users and promote eco-friendly practices. I need to add articles with images and details via the admin panel for public viewing.

## 3.3 Usage Procedures Based on User Stories

### For Shoppers

1. Visit the homepage (`/`) and log in with your credentials.
2. Navigate to the "Products" page (`/products/`) to browse available items.
3. Click on a product to view details, then click "Add to Cart" to include it in your shopping cart.
4. Go to the "Cart" page (`/cart/`) to review your items, then proceed to "Checkout" (`/checkout/`) to complete the purchase.
5. Log out after shopping to secure your session.

### For Administrators

1. Log in with admin credentials (e.g., via `/admin/` or the dashboard).
2. Access the "Dashboard" (`/dashboard/`) to view key metrics such as total products, sustainable products, total orders, revenue, and carbon savings.
3. Use the "User Management" section to edit or deactivate users as needed.
4. Monitor recent orders and top-selling products to make informed business decisions.

### For Content Creators

1. Log in with admin or authorized user credentials.
2. Navigate to the Django admin panel (`/admin/`) and select the "Blog" section.
3. Click "Add Blog" to create a new article, entering a title, summary, full content, author, and uploading an image.
4. Save the article and visit the "Blog" page (`/blog/`) to ensure it appears with the image and details.
5. Click "Read Full Article" to verify the detailed view (`/blog/<id>/`) displays correctly.

## 3.4 Installation and Usage Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Installation Steps (Docker-Based)

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/ftkbyond77/dsi202
   cd treevaq
   ```

2. **Build and Start the Application**:

   ```bash
   docker-compose up --build
   ```

3. **Create a Superuser**:

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Docker Stop**:

    ```bash
   docker-compose down
   ```

### Usage Instructions

- **Access the Application**: Open your browser and go to `http://localhost:8000/`.
- **Log In**: Use the superuser credentials or create additional users via the admin panel (`/admin/`).
- **Explore Features**: Navigate to `/products/` for shopping, `/dashboard/` for admin tasks, and `/blog/` for articles.
- **Admin Management**: Log into `/admin/` to add products, users, or blog posts.
- **API Access**: Use `/api/products/` to interact with the product list via the REST API (requires authentication for write operations).

### Additional Notes

- Ensure proper media configuration in `settings.py` (`MEDIA_URL` and `MEDIA_ROOT`) if uploading images.
- Customize templates or models in `app1/` as needed for your specific requirements.
- Refer to Django and DRF documentation for advanced customization.

This README provides a comprehensive guide to get started with Treevaq, supporting its sustainable e-commerce vision.