document.addEventListener("DOMContentLoaded", async () => {
    const dropdown = document.getElementById("device_selection_box");
    const infoPanel = document.getElementById("device_info_panel");

    try {
        const response = await fetch('/get_device_list');
        const data = await response.json();

        const devices = data.devices.split('\n').filter(device => device.trim() !== "");

        const defaultOption = document.createElement("option");
        defaultOption.textContent = "No device selected";
        defaultOption.value = "";
        dropdown.appendChild(defaultOption);

        devices.forEach(device => {
            const option = document.createElement("option");
            option.textContent = device;
            option.value = device;
            dropdown.appendChild(option);
        });

        dropdown.addEventListener("change", async () => {
            const deviceName = dropdown.value;
            const firstOption = dropdown.options[0];

            if (deviceName) {
                firstOption.disabled = true;
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

    function getChartTextColor() {
        const computedStyle = getComputedStyle(document.documentElement);
        return computedStyle.getPropertyValue('--text-color').trim() || '#333333';
    }

    const netCtx = document.getElementById('net_chart');
    const transportCtx = document.getElementById('transport_chart');
    const applicationCtx = document.getElementById('application_chart');

    let net_chart, transport_chart, application_chart;

    if (netCtx && transportCtx && applicationCtx) {
        const textColor = getChartTextColor();

        // Set default colors for all charts
        Chart.defaults.color = textColor;

        const createChart = (ctx, title) => {
            return new Chart(ctx.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: [],
                    datasets: [{ data: [], backgroundColor: [] }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        title: {
                            display: true,
                            text: title,
                            font: { size: 18 },
                            color: textColor
                        },
                        legend: {
                            labels: {
                                color: textColor
                            }
                        }
                    }
                }
            });
        };

        net_chart = createChart(netCtx, 'Network Layer Traffic');
        transport_chart = createChart(transportCtx, 'Transport Layer Traffic');
        application_chart = createChart(applicationCtx, 'Application Layer Traffic');

        // Listen for theme changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    const newTextColor = getChartTextColor();
                    
                    // Update chart colors
                    Chart.defaults.color = newTextColor;
                    
                    // Update existing charts
                    if (net_chart) {
                        net_chart.options.plugins.title.color = newTextColor;
                        net_chart.options.plugins.legend.labels.color = newTextColor;
                        net_chart.update();
                    }
                    if (transport_chart) {
                        transport_chart.options.plugins.title.color = newTextColor;
                        transport_chart.options.plugins.legend.labels.color = newTextColor;
                        transport_chart.update();
                    }
                    if (application_chart) {
                        application_chart.options.plugins.title.color = newTextColor;
                        application_chart.options.plugins.legend.labels.color = newTextColor;
                        application_chart.update();
                    }
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }

    const generateColors = (numLabels) => {
        const colors = [];
        const colorPalette = ['red', 'blue', 'yellow', 'green', 'purple', 'orange', 'pink', 'cyan', 'lime', 'indigo'];
        for (let i = 0; i < numLabels; i++) {
            colors.push(colorPalette[i % colorPalette.length]);
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

    const fetchAndUpdateCharts = async () => {
        const startInput = document.getElementById("start_time").value;
        const endInput = document.getElementById("end_time").value;
        const params = new URLSearchParams();

        if (startInput) params.append("start", startInput);
        if (endInput) params.append("end", endInput);

        try {
            const response = await fetch(`/get_chart_data?${params.toString()}`);
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
    };

    await fetchAndUpdateCharts(); // Initial load

    document.getElementById("start_time").addEventListener("change", fetchAndUpdateCharts);
    document.getElementById("end_time").addEventListener("change", fetchAndUpdateCharts);

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

    document.getElementById('start_capture').addEventListener('click', async () => {
        const dropdown = document.getElementById("device_selection_box");
        const deviceName = dropdown.value;
        const output = document.getElementById("output");
        const infoPanel = document.getElementById("device_info_panel");

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

            output.textContent = data.message;
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
        const infoPanel = document.getElementById("device_info_panel");

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

            output.textContent = data.message;
            infoPanel.innerHTML = "Updating device info...";
            infoPanel.innerHTML = await fetchDeviceInfo(deviceName);

        } catch (error) {
            console.error('Fetch error:', error);
            output.textContent = `Error: ${error.message}`;
        }
    });

    document.getElementById('make_pcap').addEventListener('click', () => {
        const start = document.getElementById("start_time").value;
        const end = document.getElementById("end_time").value;
    
        const form = document.getElementById('downloadForm');
        
        // Set form action to include no query string (POST form body will handle the data)
        form.action = '/generate_and_download_pcap';
    
        // Create hidden fields for start and end times
        const startInput = document.createElement('input');
        startInput.type = 'hidden';
        startInput.name = 'start';
        startInput.value = start;
    
        const endInput = document.createElement('input');
        endInput.type = 'hidden';
        endInput.name = 'end';
        endInput.value = end;
    
        // Remove any previous hidden fields to avoid duplication
        form.querySelectorAll('input[name="start"], input[name="end"]').forEach(e => e.remove());
    
        form.appendChild(startInput);
        form.appendChild(endInput);
    
        form.submit();
    });
});