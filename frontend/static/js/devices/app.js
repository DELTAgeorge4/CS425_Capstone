const pageContent = document.getElementById('page-content');
let sortOrder = {};
let currentPage = 1;
let rowsPerPage = 32;
let fullData = [];
// Global filters: array of objects { column: string, query: string }
let filters = [];

// Define the headers (and order) for the table
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

// Mapping from header names to functions that extract values from an entry.
// We assume each entry is an array with indexes corresponding to the order above.
const filterMapping = {
    "ID": (entry) => entry[0],
    "Hostname": (entry) => entry[1],
    "System Uptime": (entry) => entry[2],
    "CPU Usage": (entry) => entry[3],
    "RAM Used": (entry) => entry[4],
    "RAM Total": (entry) => entry[5],
    "RAM % Used": (entry) => entry[6],
    "Root Dir Used Storage": (entry) => entry[7],
    "Root Dir Total Storage": (entry) => entry[8],
    "Root Dir % Used": (entry) => entry[9],
    "Timestamp": (entry) => entry[10]
};

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

    clearButton.style.display = userRole === "admin" ? "inline-block" : "none";

    // --------------------------
    // Create the multi-filter UI
    // --------------------------
    const filtersContainer = document.createElement('div');
    filtersContainer.id = 'filters-container';
    filtersContainer.style.marginBottom = '20px';
    filtersContainer.style.border = '1px solid #ccc';
    filtersContainer.style.padding = '10px';

    const filtersTitle = document.createElement('h4');
    filtersTitle.textContent = 'Filters:';
    filtersContainer.appendChild(filtersTitle);

    // Container for individual filter rows
    const filterRowsContainer = document.createElement('div');
    filterRowsContainer.id = 'filter-rows-container';
    filtersContainer.appendChild(filterRowsContainer);

    // Button to add a new filter row
    const addFilterButton = document.createElement('button');
    addFilterButton.textContent = 'Add Filter';
    filtersContainer.appendChild(addFilterButton);

    // Apply Filters button
    const applyFiltersButton = document.createElement('button');
    applyFiltersButton.textContent = 'Apply Filters';
    filtersContainer.appendChild(applyFiltersButton);

    // Clear Filters button
    const clearFiltersButton = document.createElement('button');
    clearFiltersButton.textContent = 'Clear Filters';
    filtersContainer.appendChild(clearFiltersButton);

    pageContent.appendChild(filtersContainer);

    // Function to create a new filter row
    function addFilterRow() {
        const row = document.createElement('div');
        row.style.marginBottom = '5px';
        row.style.display = 'flex';
        row.style.alignItems = 'center';
        row.style.gap = '5px';

        const select = document.createElement('select');
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
        removeButton.addEventListener('click', () => {
            row.remove();
        });
        row.appendChild(removeButton);

        filterRowsContainer.appendChild(row);
    }

    // Initially add one filter row
    addFilterRow();

    addFilterButton.addEventListener('click', () => {
        addFilterRow();
    });

    applyFiltersButton.addEventListener('click', () => {
        // Collect filters from each filter row
        filters = [];
        const rows = filterRowsContainer.querySelectorAll('div');
        rows.forEach(row => {
            const select = row.querySelector('select');
            const input = row.querySelector('input');
            const column = select.value;
            const query = input.value.trim();
            if (query !== "") {
                filters.push({ column, query });
            }
        });
        currentPage = 1;
        renderTable(fullData);
    });

    clearFiltersButton.addEventListener('click', () => {
        filterRowsContainer.innerHTML = "";
        filters = [];
        currentPage = 1;
        renderTable(fullData);
        // Optionally add one empty filter row back
        addFilterRow();
    });

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

    // Store full data for filtering and pagination
    fullData = snmpData;
    renderTable(fullData);

    // --------------------------
    // Clear Logs button event
    // --------------------------
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
                // Automatically refresh the page after a short delay
                setTimeout(() => window.location.reload(), 1000);
            } catch (error) {
                console.error('Error Clearing Logs:', error);
                statusMessage.textContent = 'Failed to clear logs. Please try again later.';
                setTimeout(() => (statusMessage.textContent = 'Status Message: '), 5000);
            } finally {
                clearButton.disabled = false;
            }
        }
    });
}

