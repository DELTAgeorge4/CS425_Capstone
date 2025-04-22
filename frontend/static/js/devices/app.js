const pageContent = document.getElementById('page-content');
let sortOrder = {};
let currentPage = 1;
let rowsPerPage = 32;
let fullData = [];
let filters = [];

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

const filterMapping = {
  "ID": entry => entry[0],
  "Hostname": entry => entry[1],
  "System Uptime": entry => entry[2],
  "CPU Usage": entry => entry[3],
  "RAM Used": entry => entry[4],
  "RAM Total": entry => entry[5],
  "RAM % Used": entry => entry[6],
  "Root Dir Used Storage": entry => entry[7],
  "Root Dir Total Storage": entry => entry[8],
  "Root Dir % Used": entry => entry[9],
  "Timestamp": entry => entry[10]
};

async function snmp() {
  // Fetch data and role
  const filesResponse = await fetch('/snmp-logs');
  const roleData = await (await fetch("/role")).json();
  const userRole = roleData.Role;

  // Clear existing content
  pageContent.innerHTML = '';

  const header = document.createElement('h1');
  header.textContent = 'SNMP Logs';
  pageContent.appendChild(header);

  // — SNMP Collector: Status & Restart Controls —
  const statusSnmpBtn = document.createElement('button');
  statusSnmpBtn.textContent = 'Check SNMP Collector Status';
  statusSnmpBtn.style.marginRight = '0.5rem';
  pageContent.appendChild(statusSnmpBtn);

  const restartSnmpBtn = document.createElement('button');
  restartSnmpBtn.textContent = 'Restart SNMP Collector';
  restartSnmpBtn.style.marginRight = '0.5rem';
  // only admins see restart
  restartSnmpBtn.style.display = userRole === 'admin' ? 'inline-block' : 'none';
  pageContent.appendChild(restartSnmpBtn);

  const snmpStatusDisplay = document.createElement('span');
  pageContent.appendChild(snmpStatusDisplay);

  statusSnmpBtn.addEventListener('click', async () => {
    snmpStatusDisplay.textContent = '🔄 Checking…';
    try {
      const res = await fetch('/status-snmp-collector', {
        method: 'GET',
        credentials: 'include'
      });
      if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
      const { status } = await res.json();
      snmpStatusDisplay.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    } catch (e) {
      console.error(e);
      snmpStatusDisplay.textContent = '❌ Error';
    }
  });

  restartSnmpBtn.addEventListener('click', async () => {
    if (!confirm('Restart SNMP Collector service?')) return;
    restartSnmpBtn.disabled = true;
    snmpStatusDisplay.textContent = '⏳ Restarting…';
    try {
      const res = await fetch('/restart-snmp-collector', {
        method: 'POST',
        credentials: 'include'
      });
      if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
      snmpStatusDisplay.textContent = '✅ Restarted';
    } catch (e) {
      console.error(e);
      snmpStatusDisplay.textContent = '❌ ' + e.message;
    } finally {
      setTimeout(() => {
        snmpStatusDisplay.textContent = '';
        restartSnmpBtn.disabled = false;
      }, 3000);
    }
  });
  // — End SNMP Collector Controls —

  // Clear Logs button
  const clearButton = document.createElement('input');
  clearButton.type = 'button';
  clearButton.value = 'Clear Logs';
  clearButton.style.marginBottom = '20px';
  pageContent.appendChild(clearButton);

  const statusMessage = document.createElement('p');
  statusMessage.id = 'statusMessage';
  statusMessage.textContent = 'Status Message: ';
  statusMessage.style.marginBottom = '20px';
  pageContent.appendChild(statusMessage);

  clearButton.style.display = userRole === "admin" ? "inline-block" : "none";
  clearButton.addEventListener('click', async () => {
    if (!confirm("Are you sure you want to clear logs?")) return;
    statusMessage.textContent = 'Status Message: Clearing Logs...';
    clearButton.disabled = true;
    try {
      const response = await fetch('/clear-snmp', { method: 'POST' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      statusMessage.textContent = 'Status Message: Logs Cleared Successfully!';
      setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
      console.error(error);
      statusMessage.textContent = 'Failed to clear logs.';
      setTimeout(() => statusMessage.textContent = 'Status Message: ', 5000);
    } finally {
      clearButton.disabled = false;
    }
  });

  // Filter UI
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
    row.style.display = 'flex';
    row.style.alignItems = 'center';
    row.style.gap = '5px';
    row.style.marginBottom = '5px';

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

    const rm = document.createElement('button');
    rm.textContent = 'Remove';
    rm.addEventListener('click', () => row.remove());
    row.appendChild(rm);

    filterRowsContainer.appendChild(row);
  }

  addFilterRow();
  addFilterButton.addEventListener('click', addFilterRow);

  applyFiltersButton.addEventListener('click', () => {
    filters = [];
    filterRowsContainer.querySelectorAll('div').forEach(row => {
      const col = row.querySelector('select').value;
      const q = row.querySelector('input').value.trim();
      if (q) filters.push({ column: col, query: q });
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

  // Load data and draw table
  if (!filesResponse.ok) return console.error('Error fetching SNMP data');
  fullData = (await filesResponse.json()).SNMP;
  if (!Array.isArray(fullData)) return console.error('Invalid SNMP data');
  renderTable(fullData);
}

function renderTable(data) {
  let filtered = data;
  if (filters.length) {
    filtered = data.filter(entry =>
      filters.every(f => {
        const val = filterMapping[f.column](entry) || '';
        return val.toString().toLowerCase().includes(f.query.toLowerCase());
      })
    );
  }

  // Remove old table/pagination
  pageContent.querySelectorAll('table, .pagination').forEach(el => el.remove());

  const totalPages = Math.ceil(filtered.length / rowsPerPage) || 1;
  currentPage = Math.min(Math.max(1, currentPage), totalPages);

  const start = (currentPage - 1) * rowsPerPage;
  const slice = filtered.slice(start, start + rowsPerPage);

  const table = document.createElement('table');
  table.style.width = '100%';
  table.style.borderCollapse = 'collapse';
  table.style.border = '1px solid #ddd';

  // Header row
  const hr = document.createElement('tr');
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
        const va = a[i] ?? '', vb = b[i] ?? '';
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
    hr.appendChild(th);
  });
  table.appendChild(hr);

  slice.forEach(row => {
    const tr = document.createElement('tr');
    row.forEach(val => {
      const td = document.createElement('td');
      td.textContent = val ?? '-';
      td.style.padding = '8px';
      td.style.border = '1px solid #ddd';
      tr.appendChild(td);
    });
    table.appendChild(tr);
  });
  pageContent.appendChild(table);

  // Pagination
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
  info.textContent = `Page ${currentPage} of ${totalPages} (Filtered ${filtered.length})`;
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

// Initialize
snmp();
