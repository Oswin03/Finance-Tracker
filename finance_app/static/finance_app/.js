document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Date picker enhancements
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });

    // Dynamic category selection based on transaction type
    const transactionTypeSelect = document.getElementById('id_is_income');
    const categorySelect = document.getElementById('id_category');
    
    if (transactionTypeSelect && categorySelect) {
        function updateCategories() {
            const isIncome = transactionTypeSelect.checked;
            const options = categorySelect.options;
            
            for (let i = 0; i < options.length; i++) {
                const option = options[i];
                const isIncomeCategory = option.dataset.isIncome === 'true';
                
                if (isIncome) {
                    option.style.display = isIncomeCategory ? '' : 'none';
                } else {
                    option.style.display = isIncomeCategory ? 'none' : '';
                }
                
                if (option.selected && option.style.display === 'none') {
                    categorySelect.selectedIndex = 0;
                }
            }
        }
        
        transactionTypeSelect.addEventListener('change', updateCategories);
        updateCategories(); // Initial call
    }

    // Auto-format currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"][data-currency]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
});

// Chart initialization function to be called from specific pages
function initChart(chartId, chartData) {
    const ctx = document.getElementById(chartId).getContext('2d');
    return new Chart(ctx, chartData);
}