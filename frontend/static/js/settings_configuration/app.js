// Example using fetch API
async function fetchConfig() {
    try {
        const response = await fetch('/config-file');
        const result = await response.json();
        
        const textArea = document.createElement('textarea');
        textArea.id = 'config-file-input';
        
        // Set the value property instead of innerText to preserve formatting
        textArea.value = result.config;
        
        // Add some styling to make it look better
        textArea.style.width = '100%';
        textArea.style.minHeight = '400px';
        textArea.style.fontFamily = 'monospace';
        textArea.style.whiteSpace = 'pre';
        textArea.style.padding = '10px';
        
        // Clear any existing content and append the textarea
        const container = document.getElementById('config-file');
        container.innerHTML = '';
        container.appendChild(textArea);
        
    } catch (error) {
        console.error("Error fetching config:", error);
    }
}

async function updateConfig(newConfig) {
    try {
        const response = await fetch('/update-config-file', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ config: newConfig })
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error("Error updating config:", error);
        alert("Failed to update configuration");
    }
}

// Call fetchConfig() on page load to show current configuration.
window.addEventListener('DOMContentLoaded', fetchConfig);