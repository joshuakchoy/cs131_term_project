const sidebar = document.querySelector('.sidebar');
const sidebarPart = document.querySelector('.sidebar-part');
const sidebarToggler = document.querySelector('.toggler');

// Restore saved state on load
document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('sidebarCollapsed');
  if (saved === 'true') {
    if (sidebar) sidebar.classList.add('collapsed');
    if (sidebarPart) sidebarPart.classList.add('collapsed');
  }
});

if (sidebarToggler) {
    sidebarToggler.addEventListener('click', () => {
        if (sidebar) sidebar.classList.toggle('collapsed');
        if (sidebarPart) sidebarPart.classList.toggle('collapsed');
        // persist state
        const collapsed = sidebar && sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', collapsed ? 'true' : 'false');
    });
}
