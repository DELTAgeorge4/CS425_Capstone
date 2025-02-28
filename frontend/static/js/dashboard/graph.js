document.addEventListener("DOMContentLoaded", async function() {
    const leftPaneContent = document.getElementById("leftpane-content");

    const roleDataResponse = await fetch("/role", {method: "GET"});

    const roleData = await roleDataResponse.json();

    console.log("Role Data: ", roleData);



    console.log(roleData.Role);

    const UserRoleHeader = document.createElement('H1');
    UserRoleHeader.textContent = "User Role: " + roleData.Role;


    leftPaneContent.append(UserRoleHeader);
    const ctx = document.getElementById('myChart').getContext('2d');
    const ctxDonut = document.getElementById('myDonutChart').getContext('2d');
    
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
  
    const myChart = new Chart(ctx, config);

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

    const myDonutChart = new Chart(ctxDonut, donutConfig);
});
