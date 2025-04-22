document.addEventListener('DOMContentLoaded', async () => {
    console.log("Settings Configuration Page Loaded");
    const config_file_div = document.getElementById("config-file");

    //create a text input element
    const textInput = document.createElement("input");
    textInput.type = "text";
    textInput.id = "config-file-input";
    textInput.placeholder = "Enter config file path";
    
    try {
        const response = await fetch('/config-file', {
            method: 'GET',
            credentials: 'include' // For authentication cookies if needed
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(data.config); // Log the raw config data
        textInput.value = data.config; // Set the input value to the config path
        // Append the text input to the div
        if (config_file_div) {
            config_file_div.appendChild(textInput);
        }
        // Display the raw config in the div
        if (config_file_div) {
            config_file_div.textContent = data.config;
            // If you want better formatting:
            // config_file_div.innerHTML = `<pre>${data.config}</pre>`;
        }
    } catch (error) {
        console.error("Error fetching config file:", error);
        if (config_file_div) {
            config_file_div.textContent = "Failed to load configuration";
        }
    }
});