function renderTable(data) {
    // Apply filters if any exist (logical AND)
    let filteredData = data;
    if (filters.length > 0) {
        filteredData = data.filter(entry => {
            return filters.every(f => {
                const value = filterMapping[f.column](entry) || "";
                return value.toString().toLowerCase().includes(f.query.toLowerCase());
            });
        });
    }

    // Clear previous table and pagination controls (but not filter UI)
    const existingTable = pageContent.querySelector('table');
    if (existingTable) existingTable.remove();
    const existingPagination = pageContent.querySelector('.pagination');
    if (existingPagination) existingPagination.remove();

    // Pagination logic: calculate total pages and get the data slice for current page
    const totalPages = Math.ceil(filteredData.length / rowsPerPage) || 1;
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    const pageData = filteredData.slice(startIndex, endIndex);

    // Create a new table element
    const table = document.createElement('table');
    table.style.borderCollapse = 'collapse';
    table.style.width = '100%';
    table.style.margin = '20px 0';
    table.style.border = '1px solid #ddd';

    // Create header row
    const headerRow = document.createElement('tr');
    headers.forEach((header, index) => {
        const th = document.createElement('th');
        th.textContent = header;
        th.style.border = '1px solid #ddd';
        th.style.padding = '8px';
        th.style.textAlign = 'left';
        th.style.backgroundColor = '#000000';
        th.style.color = '#FFFFFF';
        th.style.cursor = 'pointer';

        // Sorting event listener on header click
        th.addEventListener('click', () => {
            const isAscending = sortOrder[index] !== true;
            sortOrder[index] = isAscending;
            currentPage = 1; // reset to first page after sort

            // Sort fullData based on the selected header column.
            // We assume each entry is an array in the same order as headers.
            fullData.sort((a, b) => {
                const valueA = a[index] || '';
                const valueB = b[index] || '';
                if (typeof valueA === 'number' && typeof valueB === 'number') {
                    return isAscending ? valueA - valueB : valueB - valueA;
                }
                return isAscending
                    ? String(valueA).localeCompare(String(valueB))
                    : String(valueB).localeCompare(String(valueA));
            });
            renderTable(fullData);
        });

        if (sortOrder[index] !== undefined) {
            th.textContent += sortOrder[index] ? ' ↑' : ' ↓';
        }
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Create rows for the current page's data
    pageData.forEach(entry => {
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

    // --------------------------
    // Create Pagination Controls
    // --------------------------
    const paginationContainer = document.createElement('div');
    paginationContainer.classList.add('pagination');
    paginationContainer.style.display = 'flex';
    paginationContainer.style.justifyContent = 'space-between';
    paginationContainer.style.alignItems = 'center';
    paginationContainer.style.margin = '20px 0';

    // Dropdown for rows per page
    const rowsPerPageSelect = document.createElement('select');
    [32, 64, 96].forEach(num => {
        const option = document.createElement('option');
        option.value = num;
        option.textContent = num;
        if (num === rowsPerPage) option.selected = true;
        rowsPerPageSelect.appendChild(option);
    });
    rowsPerPageSelect.addEventListener('change', (e) => {
        rowsPerPage = parseInt(e.target.value, 10);
        currentPage = 1;
        renderTable(fullData);
    });
    paginationContainer.appendChild(rowsPerPageSelect);

    // Previous button
    const prevButton = document.createElement('button');
    prevButton.textContent = 'Previous';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable(fullData);
        }
    });
    paginationContainer.appendChild(prevButton);

    // Page indicator
    const pageIndicator = document.createElement('span');
    pageIndicator.textContent = `Page ${currentPage} of ${totalPages} (Filtered ${filteredData.length} rows)`;
    paginationContainer.appendChild(pageIndicator);

    // Next button
    const nextButton = document.createElement('button');
    nextButton.textContent = 'Next';
    nextButton.disabled = currentPage === totalPages;
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderTable(fullData);
        }
    });
    paginationContainer.appendChild(nextButton);

    pageContent.appendChild(paginationContainer);
}

snmp();
