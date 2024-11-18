document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        });

        const contentType = response.headers.get("content-type");

        // Temporary debug to see response content
        const rawText = await response.text();
        console.log("Raw response:", rawText);

        let data;
        if (contentType && contentType.includes("application/json")) {
            data = JSON.parse(rawText); // Parse the JSON response here
        } else {
            data = { detail: "Unexpected response format" };
        }

        if (response.ok) {
            document.getElementById("message").innerText = data.message || "Login successful";
            console.log("Login successful");
            window.location.href = "/home";  
            console.log("WeniehutJR");
        } else {
            document.getElementById("message").innerText = data.detail || "Login failed";
        }
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("message").innerText = "Server error";
    }
});
