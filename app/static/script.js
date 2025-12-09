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

// Floating Message Hub functionality
document.addEventListener('DOMContentLoaded', () => {
  const messageHubButton = document.getElementById('messageHubButton');
  const messageHubModal = document.getElementById('messageHubModal');
  const closeMessageHub = document.getElementById('closeMessageHub');
  
  if (messageHubButton && messageHubModal) {
    // Toggle modal on button click
    messageHubButton.addEventListener('click', () => {
      messageHubModal.classList.toggle('active');
    });
    
    // Close modal on close button click
    if (closeMessageHub) {
      closeMessageHub.addEventListener('click', () => {
        messageHubModal.classList.remove('active');
      });
    }
    
    // Close modal when clicking outside
    document.addEventListener('click', (e) => {
      if (!messageHubModal.contains(e.target) && !messageHubButton.contains(e.target)) {
        messageHubModal.classList.remove('active');
      }
    });
  }
});

// Modal helpers for teacher portal (moved from teacher_portal.html)
function openCourseModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "flex";
    }
}

function closeCourseModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "none";
    }
}

// Close modal when clicking outside the modal-content
window.addEventListener("click", function (event) {
    if (event.target.classList && event.target.classList.contains("modal")) {
        event.target.style.display = "none";
    }
});
