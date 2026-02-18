// JS для работы со справочниками
// Например, динамическая подгрузка моделей при выборе марки

document.addEventListener('DOMContentLoaded', function() {
    const brandSelect = document.getElementById('brandFilter');
    if (brandSelect) {
        brandSelect.addEventListener('change', function() {
            const brandId = this.value;
            if (brandId) {
                window.location.href = `/admin/dict/models?brand_id=${brandId}`;
            }
        });
    }
});