document.addEventListener('DOMContentLoaded', async function () {

  
  // Get references to the tabs and content area
  const alertsTab = document.getElementById('ips-alerts');
  const rulesTab = document.getElementById('ips-rules');
  const rightPageContent = document.getElementById('right-page-content');

  const roleDataResponse = await fetch("/role", { method: "GET" });
  const roleData = await roleDataResponse.json();
  const userRole = roleData.Role;

  const createRuleButton = document.getElementById('create-rules');
  const createRuleModal = document.getElementById('create-rule-modal');
  const createRuleCloseButton = document.getElementById('close-create-rule-modal');


  // Function to clear the content area
  function clearContent() {
    rightPageContent.innerHTML = '';
  }

  // Function to load content into the rules tab
  async function loadContent() {
    clearContent();

    // Create and append header for rules
    const header = document.createElement('h1');
    header.textContent = 'Available Suricata Rules';
    rightPageContent.appendChild(header);

    // Create and append edit button
    const editButton = document.createElement('input');
    editButton.type = 'button';
    editButton.id = 'edit-rules';
    editButton.value = 'Edit Rules';
    rightPageContent.appendChild(editButton);

    // Create and append save button (initially hidden)
    const saveButton = document.createElement('input');
    saveButton.type = 'button';
    saveButton.id = 'save-rules';
    saveButton.value = 'Save Rules';
    saveButton.style.display = 'none';
    rightPageContent.appendChild(saveButton);

    // Create and append restart button
    const restartSuricataButton = document.createElement('input');
    restartSuricataButton.type = 'button';
    restartSuricataButton.id = 'restart-suricata';
    restartSuricataButton.value = 'Restart Suricata';
    rightPageContent.appendChild(restartSuricataButton);

    const createRuleButton = document.createElement('input');
    createRuleButton.type = 'button';
    createRuleButton.id = 'create-rules';
    createRuleButton.value = 'Create New Rule';
    // createRuleButton.style.display = 'none';
    rightPageContent.appendChild(createRuleButton);

    // Create and append status message area
    const statmessage = document.createElement('p');
    statmessage.id = 'statusMessage';
    statmessage.textContent = 'Status Message: ';
    rightPageContent.appendChild(statmessage);

    // Create and append rules list container
    const rulesList = document.createElement('div');
    rulesList.id = 'rules-list';
    rightPageContent.appendChild(rulesList);

    // Event listener for edit button
    editButton.addEventListener('click', function () {
      const checkboxes = document.getElementsByClassName('file-checkbox');
      // Show the checkboxes
      for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].style.display = 'inline-block';
      }
      // Show the save button
      saveButton.style.display = 'inline-block';
      console.log('Edit rules clicked');
    });

    // Event listener for save button
    saveButton.addEventListener('click', async function () {
      try {
        const checkboxes = document.getElementsByClassName('file-checkbox');
        const checkboxValues = Array.from(checkboxes).map(checkbox => checkbox.checked);

        // Send data to the backend
        const response = await fetch('/checkboxes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ checkBoxList: checkboxValues })
        });

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        console.log('Checkbox states saved successfully');
        // Reload content
        loadContent();
      } catch (error) {
        console.error('Error saving checkbox states:', error);
      }
    });

    restartSuricataButton.addEventListener('click', async function() {
      if (confirm("Are you sure you want to restart Suricata") == true) {
        // Show "Restarting Suricata..." message and disable the button
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.textContent = "Status Message: Restarting Suricata... Please wait.";
        restartSuricataButton.disabled = true;
        editButton.disabled = true;
        try {
          const response = await fetch('/restart-suricata', {
            method: 'POST',
          });
          if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
          } else {
            statusMessage.textContent = "Status Message: Suricata restarted successfully!";
            setTimeout(() => statusMessage.textContent = 'Status Message: ', 3000);
          }
        } catch (error) {
          statusMessage.textContent = "Failed to restart Suricata. Please try again later.";
          setTimeout(() => statusMessage.textContent = 'Status Message: ', 5000);
          console.error('Error restarting Suricata:', error);
        } finally {
          restartSuricataButton.disabled = false;
          editButton.disabled = false;
        }
      }
    });

    createRuleButton.addEventListener('click', function() {
      // Show the modal
      createRuleModal.style.display = 'block';
    });
    createRuleCloseButton.addEventListener('click', function() {
      // Hide the modal
      createRuleModal.style.display = 'none';
    });

    if (userRole === "admin") {  
      createRuleButton.style.display = "inline-block";
      editButton.style.display = "inline-block";
      createRuleButton.style.display = "inline-block";
      restartSuricataButton.style.display = "inline-block";
    } else {  
      createRuleButton.style.display = "none";
      editButton.style.display = "none";
      createRuleButton.style.display = "none";
      restartSuricataButton.style.display = "none";
    }

    // Fetch the list of rule files
    const filesResponse = await fetch('/rules');
    if (!filesResponse.ok) {
      console.error('Error fetching rule files');
      return;
    }
    const data = await filesResponse.json();

    // Iterate over each file
    for (const file of data.files) {
      const parsedFileName = parseFileName(file);

      // Create and append file container
      const fileContainer = document.createElement('div');
      fileContainer.classList.add('file-container');

      // Create and append collapsible button
      const collapsible = document.createElement('button');
      collapsible.textContent = parsedFileName;
      collapsible.classList.add('collapsible');
      fileContainer.appendChild(collapsible);

      // Create and append rule content container (initially hidden)
      const ruleContent = document.createElement('div');
      ruleContent.classList.add('rule-content');
      ruleContent.style.display = 'none';


      // Define fileIsEnabled with block scope
      let fileIsEnabled = true;

      // Fetch the rules for the current file
      const rulesResponse = await fetch(`/rules/${file}`);
      if (!rulesResponse.ok) {
        console.error(`Error fetching rules for file ${file}`);
        continue;
      }
      const rules = await rulesResponse.json();

      // Determine fileIsEnabled based on rules
      fileIsEnabled = !rules.some(rule => rule.type === 'inactive_rule');

      // Populate rules into the rule content container
      for (const rule of rules) {
        if (rule.type !== 'comment') {
          const ruleElement = document.createElement('p');
          ruleElement.textContent = parseFileRule(rule);
          ruleContent.appendChild(ruleElement);
        }
      }

      // Event listener for collapsible button
      collapsible.addEventListener('click', function () {
        const isVisible = ruleContent.style.display === 'block';
        ruleContent.style.display = isVisible ? 'none' : 'block';
      });

      // Create and append checkbox (initially hidden)
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.classList.add('file-checkbox');
      checkbox.value = file;
      checkbox.id = `checkbox-${file}`;
      checkbox.checked = fileIsEnabled;
      checkbox.style.display = 'none';
      fileContainer.appendChild(checkbox);
      fileContainer.appendChild(ruleContent);

      rulesList.appendChild(fileContainer);
      
    }
  }

  // Updated alertsTab event listener to display Suricata Alerts as a table with sorting, pagination, and multi-filtering.
  alertsTab.addEventListener('click', async function () {
    clearContent();

    // Create and append header for alerts
    const header = document.createElement('h1');
    header.textContent = 'Suricata Alerts';
    rightPageContent.appendChild(header);

    // Create container for alerts table and controls
    const container = document.createElement('div');
    container.id = 'alerts-container';
    rightPageContent.appendChild(container);

    // Global state for alerts table
    let suricataData = [];
    let sortOrderAlerts = {};
    let currentPageAlerts = 1;
    let rowsPerPageAlerts = 32;
    let filtersAlerts = [];

    // Define headers for alerts table
    const alertsHeaders = [
      'ID',
      'Timestamp',
      'Source IP',
      'Source Port',
      'Destination IP',
      'Destination Port',
      'Protocol',
      'Alert Message'
    ];

    // Mapping from header to value extractor for alerts
    const alertsFilterMapping = {
      "ID": entry => entry[0],
      "Timestamp": entry => entry[1],
      "Source IP": entry => entry[2],
      "Source Port": entry => entry[3],
      "Destination IP": entry => entry[4],
      "Destination Port": entry => entry[5],
      "Protocol": entry => entry[6],
      "Alert Message": entry => entry[7]
    };

    // Multi-Filter UI for alerts
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
      row.style.marginBottom = '5px';
      row.style.display = 'flex';
      row.style.alignItems = 'center';
      row.style.gap = '5px';
      const select = document.createElement('select');
      alertsHeaders.forEach(header => {
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
    addAlertFilterRow();
    addFilterButton.addEventListener('click', () => {
      addAlertFilterRow();
    });
    applyFiltersButton.addEventListener('click', () => {
      filtersAlerts = [];
      const rows = filterRowsContainer.querySelectorAll('div');
      rows.forEach(row => {
        const select = row.querySelector('select');
        const input = row.querySelector('input');
        const column = select.value;
        const query = input.value.trim();
        if (query !== "") {
          filtersAlerts.push({ column, query });
        }
      });
      currentPageAlerts = 1;
      renderAlertsTable(suricataData);
    });
    clearFiltersButton.addEventListener('click', () => {
      filterRowsContainer.innerHTML = "";
      filtersAlerts = [];
      currentPageAlerts = 1;
      renderAlertsTable(suricataData);
      addAlertFilterRow();
    });

    function renderAlertsTable(data) {
      let filteredData = data;
      if (filtersAlerts.length > 0) {
        filteredData = data.filter(entry => {
          return filtersAlerts.every(f => {
            const value = alertsFilterMapping[f.column](entry) || "";
            return value.toString().toLowerCase().includes(f.query.toLowerCase());
          });
        });
      }
      const existingTable = container.querySelector('table');
      if (existingTable) existingTable.remove();
      const existingPagination = container.querySelector('.pagination');
      if (existingPagination) existingPagination.remove();
      const totalPages = Math.ceil(filteredData.length / rowsPerPageAlerts) || 1;
      if (currentPageAlerts > totalPages) currentPageAlerts = totalPages;
      if (currentPageAlerts < 1) currentPageAlerts = 1;
      const startIndex = (currentPageAlerts - 1) * rowsPerPageAlerts;
      const endIndex = startIndex + rowsPerPageAlerts;
      const pageData = filteredData.slice(startIndex, endIndex);
      const table = document.createElement('table');
      table.style.borderCollapse = 'collapse';
      table.style.width = '100%';
      table.style.margin = '20px 0';
      table.style.border = '1px solid #ddd';
      const headerRow = document.createElement('tr');
      alertsHeaders.forEach((header, index) => {
        const th = document.createElement('th');
        th.textContent = header;
        th.style.border = '1px solid #ddd';
        th.style.padding = '8px';
        th.style.textAlign = 'left';
        th.style.backgroundColor = '#000';
        th.style.color = '#fff';
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
          const isAscending = sortOrderAlerts[index] !== true;
          sortOrderAlerts[index] = isAscending;
          currentPageAlerts = 1;
          suricataData.sort((a, b) => {
            const valueA = a[index] || '';
            const valueB = b[index] || '';
            if (typeof valueA === 'number' && typeof valueB === 'number') {
              return isAscending ? valueA - valueB : valueB - valueA;
            }
            return isAscending
              ? String(valueA).localeCompare(String(valueB))
              : String(valueB).localeCompare(String(valueA));
          });
          renderAlertsTable(suricataData);
        });
        if (sortOrderAlerts[index] !== undefined) {
          th.textContent += sortOrderAlerts[index] ? ' ↑' : ' ↓';
        }
        headerRow.appendChild(th);
      });
      table.appendChild(headerRow);
      pageData.forEach(entry => {
        const row = document.createElement('tr');
        entry.forEach(value => {
          const td = document.createElement('td');
          td.textContent = value || '-';
          td.style.border = '1px solid #ddd';
          td.style.padding = '8px';
          row.appendChild(td);
        });
        table.appendChild(row);
      });
      container.appendChild(table);
      const paginationContainer = document.createElement('div');
      paginationContainer.classList.add('pagination');
      paginationContainer.style.display = 'flex';
      paginationContainer.style.justifyContent = 'space-between';
      paginationContainer.style.alignItems = 'center';
      paginationContainer.style.margin = '20px 0';
      const rowsPerPageSelect = document.createElement('select');
      [32, 64, 96].forEach(num => {
        const option = document.createElement('option');
        option.value = num;
        option.textContent = num;
        if (num === rowsPerPageAlerts) option.selected = true;
        rowsPerPageSelect.appendChild(option);
      });
      rowsPerPageSelect.addEventListener('change', (e) => {
        rowsPerPageAlerts = parseInt(e.target.value, 10);
        currentPageAlerts = 1;
        renderAlertsTable(suricataData);
      });
      paginationContainer.appendChild(rowsPerPageSelect);
      const prevButton = document.createElement('button');
      prevButton.textContent = 'Previous';
      prevButton.disabled = currentPageAlerts === 1;
      prevButton.addEventListener('click', () => {
        if (currentPageAlerts > 1) {
          currentPageAlerts--;
          renderAlertsTable(suricataData);
        }
      });
      paginationContainer.appendChild(prevButton);
      const pageIndicator = document.createElement('span');
      pageIndicator.textContent = `Page ${currentPageAlerts} of ${totalPages} (Filtered ${filteredData.length} rows)`;
      paginationContainer.appendChild(pageIndicator);
      const nextButton = document.createElement('button');
      nextButton.textContent = 'Next';
      nextButton.disabled = currentPageAlerts === totalPages;
      nextButton.addEventListener('click', () => {
        if (currentPageAlerts < totalPages) {
          currentPageAlerts++;
          renderAlertsTable(suricataData);
        }
      });
      paginationContainer.appendChild(nextButton);
      container.appendChild(paginationContainer);
    }

    try {
      const suricataResponse = await fetch('/suricata-logs');
      if (!suricataResponse.ok) {
        throw new Error('Failed to fetch Suricata logs');
      }
      const suricataJson = await suricataResponse.json();
      suricataData = suricataJson.Suricata;
      renderAlertsTable(suricataData);
    } catch (error) {
      console.error(error);
      const errorMessage = document.createElement('p');
      errorMessage.textContent = 'Error loading Suricata alerts. Please try again later.';
      container.appendChild(errorMessage);
    }
  });

  // Event listener for the rules tab
  rulesTab.addEventListener('click', loadContent);

  // Function to parse file name
  function parseFileName(file) {
    return file.replace('.rules', '').replace(/-/g, ' ');
  }

  // Function to parse file rule
  function parseFileRule(rule) {
    const isDisabled = rule.type === 'inactive_rule';
    const ruleContent = rule.content;
    const parts = ruleContent.split(' ');
    const action = parts[0] || 'N/A';
    const protocol = parts[1] || 'N/A';
    const srcAddress = parts[2] || 'N/A';
    const srcPort = parts[3] || 'N/A';
    const direction = parts[4] || 'N/A';
    const destAddress = parts[5] || 'N/A';
    const destPort = parts[6] || 'N/A';
    return `Action:${action}, Protocol:${protocol}, Source Address:${srcAddress}, Source Port:${srcPort}, Destination Address:${destAddress}, Destination Port:${destPort}, Status:${isDisabled ? 'Disabled' : 'Enabled'}`;
  }

  // Define common rule options (excluding 'sid' since it's auto-generated)
