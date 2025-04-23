document.addEventListener('DOMContentLoaded', () => {
    console.log("Settings Page Loaded");
   
    // Hide all settings containers initially
    document.getElementById("theme-settings-container").style.display = "none";
    document.getElementById("config-settings-container").style.display = "none";
   
    // Show the default tab (Appearance)
    document.getElementById("settings_appearance").classList.add("active");
    document.getElementById("theme-settings-container").style.display = "block";
   
    // Set event listeners for the settings options
    document.querySelectorAll(".set-option").forEach(option => {
        option.addEventListener("click", function() {
            setActiveAndShowContent(this);
        });
    });

    // Ensure iframes have proper height
    adjustIframeHeights();

    // Add window resize listener to adjust iframe heights when window is resized
    window.addEventListener('resize', adjustIframeHeights);
});

// Function to adjust iframe heights
function adjustIframeHeights() {
    const headerHeight = 50; // Approximate height of the h3 headers
    const containerPadding = 20; // Account for padding
    const availableHeight = document.querySelector('.div2').offsetHeight - headerHeight - containerPadding;
    
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach(iframe => {
        iframe.style.height = availableHeight + 'px';
    });
}

// Highlight active settings tab and show corresponding content
function setActiveAndShowContent(element) {
    // Remove active class from all options
    document.querySelectorAll(".set-option").forEach(option => option.classList.remove("active"));
   
    // Add active class to clicked option
    element.classList.add("active");
   
    // Hide all settings containers
    document.getElementById("theme-settings-container").style.display = "none";
    document.getElementById("config-settings-container").style.display = "none";
   
    // Show the appropriate container based on which option was clicked
    if (element.id === "settings_appearance") {
        document.getElementById("theme-settings-container").style.display = "block";
    } else if (element.id === "settings_configuration") {
        document.getElementById("config-settings-container").style.display = "block";
    }

    // Readjust iframe heights after showing the container
    setTimeout(adjustIframeHeights, 100);
}

// Replace the existing setActive function with the new one
function setActive(element) {
    setActiveAndShowContent(element);
}