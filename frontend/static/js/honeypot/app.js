//const pageContent = document.getElementById('page-content');
//    async function honeypot(params) {
//        honeypotBody = document.createElement('div');
//        const filesResponse = await fetch('/honeypot-logs');
//        if (!filesResponse.ok) {
//          console.error('Error fetching rule files');
//          return;
//        }
//        const data = await filesResponse.json();
//        console.log(data.Honeypot);
//        for(let i = 0; i < data.Honeypot.length; i++){
//            const text196 = document.createElement('pre');
//            text196.textContent = data.Honeypot[i];
//            console.log(data.Honeypot[i]);
//            pageContent.appendChild(text196);
//        }
//
//    }
//honeypot();
const pageContent = document.getElementById('page-content');
let sortOrder = {};

async function honeypot() {
    const filesResponse = await fetch('/honeypot-logs');

    if (!filesResponse.ok) {
        console.error('Error fetching honeypot logs');
        return;
    }

    const data = await filesResponse.json();
    const honeypotData = data.Honeypot;

    if (!Array.isArray(honeypotData) || honeypotData.length === 0) {
        console.error('No honeypot data available');
        return;
    }

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

    // Add event listener to the clear logs button
    clearButton.addEventListener('click', async () => {
        statusMessage.textContent = 'Status Message: Clearing Logs... Please wait.';
        clearButton.disabled = true;

        try {
            const response = await fetch('/clear-honeypot', { method: 'POST' });

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
    });

    renderTable(honeypotData);
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
        'Timestamp',
        'Source IP',
        'Source Port',
        'Destination IP',
        'Destination Port',
        'Protocol',
        'Alert Message'
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

        const rowData = [
            entry[0],              // ID
            entry[1],              // Timestamp
            entry[3],              // Source IP
            '',                    // Source Port (Not provided in array)
            entry[4],              // Destination IP
            entry[5],              // Destination Port
            'TCP/UDP',             // Protocol (Placeholder, adjust as needed)
            entry[2]               // Alert Message
        ];

        rowData.forEach(value => {
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

honeypot();
