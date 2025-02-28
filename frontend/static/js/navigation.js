document.addEventListener("DOMContentLoaded", function () {
    loadPage("{{ url_for('home') }}"); // Default page to load

    document.querySelectorAll("a[data-page]").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent full page reload
            const pageUrl = this.getAttribute("data-page");
            loadPage(pageUrl);
            history.pushState({ page: pageUrl }, "", pageUrl);
        });
    });

    window.onpopstate = function (event) {
        if (event.state && event.state.page) {
            loadPage(event.state.page);
        }
    };
});

async function loadPage(pageUrl) {
    const contentContainer = document.getElementById("content-container");
    contentContainer.style.opacity = "0"; // Smooth transition

    try {
        const response = await fetch(pageUrl);
        if (!response.ok) throw new Error("Failed to load page");

        const html = await response.text();
        contentContainer.innerHTML = html;
        contentContainer.style.opacity = "1"; // Fade in new content
    } catch (error) {
        console.error("Error loading page:", error);
        contentContainer.innerHTML = "<h2>Error loading content.</h2>";
    }
}
