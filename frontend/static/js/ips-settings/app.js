document.addEventListener('DOMContentLoaded', function () {
  const alertsTab = document.getElementById('ips-alerts');
  const rulesTab = document.getElementById('ips-rules');
  const rightPageContent = document.getElementById('right-page-content');

  function clearContent() {
    rightPageContent.innerHTML = ''; 
  }

  alertsTab.addEventListener('click', function () {
    clearContent();
    const header = document.createElement('h1');
    header.textContent = 'Suricata Alerts';
    rightPageContent.appendChild(header);

    const alertContent = document.createElement('p');
    alertContent.textContent = 'This section will show alerts data from Suricata.';
    rightPageContent.appendChild(alertContent);

    const exampleAlert = document.createElement('p');
    exampleAlert.textContent = 'Alert 1: Example alert details.';
    rightPageContent.appendChild(exampleAlert);
  });

  rulesTab.addEventListener('click', function () {
    clearContent();

    const header = document.createElement('h1');
    header.textContent = 'Available Suricata Rules';
    rightPageContent.appendChild(header);

    const editButton = document.createElement('input');
    editButton.type = 'button';
    editButton.id = 'edit-rules';
    editButton.value = 'Edit Rules';
    rightPageContent.appendChild(editButton);

    const saveButton = document.createElement('input');
    saveButton.type = 'button';
    saveButton.id = 'save-rules';
    saveButton.value = 'Save Rules';
    // Initially hide the save button
    saveButton.style.display = 'none';
    rightPageContent.appendChild(saveButton);

    const rulesList = document.createElement('div');
    rulesList.id = 'rules-list';
    rightPageContent.appendChild(rulesList);

    // Add event listener for edit button after it is created
    editButton.addEventListener('click', function () {
      const checkboxes = document.getElementsByClassName('file-checkbox');
      for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].style.display = 'inline-block'; // Show the checkboxes
      }
      //show the save button
      saveButton.style.display = 'inline-block';
      saveButton.addEventListener('click', function () {
        console.log('Save rules clicked');
        //hide checkboxes
        for (let i = 0; i < checkboxes.length; i++) {
          checkboxes[i].style.display = 'none';
          console.log(checkboxes[i].checked);
        }
        saveButton.style.display = 'none';
      });
      console.log('Edit rules clicked');
    });

    fetch('/rules')
      .then(response => response.json())
      .then(data => {
        for (let i = 0; i < data.files.length; i++) {
          const file = data.files[i];
          const parsedFileName = parseFileName(file);

          const fileContainer = document.createElement('div');
          fileContainer.classList.add('file-container');

          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.classList.add('file-checkbox');
          checkbox.value = file;
          checkbox.id = `checkbox-${i}`;
          checkbox.checked = true;
          checkbox.style.display = 'none'; // Initially hide the checkbox
          fileContainer.appendChild(checkbox);

          const collapsible = document.createElement('button');
          collapsible.textContent = parsedFileName;
          collapsible.classList.add('collapsible');
          fileContainer.appendChild(collapsible);

          const ruleContent = document.createElement('div');
          ruleContent.classList.add('rule-content');
          ruleContent.style.display = 'none';
          fileContainer.appendChild(ruleContent);

          fetch(`/rules/${file}`)
            .then(response => response.json())
            .then(rules => {
              for (let j = 0; j < rules.length; j++) {
                const rule = rules[j];
                if (rule.type !== 'comment') {
                  const parseRule = parseFileRule(rule);

                  const ruleElement = document.createElement('p');
                  ruleElement.textContent = parseRule;
                  ruleContent.appendChild(ruleElement);
                }
              }
            })
            .catch(error => console.error(`Error fetching rules for file ${file}:`, error));

          collapsible.addEventListener('click', function () {
            const isVisible = ruleContent.style.display === 'block';
            ruleContent.style.display = isVisible ? 'none' : 'block';
          });

          rulesList.appendChild(fileContainer);
        }
      })
      .catch(error => console.error('Error fetching rules:', error));
  });

  function parseFileName(file) {
    return file.replace('.rules', '').replace(/-/g, ' ');
  }

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
