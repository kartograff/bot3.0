// Основные JS-функции для всего приложения

document.addEventListener('DOMContentLoaded', function() {
    // Feather Icons уже инициализируется в base.html, но на всякий случай
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Обработка flash-сообщений (автоматическое скрытие через 5 секунд)
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transition = 'opacity 0.5s ease';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});

// Общие функции для работы с модалками
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}