const pageContent = document.getElementById('page-content');
let sortOrder = {};
let currentPage = 1;
let rowsPerPage = 32;
let fullData = [];
let filters = [];

// Mapping from header names to functions that extract values from an entry
const filterMapping = {
    "ID": entry => entry[0],
    "Timestamp": entry => entry[1],
    "Source IP": entry => entry[3],
    "Source Port": entry => "",               // Not provided in the array
    "Destination IP": entry => entry[4],
    "Destination Port": entry => entry[5],
    "Protocol": entry => "TCP/UDP",            // Placeholder
    "Alert Message": entry => entry[2]
};

async function honeypot() {
    // Clear any existing content
    pageContent.innerHTML = '';

    // ——— Header ———
    const header = document.createElement('h1');
    header.textContent = 'Honeypot Logs';
    pageContent.appendChild(header);

    // Fetch user role
    const roleDataResponse = await fetch("/role", { method: "GET" });
    const roleData = await roleDataResponse.json();
    const userRole = roleData.Role;

    // ——— Status & Restart Controls ———
    const statusHoneypotBtn = document.createElement('button');
    statusHoneypotBtn.id = 'status-honeypot-btn';
    statusHoneypotBtn.textContent = 'Check Honeypot Service Status';
    statusHoneypotBtn.style.marginRight = '0.5rem';
    pageContent.appendChild(statusHoneypotBtn);

    const restartHoneypotBtn = document.createElement('button');
    restartHoneypotBtn.id = 'restart-honeypot-btn';
    restartHoneypotBtn.textContent = 'Restart Honeypot Service';
    restartHoneypotBtn.style.marginRight = '0.5rem';
    restartHoneypotBtn.style.display = userRole === 'admin' ? 'inline-block' : 'none';
    pageContent.appendChild(restartHoneypotBtn);

    const honeypotStatusDisplay = document.createElement('span');
    honeypotStatusDisplay.id = 'honeypot-status-display';
    pageContent.appendChild(honeypotStatusDisplay);

    statusHoneypotBtn.addEventListener('click', async () => {
        honeypotStatusDisplay.textContent = '🔄 Checking…';
        try {
            const res = await fetch('/status-py-honeypot', {
                method: 'GET',
                credentials: 'include'
            });
            if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
            const { status } = await res.json();
            honeypotStatusDisplay.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        } catch (e) {
            console.error(e);
            honeypotStatusDisplay.textContent = '❌ Error';
        }
    });

    restartHoneypotBtn.addEventListener('click', async () => {
        if (!confirm('Restart Honeypot service?')) return;
        restartHoneypotBtn.disabled = true;
        honeypotStatusDisplay.textContent = '⏳ Restarting…';
        try {
            const res = await fetch('/restart-py-honeypot', {
                method: 'POST',
                credentials: 'include'
            });
            if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
            honeypotStatusDisplay.textContent = '✅ Restarted';
        } catch (e) {
            console.error(e);
            honeypotStatusDisplay.textContent = '❌ ' + e.message;
        } finally {
            setTimeout(() => {
                honeypotStatusDisplay.textContent = '';
                restartHoneypotBtn.disabled = false;
            }, 3000);
        }
    });
    // —————————————————————————————

    // Create and append the clear logs button
    const clearButton = document.createElement('input');
    clearButton.type = 'button';
    clearButton.value = 'Clear Logs';
    clearButton.style.marginBottom = '20px';
    pageContent.appendChild(clearButton);

    // Status message element
    const statusMessage = document.createElement('p');
    statusMessage.id = 'statusMessage';
    statusMessage.textContent = 'Status Message: ';
    statusMessage.style.marginBottom = '20px';
    pageContent.appendChild(statusMessage);

    clearButton.style.display = userRole === "admin" ? "inline-block" : "none";

    clearButton.addEventListener('click', async () => {
        if (!confirm("Are you sure you want to clear logs?")) return;
        statusMessage.textContent = 'Status Message: Clearing Logs... Please wait.';
        clearButton.disabled = true;
        try {
            const response = await fetch('/clear-honeypot', { method: 'POST' });
            if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
            statusMessage.textContent = 'Status Message: Logs Cleared Successfully!';
            setTimeout(() => window.location.reload(), 1000);
        } catch (error) {
            console.error('Error Clearing Logs:', error);
            statusMessage.textContent = 'Failed to clear logs. Please try again later.';
            setTimeout(() => statusMessage.textContent = 'Status Message: ', 5000);
        } finally {
            clearButton.disabled = false;
        }
    });

    // ——— Filter UI ———
    const filtersContainer = document.createElement('div');
    filtersContainer.id = 'filters-container';
    filtersContainer.style.marginBottom = '20px';
    filtersContainer.style.border = '1px solid #ccc';
    filtersContainer.style.padding = '10px';
    const filtersTitle = document.createElement('h4');
    filtersTitle.textContent = 'Filters:';
    filtersContainer.appendChild(filtersTitle);

    const filterRowsContainer = document.createElement('div');
    filterRowsContainer.id = 'filter-rows-container';
    filtersContainer.appendChild(filterRowsContainer);

    const addFilterButton = document.createElement('button');
    addFilterButton.textContent = 'Add Filter';
    filtersContainer.appendChild(addFilterButton);

    const applyFiltersButton = document.createElement('button');
    applyFiltersButton.textContent = 'Apply Filters';
    filtersContainer.appendChild(applyFiltersButton);

    const clearFiltersButton = document.createElement('button');
    clearFiltersButton.textContent = 'Clear Filters';
    filtersContainer.appendChild(clearFiltersButton);

    pageContent.appendChild(filtersContainer);

    function addFilterRow() {
        const row = document.createElement('div');
        row.style.marginBottom = '5px';
        row.style.display = 'flex';
        row.style.alignItems = 'center';
        row.style.gap = '5px';

        const select = document.createElement('select');
        const headers = [
            'ID', 'Timestamp', 'Source IP', 'Source Port',
            'Destination IP', 'Destination Port',
            'Protocol', 'Alert Message'
        ];
        headers.forEach(header => {
            const option = document.createElement('option');
            option.value = header;
            option.textContent = header;
            select.appendChild(option);
        });
        row.appendChild(select);

        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = 'Enter filter text...';
        row.appendChild(input);

        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.addEventListener('click', () => row.remove());
        row.appendChild(removeButton);

        filterRowsContainer.appendChild(row);
    }

    addFilterRow();
    addFilterButton.addEventListener('click', addFilterRow);

    applyFiltersButton.addEventListener('click', () => {
        filters = [];
        filterRowsContainer.querySelectorAll('div').forEach(row => {
            const select = row.querySelector('select');
            const input = row.querySelector('input');
            const column = select.value;
            const query = input.value.trim();
            if (query) filters.push({ column, query });
        });
        currentPage = 1;
        renderTable(fullData);
    });

    clearFiltersButton.addEventListener('click', () => {
        filterRowsContainer.innerHTML = '';
        filters = [];
        currentPage = 1;
        renderTable(fullData);
        addFilterRow();
    });
    // —————————————————

    // Fetch and display honeypot logs
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

    fullData = honeypotData;
    renderTable(fullData);
}

