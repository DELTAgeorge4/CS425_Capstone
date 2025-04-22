document.addEventListener("DOMContentLoaded", async function() {
    const leftPaneContent = document.getElementById("leftpane-content");
    const adminActivity = document.getElementById("admin-activity-section");
    
    try {
        // Fetch role data
        const roleDataResponse = await fetch("/role", {method: "GET"});
        const roleData = await roleDataResponse.json();
        console.log("Role Data: ", roleData);
        
        // Display user role
        const UserRoleHeader = document.createElement('H1');
        UserRoleHeader.textContent = "User Role: " + roleData.Role;
        leftPaneContent.append(UserRoleHeader);
        
        // Fetch login logs data
        const loginActivityResponse = await fetch("/login-logs", {method: "GET"});
        if (!loginActivityResponse.ok) {
            throw new Error(`Error fetching login logs: ${loginActivityResponse.status}`);
        }
        const loginActivityData = await loginActivityResponse.json();
        console.log("Login Activity Data: ", loginActivityData);
        
        if (adminActivity) {
            const logsHeader = document.createElement('h2');
            logsHeader.textContent = "Recent User Activity";
            adminActivity.appendChild(logsHeader);
            
            const logsTable = document.createElement('table');
            logsTable.className = 'login-logs-table';
            
            const tableHeader = document.createElement('thead');
            const headerRow = document.createElement('tr');
            
            const columns = [ 'username', 'action', 'timestamp'];
            const columnLabels = [ 'Username', 'Action', 'Time'];
            
            for (let i = 0; i < columns.length; i++) {
                const th = document.createElement('th');
                th.textContent = columnLabels[i];
                headerRow.appendChild(th);
            }
            
            tableHeader.appendChild(headerRow);
            logsTable.appendChild(tableHeader);
            
            const tableBody = document.createElement('tbody');
            
            const sortedLogs = [...loginActivityData.logs].sort((a, b) => {
                return new Date(b.timestamp) - new Date(a.timestamp);
            });
            
            sortedLogs.forEach(log => {
                const row = document.createElement('tr');
                
                columns.forEach(column => {
                    const cell = document.createElement('td');
                    
                    if (column === 'timestamp' && log[column]) {
                        const date = new Date(log[column]);
                        cell.textContent = date.toLocaleString();
                    } else {
                        cell.textContent = log[column] || 'N/A';
                    }
                    
                    row.appendChild(cell);
                });
                
                tableBody.appendChild(row);
            });
            
            logsTable.appendChild(tableBody);
            adminActivity.appendChild(logsTable);
            
        }
        
        const ctx = document.getElementById('myChart');
        const ctxDonut = document.getElementById('myDonutChart');
        
        if (ctx && ctxDonut) {
            const data = {
                labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
                datasets: [{
                    label: 'Network Traffic',
                    data: [65, 59, 80, 81, 56, 55, 7],
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            };
            
            const config = {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Network Traffic Over Time'
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Month'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Traffic'
                            }
                        }
                    }
                }
            };
            
            const myChart = new Chart(ctx.getContext('2d'), config);
            
            const donutData = {
                labels: ['Used Memory', 'Free Memory'],
                datasets: [{
                    label: 'Memory Usage',
                    data: [70, 30],
                    backgroundColor: ['rgb(255, 99, 132)', 'rgb(54, 162, 235)'],
                    hoverOffset: 4
                }]
            };
            
            const donutConfig = {
                type: 'doughnut',
                data: donutData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Memory Usage'
                        }
                    }
                }
            };
            
            const myDonutChart = new Chart(ctxDonut.getContext('2d'), donutConfig);
        }
    } catch (error) {
        console.error("Error:", error);
        // Display error message to user
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = `An error occurred: ${error.message}`;
        leftPaneContent.appendChild(errorElement);
    }
});