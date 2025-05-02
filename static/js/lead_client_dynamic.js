document.addEventListener('DOMContentLoaded', function() {
    const clientSelect = document.getElementById('id_client_select');
    const leadNameInput = document.getElementById('id_lead_name');
    const leadEmailInput = document.getElementById('id_lead_email');

    if (clientSelect) {
        clientSelect.addEventListener('change', function() {
            const clientId = this.value;
            
            if (clientId) {
                fetch(`/leads/get-client-details/?client_id=${clientId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Populate name and email if not already filled
                            if (!leadNameInput.value) {
                                leadNameInput.value = data.name;
                            }
                            
                            if (!leadEmailInput.value) {
                                leadEmailInput.value = data.email;
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            }
        });
    }
});