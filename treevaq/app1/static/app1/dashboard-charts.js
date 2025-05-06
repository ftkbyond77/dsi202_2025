// Products Per Seller Chart
const productsPerSellerCtx = document.getElementById('productsPerSellerChart').getContext('2d');
const productsPerSellerData = {
    labels: JSON.parse(document.getElementById('productsPerSellerData').textContent),
    datasets: [{
        label: 'Number of Products',
        data: JSON.parse(document.getElementById('productsPerSellerValues').textContent),
        backgroundColor: 'rgba(75, 192, 192, 0.6)', // Teal with opacity
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
    }]
};
const productsPerSellerChart = new Chart(productsPerSellerCtx, {
    type: 'bar',
    data: productsPerSellerData,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Number of Products'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Sellers'
                }
            }
        },
        plugins: {
            legend: {
                display: true
            }
        },
        responsive: true,
        maintainAspectRatio: false
    }
});

// Top Products by Revenue Chart
const topProductsCtx = document.getElementById('topProductsChart').getContext('2d');
const topProductsData = {
    labels: JSON.parse(document.getElementById('topProductsLabels').textContent),
    datasets: [{
        label: 'Revenue ($)',
        data: JSON.parse(document.getElementById('topProductsValues').textContent),
        backgroundColor: 'rgba(255, 99, 132, 0.6)', // Pink with opacity
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
    }]
};
const topProductsChart = new Chart(topProductsCtx, {
    type: 'bar',
    data: topProductsData,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Revenue ($)'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Products'
                }
            }
        },
        plugins: {
            legend: {
                display: true
            }
        },
        responsive: true,
        maintainAspectRatio: false
    }
});

// Orders and Revenue Over Time Line Chart
const ordersRevenueCtx = document.getElementById('ordersRevenueChart').getContext('2d');
const ordersRevenueData = {
    labels: JSON.parse(document.getElementById('ordersRevenueLabels').textContent),
    datasets: [
        {
            label: 'Orders',
            data: JSON.parse(document.getElementById('ordersData').textContent),
            borderColor: '#38a169', // Green (matches text-green-600)
            backgroundColor: 'rgba(56, 161, 105, 0.1)', // Light green fill
            borderWidth: 2,
            fill: true,
            tension: 0.4 // Smooth curve
        },
        {
            label: 'Revenue ($)',
            data: JSON.parse(document.getElementById('revenueData').textContent),
            borderColor: '#68d391', // Lighter green (matches text-green-500)
            backgroundColor: 'rgba(104, 211, 145, 0.1)', // Light green fill
            borderWidth: 2,
            fill: true,
            tension: 0.4 // Smooth curve
        }
    ]
};
const ordersRevenueChart = new Chart(ordersRevenueCtx, {
    type: 'line',
    data: ordersRevenueData,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Values'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Months'
                }
            }
        },
        plugins: {
            legend: {
                display: true
            }
        },
        responsive: true,
        maintainAspectRatio: false
    }
});

// Adjust chart colors for Dark Mode
function updateChartColors() {
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#e2e8f0' : '#2d3748';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Update Products Per Seller Chart
    productsPerSellerChart.options.scales.y.grid.color = gridColor;
    productsPerSellerChart.options.scales.x.grid.color = gridColor;
    productsPerSellerChart.options.scales.y.title.color = textColor;
    productsPerSellerChart.options.scales.x.title.color = textColor;
    productsPerSellerChart.options.scales.y.ticks.color = textColor;
    productsPerSellerChart.options.scales.x.ticks.color = textColor;
    productsPerSellerChart.options.plugins.legend.labels.color = textColor;
    productsPerSellerChart.update();

    // Update Top Products Chart
    topProductsChart.options.scales.y.grid.color = gridColor;
    topProductsChart.options.scales.x.grid.color = gridColor;
    topProductsChart.options.scales.y.title.color = textColor;
    topProductsChart.options.scales.x.title.color = textColor;
    topProductsChart.options.scales.y.ticks.color = textColor;
    topProductsChart.options.scales.x.ticks.color = textColor;
    topProductsChart.options.plugins.legend.labels.color = textColor;
    topProductsChart.update();

    // Update Orders and Revenue Chart
    ordersRevenueChart.options.scales.y.grid.color = gridColor;
    ordersRevenueChart.options.scales.x.grid.color = gridColor;
    ordersRevenueChart.options.scales.y.title.color = textColor;
    ordersRevenueChart.options.scales.x.title.color = textColor;
    ordersRevenueChart.options.scales.y.ticks.color = textColor;
    ordersRevenueChart.options.scales.x.ticks.color = textColor;
    ordersRevenueChart.options.plugins.legend.labels.color = textColor;
    ordersRevenueChart.update();
}

// Initial color update
updateChartColors();

// Listen for Dark Mode changes
document.getElementById('dark-mode-toggle').addEventListener('click', updateChartColors);