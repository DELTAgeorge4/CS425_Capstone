document.addEventListener("DOMContentLoaded", function () {
    // loadNavigation();
    loadUserSettings();

    // Only add event listeners if the elements exist
    const saveSettingsBtn = document.getElementById("save-settings");
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener("click", saveUserSettings);
    }
    const saveFirewallBtn = document.getElementById("save-firewall");
    if (saveFirewallBtn) {
        saveFirewallBtn.addEventListener("click", saveFirewallSettings);
    }
});

// Load Navigation Bar
// function loadNavigation() {
//     fetch("/nav")
//         .then(response => response.text())
//         .then(data => {
//             const navPlaceholder = document.getElementById("nav-placeholder");
//             if (navPlaceholder) {
//                 navPlaceholder.innerHTML = data;
//                 const navLinks = document.querySelectorAll("#nav-placeholder ul li a");
//                 navLinks.forEach(link => {
//                     if (window.location.pathname === link.pathname) {
//                         link.classList.add("active");
//                     }
//                 });
//             }
//         })
//         .catch(error => console.error("Error loading navigation:", error));
// }


function loadUserSettings() {
    fetch("/user-settings")
        .then(response => response.json())
        .then(data => {
            if (data.theme) {
                document.documentElement.setAttribute("data-theme", data.theme);

                const themeSelect = document.getElementById("theme");
                if (themeSelect) {
                    themeSelect.value = data.theme;
                }
            }
            if (data.font_size) {
                document.documentElement.setAttribute("data-font", data.font_size);

                const fontSelect = document.getElementById("font-selector");
                if (fontSelect) {
                    fontSelect.value = data.font_size;
                }
            }
        })
        .catch(error => console.error("Error loading user settings:", error));
}

// Save user settings (theme & font size) with complete page reload
function saveUserSettings() {
    console.log("Saving user settings...");
    const themeSelect = document.getElementById("theme");
    const fontSelect = document.getElementById("font-selector");


    if (!themeSelect || !fontSelect) return;

    const theme = themeSelect.value;
    const fontSize = fontSelect.value;

    fetch("/set-user-settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme, font_size: fontSize })
    })
    .then(response => response.json())
    .then(() => {
        // Apply settings to the current document
        document.documentElement.setAttribute("data-theme", theme);
        document.documentElement.setAttribute("data-font", fontSize);
        
        alert("Settings saved successfully!");
        

        let topWindow = window;
        while (topWindow.parent !== topWindow) {
            try {
                // Try to access the parent - will throw error if cross-origin
                topWindow = topWindow.parent;
            } catch (e) {
                break;
            }
        }
        
        // Force a complete refresh of the top window (like Ctrl+F5)
        setTimeout(() => {
            // Using location.href forces a full page reload instead of using cache
            topWindow.location.href = topWindow.location.href.split('#')[0] + 
                '?reload=' + new Date().getTime();
        }, 100);
    })
    .catch(error => console.error("Error saving settings:", error));

    return false; 
}

function getFontSizeValue(fontSize) {
    const fontSizes = {
        "small": "10px",
        "medium": "16px",
        "large": "25px",
        "x-large": "32px"
    };
    return fontSizes[fontSize] || "16px";
}

// Save Firewall Settings
function saveFirewallSettings() {
    const firewallEnabled = document.getElementById("firewall-toggle").checked;
    const firewallMode = document.getElementById("firewall-mode").value;
    const blockedPorts = document.getElementById("blocked-ports").value.split(",");
    const whitelistedIps = document.getElementById("whitelisted-ips").value.split(",");
    const blacklistedIps = document.getElementById("blacklisted-ips").value.split(",");
    const trafficLogging = document.getElementById("traffic-logging").checked;
    const intrusionDetection = document.getElementById("intrusion-detection").checked;
    const customRules = document.getElementById("firewall-rules").value;

    console.log("Firewall settings saved:", {
        firewallEnabled,
        firewallMode,
        blockedPorts,
        whitelistedIps,
        blacklistedIps,
        trafficLogging,
        intrusionDetection,
        customRules
    });

    alert("Firewall settings saved successfully!");
}

