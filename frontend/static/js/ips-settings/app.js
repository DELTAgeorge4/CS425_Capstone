document.addEventListener('DOMContentLoaded', function () {
  // Get references to the tabs and content area
  const alertsTab = document.getElementById('ips-alerts');
  const rulesTab = document.getElementById('ips-rules');
  const rightPageContent = document.getElementById('right-page-content');

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

    //Create and appned a status message area
    const statmessage = document.createElement('p');
    statmessage.id = 'statusMessage';
    statmessage.textContent = '*';
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
      // Show "Restarting Suricata..." message and disable the button
      const statusMessage = document.getElementById('statusMessage');
      statusMessage.textContent = "Restarting Suricata... Please wait.";
      restartSuricataButton.disabled = true;
    
      try {
        const response = await fetch('/restart-suricata', {
          method: 'POST',
        });
    
        
        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        } else {
          
          statusMessage.textContent = "Suricata restarted successfully!";
          setTimeout(() => statusMessage.textContent = '', 3000); 
        }
      } catch (error) {

        statusMessage.textContent = "Failed to restart Suricata. Please try again later.";
        setTimeout(() => statusMessage.textContent = '', 5000); 
        console.error('Error restarting Suricata:', error);
      } finally {
        
        restartSuricataButton.disabled = false;
      }
    });
    
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
      fileContainer.appendChild(ruleContent);

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

      rulesList.appendChild(fileContainer);
    }
  }

  // Event listener for the alerts tab
  alertsTab.addEventListener('click', function () {
    clearContent();
    // Create and append header for alerts
    const header = document.createElement('h1');
    header.textContent = 'Suricata Alerts';
    rightPageContent.appendChild(header);

    // Create and append alert content
    const alertContent = document.createElement('p');
    alertContent.textContent = 'This section will show alerts data from Suricata.';
    rightPageContent.appendChild(alertContent);

    // Create and append example alert
    const exampleAlert = document.createElement('p');
    exampleAlert.textContent = 'Alert 1: Example alert details.';
    rightPageContent.appendChild(exampleAlert);
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
});