const commonRuleOptions = [
  { value: 'content', text: 'content (Content)' },
  { value: 'pcre', text: 'pcre (Regular Expression)' },
  { value: 'rev', text: 'rev (Revision)' },
  { value: 'classtype', text: 'classtype (Classification)' }
];

// Update each dropdown to disable options already selected in other rows
function updateRuleOptions() {
  const selects = document.querySelectorAll('.rule-option');
  const selectedValues = Array.from(selects)
    .map(select => select.value)
    .filter(val => val !== "");
  selects.forEach(select => {
    Array.from(select.options).forEach(option => {
      if (option.value === "") return;
      option.disabled = (selectedValues.includes(option.value) && select.value !== option.value);
    });
  });
  // Disable the "Add Rule Option" button if all options are already added
  const addBtn = document.getElementById('add-rule-option-btn');
  addBtn.disabled = (selects.length >= commonRuleOptions.length);
}

// Add a new rule option row (dropdown + config input + remove button)
function addRuleOption() {
  const container = document.getElementById('common-rule-options-container');
  const existingSelects = container.querySelectorAll('.rule-option');
  if (existingSelects.length >= commonRuleOptions.length) {
    alert("All available rule options have been added.");
    return;
  }
  const div = document.createElement('div');
  div.className = 'rule-option-container';

  // Create the dropdown select element
  const select = document.createElement('select');
  select.className = 'rule-option';
  select.name = 'rule-option[]';
  const defaultOption = document.createElement('option');
  defaultOption.value = "";
  defaultOption.text = "Select an option";
  select.appendChild(defaultOption);
  commonRuleOptions.forEach(opt => {
    const option = document.createElement('option');
    option.value = opt.value;
    option.text = opt.text;
    select.appendChild(option);
  });

  // Create the text input for the configuration
  const input = document.createElement('input');
  input.type = 'text';
  input.name = 'rule-option-config[]';
  input.placeholder = 'Enter configuration';
  input.disabled = true;

  // Create the remove button for this row
  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'remove-btn';
  removeBtn.textContent = '✕';
  removeBtn.addEventListener('click', function () {
    div.remove();
    updateRuleOptions();
  });

  // Enable the config input when a valid option is selected
  select.addEventListener('change', function () {
    if (select.value === "") {
      input.value = "";
      input.disabled = true;
    } else {
      input.disabled = false;
    }
    updateRuleOptions();
  });

  div.appendChild(select);
  div.appendChild(input);
  div.appendChild(removeBtn);
  container.appendChild(div);
  updateRuleOptions();
}

// Attach event listener to the "Add Rule Option" button
document.getElementById('add-rule-option-btn').addEventListener('click', addRuleOption);

// Advanced Rule Option Toggle
document.getElementById('advanced-rule-option-btn').addEventListener('click', function () {
  const advContainer = document.getElementById('advanced-rule-option-container');
  if (advContainer.style.display === 'none' || advContainer.style.display === '') {
    advContainer.style.display = 'block';
  } else {
    advContainer.style.display = 'none';
    document.getElementById('advanced-rule-option').value = "";
  }
});

});
