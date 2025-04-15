document.addEventListener("DOMContentLoaded", async () => {
    const dropdown = document.getElementById("device_selection_box");
    const infoPanel = document.getElementById("device_info_panel");

    try {
        // Fetch available devices
        const response = await fetch('/get_device_list');
        const data = await response.json();
        
        // Extract devices and split into an array
        const devices = data.devices.split('\n').filter(device => device.trim() !== "");

        // Add "No device selected" as the default option
        const defaultOption = document.createElement("option");
        defaultOption.textContent = "No device selected";
        defaultOption.value = "";
        dropdown.appendChild(defaultOption);

        // Populate the dropdown with device options
        devices.forEach(device => {
            const option = document.createElement("option");
            option.textContent = device;
            option.value = device;
            dropdown.appendChild(option);
        });

        

        // Show device info when a new device is selected
        dropdown.addEventListener("change", async () => {
            const deviceName = dropdown.value;
            const firstOption = dropdown.options[0]; // Get "No device selected" option
        
            if (deviceName) {
                firstOption.disabled = true; // Disable "No device selected"
                infoPanel.innerHTML = "Loading...";
                infoPanel.style.display = "block";
                infoPanel.innerHTML = await fetchDeviceInfo(deviceName);
            } else {
                infoPanel.style.display = "none";
            }
        });

    } catch (error) {
        console.error("Error loading devices:", error);
    }
    // Function to fetch device info
    const fetchDeviceInfo = async (deviceName) => {
        try {
            const response = await fetch('/device', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ device: deviceName })
            });

            const result = await response.json();
            return result.output ? result.output.replace(/\n/g, "<br>") : "No data available";
        } catch (error) {
            console.error("Error fetching device info:", error);
            return "Error fetching data";
        }
    };

    // Fetch navigation data
    fetch("/nav")
        .then(response => response.text())
        .then(data => {
            document.getElementById("nav-placeholder").innerHTML = data;
            const navLinks = document.querySelectorAll("#nav-placeholder ul li a");
            navLinks.forEach(link => {
                if (link.pathname === window.location.pathname) {
                    link.classList.add("active");
                }
            });
        })
        .catch(error => console.error("Error loading navigation:", error));

    // Initialize charts
    const netCtx = document.getElementById('net_chart').getContext('2d');
    const transportCtx = document.getElementById('transport_chart').getContext('2d');
    const applicationCtx = document.getElementById('application_chart').getContext('2d');

    const createChart = (ctx, title) => {
        return new Chart(ctx, {
            type: 'pie',
            data: { labels: [], datasets: [{ data: [], backgroundColor: [] }] },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: { display: true, text: title, font: { size: 18 }, color: '#FFF' }
                }
            }
        });
    };

    const net_chart = createChart(netCtx, 'Network Layer Traffic');
    const transport_chart = createChart(transportCtx, 'Transport Layer Traffic');
    const application_chart = createChart(applicationCtx, 'Application Layer Traffic');

    const generateColors = (numLabels) => {
        const colors = [];
        const colorPalette = ['red', 'blue', 'yellow', 'green', 'purple', 'orange', 'pink', 'cyan', 'lime', 'indigo'];
        for (let i = 0; i < numLabels; i++) {
            colors.push(colorPalette[i % colorPalette.length]); // Cycle through the color palette
        }
        return colors;
    };

    const updateChartData = (chart, data) => {
        if (!data) return;
        const labels = Object.keys(data);
        const values = Object.values(data);
        chart.data.labels = labels;
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = generateColors(labels.length);
        chart.update();
    };

    try {
        const response = await fetch('/get_chart_data');
        const chartData = await response.json();

        if (chartData) {
            updateChartData(net_chart, chartData.net_chart_data);
            updateChartData(transport_chart, chartData.transport_chart_data);
            updateChartData(application_chart, chartData.application_chart_data);
        } else {
            console.error('Received empty chart data');
        }
    } catch (error) {
        console.error('Error fetching chart data:', error);
    }

    // Function to send a POST request with data
    const executeScript = async (endpoint, body = null) => {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const result = await response.text();
            output.textContent = result;
        } catch (error) {
            console.error('Error:', error);
            output.textContent = 'Error sending request';
        }
    };

    // Handle capture button click
    document.getElementById('start_capture').addEventListener('click', async () => {
        const dropdown = document.getElementById("device_selection_box");
        const deviceName = dropdown.value;
        const output = document.getElementById("output");
        const infoPanel = document.getElementById("device_info_panel"); // Get device info panel
    
        if (!deviceName) {
            output.textContent = "Please select a device.";
            return;
        }
    
        try {
            const response = await fetch('/packet_capture', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ device: deviceName })
            });
    
            const data = await response.json();
    
            if (!response.ok) {
                throw new Error(data.detail || "Unknown error");
            }
    
            output.textContent = data.message; // Ensure correct output message
    
            // Update device info panel
            infoPanel.innerHTML = "Updating device info...";
            infoPanel.innerHTML = await fetchDeviceInfo(deviceName);
    
        } catch (error) {
            console.error('Fetch error:', error);
            output.textContent = `Error: ${error.message}`;
        }
    });
    
    document.getElementById('stop_capture').addEventListener('click', async () => {
        const dropdown = document.getElementById("device_selection_box");
        const deviceName = dropdown.value;
        const output = document.getElementById("output");
        const infoPanel = document.getElementById("device_info_panel"); // Get device info panel
    
        if (!deviceName) {
            output.textContent = "Please select a device.";
            return;
        }
    
        try {
            const response = await fetch('/stop_capture', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ device: deviceName })
            });
    
            const data = await response.json();
    
            if (!response.ok) {
                throw new Error(data.detail || "Unknown error");
            }
    
            output.textContent = data.message; // Show success message
    
            // Update device info panel
            infoPanel.innerHTML = "Updating device info...";
            infoPanel.innerHTML = await fetchDeviceInfo(deviceName);
    
        } catch (error) {
            console.error('Fetch error:', error);
            output.textContent = `Error: ${error.message}`;
        }
    });
    
    

    // Handle get packets button click
    document.getElementById('get_packets').addEventListener('click', () => {
        const startTime = document.getElementById('start_time').value || 'None';
        const endTime = document.getElementById('end_time').value || 'None';
        const protocol = document.getElementById('protocol').value || 'None';
        executeScript('/packets', { startTime, endTime, protocol });
    });

});
