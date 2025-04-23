// config.js

// Fetch the current config and build the UI
async function fetchConfig() {
    try {
      const response = await fetch('/config-file');
      const result = await response.json();
  
      const container = document.getElementById('config-file');
      container.innerHTML = '';
  
      // 1) Textarea for editing
      const textArea = document.createElement('textarea');
      textArea.id = 'config-file-input';
      textArea.value = result.config;
      textArea.style.width = '100%';
      textArea.style.minHeight = '400px';
      textArea.style.fontFamily = 'monospace';
      textArea.style.whiteSpace = 'pre';
      textArea.style.padding = '10px';
      container.appendChild(textArea);
  
      // 2) Save button
      const saveBtn = document.createElement('button');
      saveBtn.id = 'save-config-btn';
      saveBtn.textContent = 'Save Configuration';
      saveBtn.style.display = 'block';
      saveBtn.style.marginTop = '10px';
      container.appendChild(saveBtn);
  
      // 3) Status message
      const statusSpan = document.createElement('span');
      statusSpan.id = 'config-status';
      statusSpan.style.marginLeft = '1rem';
      container.appendChild(statusSpan);
  
      // Handler for Save
      saveBtn.addEventListener('click', async () => {
        saveBtn.disabled = true;
        statusSpan.textContent = 'Saving…';
        try {
          const result = await updateConfig(textArea.value);
          // updateConfig will throw on error
          statusSpan.textContent = result.message || 'Saved!';
        } catch (err) {
          console.error(err);
          statusSpan.textContent = '❌ Error saving';
        } finally {
          setTimeout(() => {
            statusSpan.textContent = '';
            saveBtn.disabled = false;
          }, 3000);
        }
      });
  
    } catch (error) {
      console.error("Error fetching config:", error);
      alert("Failed to load configuration");
    }
  }
  
  // Push the new config to the backend
  async function updateConfig(newConfig) {
    const response = await fetch('/update-config-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ config: newConfig })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || response.statusText);
    }
    return response.json();
  }
  
  // When the page loads, fetch and render config editor
  window.addEventListener('DOMContentLoaded', fetchConfig);
  