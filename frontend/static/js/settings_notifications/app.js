window.addEventListener('DOMContentLoaded', () => {

    console.log("Settings Page Loaded");

    showNotificationPreferences();

});

async function showNotificationPreferences() {
    const getNotifcationPreferencesDiv = document.getElementById("notifications-settings-container");
    const response = await fetch('/user-notification-settings', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    });
    
    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || response.statusText);
    }
    
    const data = await response.json();
    console.log("Notification Preferences Data:", data);
    console.log("Notification Preferences Div:", data.userNotificationPreferences);
    const userNotificationPreferences = data.userNotificationPreferences;
    
    // Clear existing content
    getNotifcationPreferencesDiv.innerHTML = '';
    
    // Iterate over the array of notification preferences
    for (let i = 0; i < userNotificationPreferences.length; i++) {
        const [notificationType, isEnabled] = userNotificationPreferences[i];
        
        console.log(`Notification Type: ${notificationType}, Enabled: ${isEnabled}`);
        
        const notificationPreferenceDiv = document.createElement('div');
        notificationPreferenceDiv.className = "notification-preference";
        notificationPreferenceDiv.innerHTML = `
            <label for="${notificationType}">${notificationType}</label>
            <input type="checkbox" id="${notificationType}" ${isEnabled ? 'checked' : ''}>
        `;
        getNotifcationPreferencesDiv.appendChild(notificationPreferenceDiv);
    }
    const saveButton = document.createElement('button');
    saveButton.innerText = "Save Preferences";
    saveButton.id = "save-notification-preferences";
    saveButton.addEventListener('click', async () => {
        const updatedPreferences = {};
        for (let i = 0; i < userNotificationPreferences.length; i++) {
            const [notificationType] = userNotificationPreferences[i];
            const checkbox = document.getElementById(notificationType);
            updatedPreferences[notificationType] = checkbox.checked;
        }
        
        console.log("Updated Preferences:", updatedPreferences);
        
        const response = await fetch('/set-notification-settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedPreferences)
        });
        
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || response.statusText);
        }
        
        alert("Notification preferences saved successfully!");
    }
    );
    getNotifcationPreferencesDiv.appendChild(saveButton);
}

