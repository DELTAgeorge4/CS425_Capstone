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

async function snmp() {
    const filesResponse = await fetch('/snmp-logs');

    if (!filesResponse.ok) {
        console.error('Error fetching SNMP data');
        return;
    }

    const data = await filesResponse.json();
    const snmpData = data.SNMP;

    // Create a table
    const table = document.createElement('table');
    table.style.borderCollapse = 'collapse';
    table.style.width = '100%';
    table.style.margin = '20px 0';

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

    snmpData.forEach(entry => {
        const dataRow = document.createElement('tr');

        entry.forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            td.style.border = '1px solid #ddd';
            td.style.padding = '8px';
            dataRow.appendChild(td);
        });

        table.appendChild(dataRow);
    });

    pageContent.appendChild(table);
}

snmp();
