const pageContent = document.getElementById('page-content');
let sortOrder = {};
let currentPage = 1;
let rowsPerPage = 32;
let fullData = [];
let filters = [];
let headers = [];

async function vtResults() {
    // Clear any existing content
    pageContent.innerHTML = '';

    // Header
    const header = document.createElement('h1');
    header.textContent = 'VirusTotal Scan Results';
    pageContent.appendChild(header);

    // Fetch data
    const response = await fetch('/vt-results');
    if (!response.ok) {
        console.error('Error fetching VT results');
        return;
    }
    const data = await response.json();
    headers = data.header_info;
    fullData = data.vt_results;

    // Create filter UI
    const filtersContainer = document.createElement('div');
    filtersContainer.id = 'filters-container';
    const filtersTitle = document.createElement('h4');
    filtersTitle.textContent = 'Filters:';
    filtersContainer.appendChild(filtersTitle);

    const filterRowsContainer = document.createElement('div');
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

    renderTable(fullData);
}

function renderTable(data) {
    // Apply filters
    let filteredData = data;
    if (filters.length) {
        filteredData = data.filter(entry =>
            filters.every(f => {
                const index = headers.indexOf(f.column);
                const val = entry[index] || '';
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

    // Header row
    const headerRow = document.createElement('tr');
    headers.forEach((h, i) => {
        const th = document.createElement('th');
        th.textContent = h + (sortOrder[i] != null ? (sortOrder[i] ? ' ↑' : ' ↓') : '');
        th.addEventListener('click', () => {
            const asc = !sortOrder[i];
            sortOrder[i] = asc;
            data.sort((a, b) => {
                const va = a[i];
                const vb = b[i];
                if (typeof va === 'number' && typeof vb === 'number') {
                    return asc ? va - vb : vb - va;
                }
                return asc
                    ? String(va).localeCompare(String(vb))
                    : String(vb).localeCompare(String(va));
            });
            currentPage = 1;
            renderTable(data);
        });
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);
    const tableContainer = document.createElement('div');
    tableContainer.classList.add('table-container');
    // Data rows
    slice.forEach(entry => {
        const tr = document.createElement('tr');
        entry.forEach(val => {
            const td = document.createElement('td');
            // Special handling for boolean values
            const yesColor = 'var(--rule-disabled-bg)';
            const noColor = 'var(--rule-enabled-bg)';
            if (typeof val === 'boolean') {
                td.textContent = val ? 'Yes' : 'No';
                td.style.color = val ? yesColor : noColor;
            } else {
                td.textContent = val != null ? val : '-';
            }
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
    tableContainer.appendChild(table);
    pageContent.appendChild(tableContainer);
    // pageContent.appendChild(table);

    // Pagination controls
    const pc = document.createElement('div');
    pc.classList.add('pagination');

    const perSelect = document.createElement('select');
    [8, 16, 32, 64, 96].forEach(n => {
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
vtResults();