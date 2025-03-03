const pageContent = document.getElementById('page-content');
let sortOrder = {};
let currentPage = 1;
let rowsPerPage = 32;
let fullData = [];
// Global filters: array of objects { column: string, query: string }
let filters = [];

// Mapping from header names to functions that extract values from an entry
const filterMapping = {
    "ID": (entry) => entry[0],
    "Timestamp": (entry) => entry[1],
    "Source IP": (entry) => entry[3],
    "Source Port": (entry) => "", // Not provided in the array
    "Destination IP": (entry) => entry[4],
    "Destination Port": (entry) => entry[5],
    "Protocol": (entry) => "TCP/UDP", // Placeholder
    "Alert Message": (entry) => entry[2]
};

async function honeypot() {
    const filesResponse = await fetch('/honeypot-logs');
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

    // Create filter UI container
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

    // Event listeners for filter buttons
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
        // Clear filter rows and filters array
        filterRowsContainer.innerHTML = "";
        filters = [];
        currentPage = 1;
        renderTable(fullData);
        // Optionally add an empty filter row back
        addFilterRow();
    });

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

    // Store full data for later filtering and pagination
    fullData = honeypotData;
    renderTable(fullData);

    // Add event listener to the clear logs button
    clearButton.addEventListener('click', async () => {
        if (confirm("Are you sure you want to clear logs?") == true) {
            statusMessage.textContent = 'Status Message: Clearing Logs... Please wait.';
            clearButton.disabled = true;
            try {
                const response = await fetch('/clear-honeypot', { method: 'POST' });
                if (!response.ok) {
                    throw new Error(`HTTP error: ${response.status}`);
                }
                statusMessage.textContent = 'Status Message: Logs Cleared Successfully!';
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
    // Apply multiple filters if any exist
    let filteredData = data;
    if (filters.length > 0) {
        filteredData = data.filter(entry => {
            return filters.every(f => {
                const value = filterMapping[f.column](entry) || "";
                return value.toString().toLowerCase().includes(f.query.toLowerCase());
            });
        });
    }

    // Clear previous table and pagination controls (but not filter controls)
    const existingTable = pageContent.querySelector('table');
    if (existingTable) existingTable.remove();
    const existingPagination = pageContent.querySelector('.pagination');
    if (existingPagination) existingPagination.remove();

    // Pagination logic: calculate total pages and slice filteredData for the current page
    const totalPages = Math.ceil(filteredData.length / rowsPerPage) || 1;
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    const pageData = filteredData.slice(startIndex, endIndex);

    // Create the table
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
            currentPage = 1; // Reset to first page after sort
            // Sorting logic based on header
            filteredData.sort((a, b) => {
                let valueA, valueB;
                switch (header) {
                    case "ID":
                        valueA = a[0]; valueB = b[0];
                        break;
                    case "Timestamp":
                        valueA = a[1]; valueB = b[1];
                        break;
                    case "Source IP":
                        valueA = a[3]; valueB = b[3];
                        break;
                    case "Source Port":
                        valueA = ""; valueB = "";
                        break;
                    case "Destination IP":
                        valueA = a[4]; valueB = b[4];
                        break;
                    case "Destination Port":
                        valueA = a[5]; valueB = b[5];
                        break;
                    case "Protocol":
                        valueA = "TCP/UDP"; valueB = "TCP/UDP";
                        break;
                    case "Alert Message":
                        valueA = a[2]; valueB = b[2];
                        break;
                    default:
                        valueA = ''; valueB = '';
                }
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

    // Create table rows using the current page's data
    pageData.forEach(entry => {
        const dataRow = document.createElement('tr');
        const rowData = [
            entry[0],              // ID
            entry[1],              // Timestamp
            entry[3],              // Source IP
            '',                    // Source Port (Not provided)
            entry[4],              // Destination IP
            entry[5],              // Destination Port
            'TCP/UDP',             // Protocol (Placeholder)
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

    // Create pagination controls container
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
        renderTable(data);
    });
    paginationContainer.appendChild(rowsPerPageSelect);

    // Previous button
    const prevButton = document.createElement('button');
    prevButton.textContent = 'Previous';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable(data);
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
            renderTable(data);
        }
    });
    paginationContainer.appendChild(nextButton);

    pageContent.appendChild(paginationContainer);
}

honeypot();
