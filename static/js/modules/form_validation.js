/**
 * Asynchronous Booking Request Form Submission
 */
export function initFormValidation() {
    const bookingForm = document.getElementById('studio-booking-form');
    if (!bookingForm) return;

    bookingForm.addEventListener('submit', async (e) => {
        // If it's a normal POST, let server handle it or process via AJAX
        const formData = new FormData(bookingForm);
        try {
            const response = await fetch(bookingForm.action || window.location.href, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Booking submitted successfully:', data);
            }
        } catch (err) {
            console.warn('Form submitting natively:', err);
        }
    });
}
