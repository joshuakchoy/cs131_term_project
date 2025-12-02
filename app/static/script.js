const sidebar = document.querySelector('.sidebar');
const sidebarToggler = document.querySelector('.toggler');

if (sidebarToggler) {
    sidebarToggler.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}
