document.addEventListener("DOMContentLoaded", async function () {
    await loadAccountInfo();
});

async function loadAccountInfo() {
    try {
        const usernameIndicator = document.getElementById("username-indicator");
        const roleIndicator = document.getElementById("role-indicator");

        const roleDataResponse = await fetch("/role", { method: "GET" });

        if (!roleDataResponse.ok) {
            throw new Error("Failed to fetch role data");
        }

        const roleData = await roleDataResponse.json();

        usernameIndicator.textContent = "Username: " + roleData.Username;
        roleIndicator.textContent = "Role: " + roleData.Role;

    } catch (error) {
        console.error("Error loading account info:", error);
        document.getElementById("page-content").innerHTML = "<p>Failed to load account information.</p>";
    }
}
