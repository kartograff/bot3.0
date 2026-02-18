// Графики для страницы статистики
// Здесь будет код для Chart.js, но для простоты оставим заглушку

document.addEventListener('DOMContentLoaded', function() {
    // Пример инициализации графика, если есть элемент canvas с id appointmentsChart
    const ctx = document.getElementById('appointmentsChart');
    if (ctx) {
        fetch('/api/stats/appointments')
            .then(r => r.json())
            .then(data => {
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.map(d => d.date),
                        datasets: [{
                            label: 'Записи',
                            data: data.map(d => d.count),
                            borderColor: '#2383e2',
                            tension: 0.1
                        }]
                    }
                });
            });
    }
});