function renderTable(data) {
    // Apply filters
    let filteredData = data;
    if (filters.length) {
        filteredData = data.filter(entry =>
            filters.every(f => {
                const val = filterMapping[f.column](entry) || '';
                return val.toString().toLowerCase().includes(f.query.toLowerCase());
            })
        );
    }

    // Remove old table/pagination
    pageContent.querySelectorAll('table, .pagination').forEach(el => el.remove());

    const totalPages = Math.ceil(filteredData.length / rowsPerPage) || 1;
    currentPage = Math.min(Math.max(1, currentPage), totalPages);

    const start = (currentPage - 1) * rowsPerPage;
    const slice = filteredData.slice(start, start + rowsPerPage);

    // Build table
    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.style.border = '1px solid #ddd';

    // Header row
    const headerRow = document.createElement('tr');
    const headers = [
        'ID', 'Timestamp', 'Source IP', 'Source Port',
        'Destination IP', 'Destination Port',
        'Protocol', 'Alert Message'
    ];
    headers.forEach((h, i) => {
        const th = document.createElement('th');
        th.textContent = h + (sortOrder[i] != null ? (sortOrder[i] ? ' ↑' : ' ↓') : '');
        th.style.padding = '8px';
        th.style.border = '1px solid #ddd';
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            const asc = !sortOrder[i];
            sortOrder[i] = asc;
            data.sort((a, b) => {
                let va, vb;
                switch (h) {
                    case 'ID':             va = a[0]; vb = b[0]; break;
                    case 'Timestamp':      va = a[1]; vb = b[1]; break;
                    case 'Source IP':      va = a[3]; vb = b[3]; break;
                    case 'Destination IP': va = a[4]; vb = b[4]; break;
                    case 'Destination Port':va = a[5]; vb = b[5]; break;
                    case 'Alert Message':  va = a[2]; vb = b[2]; break;
                    default:               va = '';   vb = '';
                }
                if (typeof va === 'number' && typeof vb === 'number') {
                    return asc ? va - vb : vb - va;
                }
                return asc
                    ? String(va).localeCompare(vb)
                    : String(vb).localeCompare(va);
            });
            currentPage = 1;
            renderTable(data);
        });
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Data rows
    slice.forEach(entry => {
        const tr = document.createElement('tr');
        const rowData = [
            entry[0],
            entry[1],
            entry[3],
            '',
            entry[4],
            entry[5],
            'TCP/UDP',
            entry[2]
        ];
        rowData.forEach(val => {
            const td = document.createElement('td');
            td.textContent = val || '-';
            td.style.border = '1px solid #ddd';
            td.style.padding = '8px';
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
    pageContent.appendChild(table);

    // Pagination controls
    const pc = document.createElement('div');
    pc.classList.add('pagination');
    pc.style.display = 'flex';
    pc.style.justifyContent = 'space-between';
    pc.style.alignItems = 'center';
    pc.style.margin = '20px 0';

    const perSelect = document.createElement('select');
    [32, 64, 96].forEach(n => {
        const opt = document.createElement('option');
        opt.value = n;
        opt.textContent = n;
        if (n === rowsPerPage) opt.selected = true;
        perSelect.appendChild(opt);
    });
    perSelect.addEventListener('change', e => {
        rowsPerPage = +e.target.value;
        currentPage = 1;
        renderTable(data);
    });
    pc.appendChild(perSelect);

    const prev = document.createElement('button');
    prev.textContent = 'Previous';
    prev.disabled = currentPage === 1;
    prev.addEventListener('click', () => {
        currentPage--;
        renderTable(data);
    });
    pc.appendChild(prev);

    const info = document.createElement('span');
    info.textContent = `Page ${currentPage} of ${totalPages} (Filtered ${filteredData.length})`;
    pc.appendChild(info);

    const next = document.createElement('button');
    next.textContent = 'Next';
    next.disabled = currentPage === totalPages;
    next.addEventListener('click', () => {
        currentPage++;
        renderTable(data);
    });
    pc.appendChild(next);

    pageContent.appendChild(pc);
}

// Initialize the page
honeypot();
