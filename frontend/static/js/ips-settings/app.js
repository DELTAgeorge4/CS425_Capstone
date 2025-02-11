document.addEventListener('DOMContentLoaded', async function () {
  // Get references to the tabs and content area
  const alertsTab = document.getElementById('ips-alerts');
  const rulesTab = document.getElementById('ips-rules');
  const rightPageContent = document.getElementById('right-page-content');
  const roleDataResponse = await fetch("/role", {method: "GET"});

  const roleData = await roleDataResponse.json();

  const userRole = roleData.Role;
  console.log("Role Data: ", roleData);



  console.log(roleData.Role);
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

    //Create and appned a status message area
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
      if(confirm("Are you sure you want to restart Suricata") == true){
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
    if (userRole === "admin") {  
      editButton.style.display = "inline-block";
      createRuleButton.style.display = "inline-block";
      restartSuricataButton.style.display = "inline-block";
    } else {  
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
  alertsTab.addEventListener('click', async function () {
    clearContent();

    // Create and append header for alerts
    const header = document.createElement('h1');
    header.textContent = 'Suricata Alerts';
    rightPageContent.appendChild(header);

    // Fetch Suricata logs
    try {
        const suricataResponse = await fetch('/suricata-logs');
        if (!suricataResponse.ok) {
            throw new Error('Failed to fetch Suricata logs');
        }
         // Use <pre> for formatted JSON
        const suricata_data = await suricataResponse.json();
        for(let i = 0; i < suricata_data.Suricata.length; i++){
          console.log(suricata_data.Suricata[i]);
          const suricataBox = document.createElement('pre');
          suricataBox.textContent = suricata_data.Suricata[i];
        // console.log(suricata_data);
        // console.log(suricata_string_data);
        rightPageContent.appendChild(suricataBox);
        }
        // Display logs in the content area

        // suricataBox.textContent = suricata_data.Suricata[0];
        // console.log(suricata_data);
        // console.log(suricata_string_data);
        // rightPageContent.appendChild(suricataBox);

    } catch (error) {
        console.error(error);
        const errorMessage = document.createElement('p');
        errorMessage.textContent = 'Error loading Suricata logs. Please try again later.';
        rightPageContent.appendChild(errorMessage);
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
});
