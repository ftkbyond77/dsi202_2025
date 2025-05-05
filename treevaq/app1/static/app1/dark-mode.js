// Check if dark mode is preferred by the user (stored in localStorage)
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
let darkModeEnabled = localStorage.getItem('darkMode') === 'true' || (prefersDark.matches && localStorage.getItem('darkMode') === null);

// Apply dark mode class to body if enabled
document.body.classList.toggle('dark-mode', darkModeEnabled);

// Toggle dark mode when button is clicked
document.getElementById('dark-mode-toggle').addEventListener('click', function () {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
});

// Update toggle button text based on mode
function updateToggleText() {
    const toggleButton = document.getElementById('dark-mode-toggle');
    toggleButton.textContent = darkModeEnabled ? 'Light Mode' : 'Dark Mode';
}

// Initial toggle text update
updateToggleText();

// Sync with system preference changes
prefersDark.addEventListener('change', e => {
    if (localStorage.getItem('darkMode') === null) {
        darkModeEnabled = e.matches;
        document.body.classList.toggle('dark-mode', darkModeEnabled);
        updateToggleText();
    }
});