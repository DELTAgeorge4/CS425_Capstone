document.addEventListener('DOMContentLoaded', async function () {
  // Get references to the tabs and content area
  const alertsTab = document.getElementById('ips-alerts');
  const rulesTab = document.getElementById('ips-rules');
  const rightPageContent = document.getElementById('right-page-content');

  // Fetch user role
  const roleDataResponse = await fetch("/role", { method: "GET" });
  const roleData = await roleDataResponse.json();
  const userRole = roleData.Role;

  // Modal elements
  const createRuleModal = document.getElementById('create-rule-modal');
  const createRuleCloseButton = document.getElementById('close-create-rule-modal');

  // Function to clear the content area
  function clearContent() {
    rightPageContent.innerHTML = '';
  }

  // Function to load content into the Rules tab
  async function loadContent() {
    clearContent();

    // Header
    const header = document.createElement('h1');
    header.textContent = 'Available Suricata Rules';
    rightPageContent.appendChild(header);

    // Edit / Save buttons
    const editButton = document.createElement('input');
    editButton.type = 'button';
    editButton.id = 'edit-rules';
    editButton.value = 'Edit Rules';
    rightPageContent.appendChild(editButton);

    const saveButton = document.createElement('input');
    saveButton.type = 'button';
    saveButton.id = 'save-rules';
    saveButton.value = 'Save Rules';
    saveButton.style.display = 'none';
    rightPageContent.appendChild(saveButton);

    // Restart Suricata button
    const restartSuricataButton = document.createElement('input');
    restartSuricataButton.type = 'button';
    restartSuricataButton.id = 'restart-suricata';
    restartSuricataButton.value = 'Restart Suricata';
    rightPageContent.appendChild(restartSuricataButton);

    // Create New Rule button
    const newRuleBtn = document.createElement('input');
    newRuleBtn.type = 'button';
    newRuleBtn.id = 'create-rules';
    newRuleBtn.value = 'Create New Rule';
    // rightPageContent.appendChild(newRuleBtn);

    // Status message area
    const statusMessage = document.createElement('p');
    statusMessage.id = 'statusMessage';
    statusMessage.textContent = 'Status Message: ';
    rightPageContent.appendChild(statusMessage);

    // Container for rule files
    const rulesList = document.createElement('div');
    rulesList.id = 'rules-list';
    rightPageContent.appendChild(rulesList);

    // Handlers
    editButton.addEventListener('click', () => {
      document.querySelectorAll('.file-checkbox').forEach(cb => cb.style.display = 'inline-block');
      saveButton.style.display = 'inline-block';
    });

    saveButton.addEventListener('click', async () => {
      try {
        const checkboxValues = Array.from(document.querySelectorAll('.file-checkbox'))
          .map(cb => cb.checked);
        const resp = await fetch('/checkboxes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ checkBoxList: checkboxValues })
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        await loadContent();
      } catch (e) {
        console.error(e);
      }
    });

    restartSuricataButton.addEventListener('click', async () => {
      if (!confirm("Restart Suricata?")) return;
      statusMessage.textContent = 'Status Message: Restarting Suricata…';
      restartSuricataButton.disabled = true;
      editButton.disabled = true;
      try {
        const resp = await fetch('/restart-suricata', { method: 'POST' });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        statusMessage.textContent = 'Status Message: Suricata restarted!';
      } catch {
        statusMessage.textContent = 'Status Message: Restart failed.';
      } finally {
        setTimeout(() => {
          statusMessage.textContent = 'Status Message: ';
          restartSuricataButton.disabled = false;
          editButton.disabled = false;
        }, 3000);
      }
    });

    newRuleBtn.addEventListener('click', () => createRuleModal.style.display = 'block');
    createRuleCloseButton.addEventListener('click', () => createRuleModal.style.display = 'none');

    // Only admins see edit/restart/create buttons
    if (userRole === 'admin') {
      editButton.style.display = 'inline-block';
      restartSuricataButton.style.display = 'inline-block';
      newRuleBtn.style.display = 'inline-block';
    } else {
      editButton.style.display = 'none';
      restartSuricataButton.style.display = 'none';
      newRuleBtn.style.display = 'none';
    }

    // Fetch and render rule files
    const filesResp = await fetch('/rules');
    if (!filesResp.ok) return console.error('Error fetching rules');
    const { files } = await filesResp.json();

    for (const file of files) {
      const name = parseFileName(file);
      const fileContainer = document.createElement('div');
      fileContainer.classList.add('file-container');

      const collapsible = document.createElement('button');
      collapsible.textContent = name;
      collapsible.classList.add('collapsible');
      fileContainer.appendChild(collapsible);

      const contentDiv = document.createElement('div');
      contentDiv.classList.add('rule-content');
      contentDiv.style.display = 'none';

      // Determine enabled state
      const rulesResp = await fetch(`/rules/${file}`);
      if (!rulesResp.ok) continue;
      const rules = await rulesResp.json();
      const enabled = !rules.some(r => r.type === 'inactive_rule');

      rules.forEach(r => {
        if (r.type !== 'comment') {
          const p = document.createElement('p');
          p.textContent = parseFileRule(r);
          contentDiv.appendChild(p);
        }
      });

      collapsible.addEventListener('click', () => {
        contentDiv.style.display = contentDiv.style.display === 'block' ? 'none' : 'block';
      });

      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.classList.add('file-checkbox');
      cb.checked = enabled;
      cb.style.display = 'none';
      fileContainer.appendChild(cb);

      if (enabled) {
        fileContainer.style.backgroundColor = 'var(--rule-enabled-bg)';
        fileContainer.style.color = 'var(--rule-enabled-text)';
      } else {
        fileContainer.style.backgroundColor = 'var(--rule-disabled-bg)';
        fileContainer.style.color = 'var(--rule-disabled-text)';
        // fileContainer.style.color = '#721c24';
      }
      fileContainer.appendChild(contentDiv);
      rulesList.appendChild(fileContainer);
    }
  }

  // Alerts tab: status & restart for Suricata_to_DB + logs table
  alertsTab.addEventListener('click', async function () {
    clearContent();

    // Header
    const header = document.createElement('h1');
    header.textContent = 'Suricata Alerts';
    rightPageContent.appendChild(header);

    // Container for controls + table
    const container = document.createElement('div');
    container.id = 'alerts-container';
    rightPageContent.appendChild(container);

    // — Status button (everyone) —
    const statusDbBtn = document.createElement('button');
    statusDbBtn.id = 'status-db-btn';
    statusDbBtn.textContent = 'Check Suricata→DB Status';
    statusDbBtn.style.marginRight = '0.5rem';
    container.appendChild(statusDbBtn);

    const statusDbDisplay = document.createElement('span');
    statusDbDisplay.id = 'status-db-display';
    container.appendChild(statusDbDisplay);

    statusDbBtn.addEventListener('click', async () => {
      statusDbDisplay.textContent = '🔄 Checking…';
      try {
        const res = await fetch('/status-suricata-db', {
          method: 'GET',
          credentials: 'include'
        });
        if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
        const { status } = await res.json();
        statusDbDisplay.textContent = status.charAt(0).toUpperCase() + status.slice(1);
      } catch {
        statusDbDisplay.textContent = '❌ Error';
      }
    });

    // — Restart button (admin only) —
    if (userRole === 'admin') {
      const restartDbBtn = document.createElement('button');
      restartDbBtn.id = 'restart-db-btn';
      restartDbBtn.textContent = 'Restart Suricata→DB';
      restartDbBtn.style.marginLeft = '0.5rem';
      container.appendChild(restartDbBtn);

      restartDbBtn.addEventListener('click', async () => {
        if (!confirm('Restart Suricata_to_DB service?')) return;
        restartDbBtn.disabled = true;
        statusDbDisplay.textContent = '⏳ Restarting…';
        try {
          const res = await fetch('/restart-suricata-db', {
            method: 'POST',
            credentials: 'include'
          });
          if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
          statusDbDisplay.textContent = '✅ Restarted';
        } catch (e) {
          statusDbDisplay.textContent = '❌ ' + e.message;
        } finally {
          setTimeout(() => {
            statusDbDisplay.textContent = '';
            restartDbBtn.disabled = false;
          }, 3000);
        }
      });
    }

    // ============= Filters & Table Rendering =============
    // Global state
    let suricataData = [];
    let sortOrderAlerts = {};
    let currentPageAlerts = 1;
    let rowsPerPageAlerts = 32;
    let filtersAlerts = [];

    // Column definitions
    const alertsHeaders = [
      'ID', 'Timestamp', 'Source IP', 'Source Port',
      'Destination IP', 'Destination Port', 'Protocol', 'Alert Message'
    ];
    const alertsFilterMapping = {
      'ID': entry => entry[0],
      'Timestamp': entry => entry[1],
      'Source IP': entry => entry[2],
      'Source Port': entry => entry[3],
      'Destination IP': entry => entry[4],
      'Destination Port': entry => entry[5],
      'Protocol': entry => entry[6],
      'Alert Message': entry => entry[7]
    };

    // Filter UI
    const filtersContainer = document.createElement('div');
    filtersContainer.id = 'alerts-filters-container';
    filtersContainer.style.marginBottom = '20px';
    filtersContainer.style.border = '1px solid #ccc';
    filtersContainer.style.padding = '10px';
    const filtersTitle = document.createElement('h4');
    filtersTitle.textContent = 'Filters:';
    filtersContainer.appendChild(filtersTitle);

    const filterRowsContainer = document.createElement('div');
    filterRowsContainer.id = 'alerts-filter-rows-container';
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

    container.appendChild(filtersContainer);

    function addAlertFilterRow() {
      const row = document.createElement('div');
      row.style.display = 'flex';
      row.style.alignItems = 'center';
      row.style.gap = '5px';
      row.style.marginBottom = '5px';

      const select = document.createElement('select');
      alertsHeaders.forEach(h => {
        const opt = document.createElement('option');
        opt.value = h;
        opt.textContent = h;
        select.appendChild(opt);
      });
      row.appendChild(select);

      const input = document.createElement('input');
      input.type = 'text';
      input.placeholder = 'Enter filter text…';
      row.appendChild(input);

      const rm = document.createElement('button');
      rm.textContent = 'Remove';
      rm.addEventListener('click', () => row.remove());
      row.appendChild(rm);

      filterRowsContainer.appendChild(row);
    }

    addAlertFilterRow();
    addFilterButton.addEventListener('click', addAlertFilterRow);

    applyFiltersButton.addEventListener('click', () => {
      filtersAlerts = [];
      filterRowsContainer.querySelectorAll('div').forEach(row => {
        const col = row.querySelector('select').value;
        const q = row.querySelector('input').value.trim();
        if (q) filtersAlerts.push({ column: col, query: q });
      });
      currentPageAlerts = 1;
      renderAlertsTable(suricataData);
    });

    clearFiltersButton.addEventListener('click', () => {
      filterRowsContainer.innerHTML = '';
      filtersAlerts = [];
      currentPageAlerts = 1;
      renderAlertsTable(suricataData);
      addAlertFilterRow();
    });

    function renderAlertsTable(data) {
      let filtered = data;
      if (filtersAlerts.length) {
        filtered = data.filter(entry =>
          filtersAlerts.every(f => {
            const val = alertsFilterMapping[f.column](entry) || '';
            return val.toString().toLowerCase().includes(f.query.toLowerCase());
          })
        );
      }

      // Remove old table/pagination
      container.querySelectorAll('table, .pagination').forEach(el => el.remove());

      const totalPages = Math.ceil(filtered.length / rowsPerPageAlerts) || 1;
      currentPageAlerts = Math.min(Math.max(1, currentPageAlerts), totalPages);

      const start = (currentPageAlerts - 1) * rowsPerPageAlerts;
      const pageData = filtered.slice(start, start + rowsPerPageAlerts);

      // Build table
      const table = document.createElement('table');
      table.style.width = '100%';
      table.style.borderCollapse = 'collapse';
      table.style.border = '1px solid #ddd';

      const headerRow = document.createElement('tr');
      alertsHeaders.forEach((h, i) => {
        const th = document.createElement('th');
        th.textContent = h + (sortOrderAlerts[i] != null ? (sortOrderAlerts[i] ? ' ↑' : ' ↓') : '');
        th.style.padding = '8px';
        th.style.border = '1px solid #ddd';
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
          const asc = !sortOrderAlerts[i];
          sortOrderAlerts[i] = asc;
          suricataData.sort((a, b) => {
            const va = a[i] ?? '', vb = b[i] ?? '';
            if (typeof va === 'number' && typeof vb === 'number') {
              return asc ? va - vb : vb - va;
            }
            return asc
              ? String(va).localeCompare(vb)
              : String(vb).localeCompare(va);
          });
          currentPageAlerts = 1;
          renderAlertsTable(suricataData);
        });
        headerRow.appendChild(th);
      });
      table.appendChild(headerRow);

      pageData.forEach(rowData => {
        const tr = document.createElement('tr');
        rowData.forEach(val => {
          const td = document.createElement('td');
          td.textContent = val ?? '-';
          td.style.padding = '8px';
          td.style.border = '1px solid #ddd';
          tr.appendChild(td);
        });
        table.appendChild(tr);
      });

      container.appendChild(table);

      // Pagination controls
      const pager = document.createElement('div');
      pager.classList.add('pagination');
      pager.style.display = 'flex';
      pager.style.justifyContent = 'space-between';
      pager.style.alignItems = 'center';
      pager.style.margin = '20px 0';

      const perPageSelect = document.createElement('select');
      [32, 64, 96].forEach(n => {
        const o = document.createElement('option');
        o.value = n;
        o.textContent = n;
        if (n === rowsPerPageAlerts) o.selected = true;
        perPageSelect.appendChild(o);
      });
      perPageSelect.addEventListener('change', e => {
        rowsPerPageAlerts = +e.target.value;
        currentPageAlerts = 1;
        renderAlertsTable(suricataData);
      });
      pager.appendChild(perPageSelect);

      const prev = document.createElement('button');
      prev.textContent = 'Previous';
      prev.disabled = currentPageAlerts === 1;
      prev.addEventListener('click', () => {
        currentPageAlerts--;
        renderAlertsTable(suricataData);
      });
      pager.appendChild(prev);

      const pageInfo = document.createElement('span');
      pageInfo.textContent = `Page ${currentPageAlerts} of ${totalPages} (Filtered ${filtered.length})`;
      pager.appendChild(pageInfo);

      const next = document.createElement('button');
      next.textContent = 'Next';
      next.disabled = currentPageAlerts === totalPages;
      next.addEventListener('click', () => {
        currentPageAlerts++;
        renderAlertsTable(suricataData);
      });
      pager.appendChild(next);

      container.appendChild(pager);
    }

    // Fetch and render Suricata logs
    try {
      const suriResp = await fetch('/suricata-logs');
      if (!suriResp.ok) throw new Error('Failed to fetch logs');
      const suriJson = await suriResp.json();
      suricataData = suriJson.Suricata;
      renderAlertsTable(suricataData);
    } catch (e) {
      console.error(e);
      const errP = document.createElement('p');
      errP.textContent = 'Error loading Suricata alerts.';
      container.appendChild(errP);
    }
  });

  // Wire up the Rules tab
  rulesTab.addEventListener('click', loadContent);

  // Helper functions for parsing and options
  function parseFileName(file) {
    return file.replace('.rules', '').replace(/-/g, ' ');
  }
  function parseFileRule(rule) {
    const isDisabled = rule.type === 'inactive_rule';
    const p = rule.content.split(' ');
    return `Action:${p[0]||'N/A'}, Protocol:${p[1]||'N/A'}, `
      + `Src:${p[2]||'N/A'}:${p[3]||'N/A'} → `
      + `Dst:${p[5]||'N/A'}:${p[6]||'N/A'} `
      + `(${isDisabled?'Disabled':'Enabled'})`;
  }

  const commonRuleOptions = [
    { value: 'content', text: 'content (Content)' },
    { value: 'pcre',    text: 'pcre (Regex)' },
    { value: 'rev',     text: 'rev (Revision)' },
    { value: 'classtype', text: 'classtype (Classification)' }
  ];

  function updateRuleOptions() {
    const selects = document.querySelectorAll('.rule-option');
    const selected = Array.from(selects).map(s => s.value).filter(v => v);
    selects.forEach(select => {
      Array.from(select.options).forEach(opt => {
        if (!opt.value) return;
        opt.disabled = selected.includes(opt.value) && select.value !== opt.value;
      });
    });
    document.getElementById('add-rule-option-btn').disabled =
      selects.length >= commonRuleOptions.length;
  }

  function addRuleOption() {
    const container = document.getElementById('common-rule-options-container');
    if (container.querySelectorAll('.rule-option').length >= commonRuleOptions.length) {
      alert("All options added");
      return;
    }
    const div = document.createElement('div');
    div.className = 'rule-option-container';

    const select = document.createElement('select');
    select.className = 'rule-option';
    const defaultOpt = document.createElement('option');
    defaultOpt.value = '';
    defaultOpt.textContent = 'Select an option';
    select.appendChild(defaultOpt);
    commonRuleOptions.forEach(o => {
      const opt = document.createElement('option');
      opt.value = o.value;
      opt.textContent = o.text;
      select.appendChild(opt);
    });

    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'rule-option-config[]';
    input.placeholder = 'Enter config';
    input.disabled = true;

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'remove-btn';
    removeBtn.textContent = '✕';
    removeBtn.addEventListener('click', () => {
      div.remove();
      updateRuleOptions();
    });

    select.addEventListener('change', () => {
      input.disabled = !select.value;
      if (!select.value) input.value = '';
      updateRuleOptions();
    });

    div.appendChild(select);
    div.appendChild(input);
    div.appendChild(removeBtn);
    container.appendChild(div);
    updateRuleOptions();
  }

  document.getElementById('add-rule-option-btn')
    .addEventListener('click', addRuleOption);

  document.getElementById('advanced-rule-option-btn')
    .addEventListener('click', function () {
      const adv = document.getElementById('advanced-rule-option-container');
      if (!adv.style.display || adv.style.display === 'none') {
        adv.style.display = 'block';
      } else {
        adv.style.display = 'none';
        document.getElementById('advanced-rule-option').value = '';
      }
    });
});
