document.addEventListener("DOMContentLoaded", function () {
    loadNavigation();
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
function loadNavigation() {
    fetch("/nav")
        .then(response => response.text())
        .then(data => {
            document.getElementById("nav-placeholder").innerHTML = data;
            const navLinks = document.querySelectorAll("#nav-placeholder ul li a");
            navLinks.forEach(link => {
                if (window.location.pathname === link.pathname) {
                    link.classList.add("active");
                }
            });
        })
        .catch(error => console.error("Error loading navigation:", error));
}

// Load user settings (theme & font size)
function loadUserSettings() {
    fetch("/user-settings")
        .then(response => response.json())
        .then(data => {
            if (data.theme) {
                document.documentElement.setAttribute("data-theme", data.theme);
                // If theme selector exists, update its value
                const themeSelect = document.getElementById("theme");
                if (themeSelect) {
                    themeSelect.value = data.theme;
                }
            }
            if (data.font_size) {
                document.documentElement.setAttribute("data-font", data.font_size);
                // If font selector exists, update its value
                const fontSelect = document.getElementById("font-selector");
                if (fontSelect) {
                    fontSelect.value = data.font_size;
                }
            }
        })
        .catch(error => console.error("Error loading user settings:", error));
}

// Save user settings (theme & font size)
function saveUserSettings() {
    const themeSelect = document.getElementById("theme");
    const fontSelect = document.getElementById("font-selector");

    // Only proceed if these elements exist
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
        document.documentElement.setAttribute("data-theme", theme);
        document.documentElement.setAttribute("data-font", fontSize);
        alert("Settings saved successfully!");
    })
    .catch(error => console.error("Error saving settings:", error));
}

// Optional: Mapping function if needed for direct style changes (not used here)
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

// Highlight active settings tab
function setActive(element) {
    document.querySelectorAll(".set-option").forEach(option => option.classList.remove("active"));
    element.classList.add("active");
}
