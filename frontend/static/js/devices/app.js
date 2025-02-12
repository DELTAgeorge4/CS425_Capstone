//const pageContent = document.getElementById('page-content');
//    async function snmp(params) {
//        snmpBody = document.createElement('div');
//        const filesResponse = await fetch('/snmp-logs');
//        if (!filesResponse.ok) {
//          console.error('Error fetching rule files');
//          return;
//        }
//        const data = await filesResponse.json();
//        console.log(data.SNMP);
//        for(let i = 0; i < data.SNMP.length; i++){
//            const text196 = document.createElement('pre');
//            text196.textContent = data.SNMP[i];
//            console.log(data.SNMP[i]);
//            pageContent.appendChild(text196);
//        }
//    }
//snmp();
const pageContent = document.getElementById('page-content');
let sortOrder = {};

async function snmp() {
    const filesResponse = await fetch('/snmp-logs');

    const roleDataResponse = await fetch("/role", { method: "GET" });

    const roleData = await roleDataResponse.json();

    const userRole = roleData.Role;


    // Create and append the clear logs button
    const clearButton = document.createElement('input');
    clearButton.type = 'button';
    clearButton.value = 'Clear Logs';
    clearButton.style.marginBottom = '20px';
    pageContent.appendChild(clearButton);

    // Add status message element
    const statusMessage = document.createElement('p');
    statusMessage.id = 'statusMessage';
    statusMessage.textContent = 'Status Message: ';
    statusMessage.style.marginBottom = '20px';
    pageContent.appendChild(statusMessage);

    if (userRole === "admin") {
        clearButton.style.display = "inline-block";
    } else {
        clearButton.style.display = "none";
    }

    if (!filesResponse.ok) {
        console.error('Error fetching SNMP data');
        return;
    }

    const data = await filesResponse.json();
    let snmpData = data.SNMP;

    if (!Array.isArray(snmpData) || snmpData.length === 0) {
        console.error('No SNMP data available');
        return;
    }



    // Add event listener to the clear logs button
    clearButton.addEventListener('click', async () => {
        if (confirm("Are you sure you want to clear logs?") == true) {
            statusMessage.textContent = 'Status Message: Clearing Logs... Please wait.';
            clearButton.disabled = true;

            try {
                const response = await fetch('/clear-snmp', { method: 'POST' });

                if (!response.ok) {
                    throw new Error(`HTTP error: ${response.status}`);
                }

                statusMessage.textContent = 'Status Message: Logs Cleared Successfully!';
                setTimeout(() => (statusMessage.textContent = 'Status Message: '), 3000);
            } catch (error) {
                console.error('Error Clearing Logs:', error);
                statusMessage.textContent = 'Failed to clear logs. Please try again later.';
                setTimeout(() => (statusMessage.textContent = 'Status Message: '), 5000);
            } finally {
                clearButton.disabled = false;
            }
        }
    });

    renderTable(snmpData);
}

function renderTable(data) {
    // Clear previous table
    const existingTable = pageContent.querySelector('table');
    if (existingTable) existingTable.remove();

    // Create a new table
    const table = document.createElement('table');
    table.style.borderCollapse = 'collapse';
    table.style.width = '100%';
    table.style.margin = '20px 0';
    table.style.border = '1px solid #ddd';

    // Create the table header row
    const headerRow = document.createElement('tr');
    const headers = [
        'ID',
        'Hostname',
        'System Uptime',
        'CPU Usage',
        'RAM Used',
        'RAM Total',
        'RAM % Used',
        'Root Dir Used Storage',
        'Root Dir Total Storage',
        'Root Dir % Used',
        'Timestamp'
    ];

    headers.forEach((header, index) => {
        const th = document.createElement('th');
        th.textContent = header;
        th.style.border = '1px solid #ddd';
        th.style.padding = '8px';
        th.style.textAlign = 'left';
        th.style.backgroundColor = '#000000';
        th.style.color = '#FFFFFF';
        th.style.cursor = 'pointer';

        // Event listener for sorting
        th.addEventListener('click', () => {
            const isAscending = sortOrder[index] !== true;
            sortOrder[index] = isAscending;

            data.sort((a, b) => {
                const valueA = a[index] || '';
                const valueB = b[index] || '';

                if (typeof valueA === 'number' && typeof valueB === 'number') {
                    return isAscending ? valueA - valueB : valueB - valueA;
                }
                return isAscending
                    ? String(valueA).localeCompare(String(valueB))
                    : String(valueB).localeCompare(String(valueA));
            });

            renderTable(data);
        });

        if (sortOrder[index] !== undefined) {
            th.textContent += sortOrder[index] ? ' ↑' : ' ↓';
        }

        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    data.forEach(entry => {
        const dataRow = document.createElement('tr');

        entry.forEach(value => {
            const td = document.createElement('td');
            td.textContent = value || '-';
            td.style.border = '1px solid #ddd';
            td.style.padding = '8px';
            dataRow.appendChild(td);
        });

        table.appendChild(dataRow);
    });

    pageContent.appendChild(table);
}

snmp();
