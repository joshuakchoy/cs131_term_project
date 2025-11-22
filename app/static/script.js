const sidebar = document.querySelector('.sidebar');
const sidebarToggler = document.querySelector('.toggler');
const layoutBar = document.querySelector('.sidebar-part')

// Disable transitions on load
layoutBar.classList.add('no-transition');

// Load sidebar state from localStorage on page load
if (localStorage.getItem('sidebarCollapsed') === 'true') {
    sidebar.classList.add('collapsed');
    layoutBar.classList.add('collapsed');
}

// Re-enable transitions after layout is set
setTimeout(() => {
    layoutBar.classList.remove('no-transition');
}, 10);

if (sidebarToggler) {
    sidebarToggler.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        layoutBar.classList.toggle('collapsed');
        
        // Save state to localStorage in case where switching pages
        //in collapsed form
        if (sidebar.classList.contains('collapsed')) {
            localStorage.setItem('sidebarCollapsed', 'true');
        } else {
            localStorage.setItem('sidebarCollapsed', 'false');
        }
    });
}
