document.addEventListener('DOMContentLoaded', () => {
    const seleccionarAsientoButtons = document.querySelectorAll('.seleccionar-asiento-btn');

    seleccionarAsientoButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const vueloId = button.getAttribute('data-vuelo-id');

            const response = await fetch(`/seleccionar_asientos/${vueloId}`, { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                const asientoCell = document.getElementById(`asiento-seleccionado-${vueloId}`);
                asientoCell.textContent = `Asiento ${data.asiento_seleccionado}`;
            }
        });
    });
});
