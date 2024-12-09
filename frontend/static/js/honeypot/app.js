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

    // Create a table
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

    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        th.style.border = '1px solid #ddd';
        th.style.padding = '8px';
        th.style.textAlign = 'left';
        th.style.backgroundColor = '#000000';
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Add data rows
    honeypotData.forEach(entry => {
        const dataRow = document.createElement('tr');

        // Map entry fields to the correct table columns
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
            td.textContent = value || '-'; // Display '-' if the value is missing
            td.style.border = '1px solid #ddd';
            td.style.padding = '8px';
            dataRow.appendChild(td);
        });

        table.appendChild(dataRow);
    });

    pageContent.appendChild(table);
}

honeypot();
