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

  const rulesList = document.createElement('div');
  rulesList.id = 'rules-list';
  rightPageContent.appendChild(rulesList);

  fetch('/rules')
    .then(response => response.json())
    .then(data => {
      for (let i = 0; i < data.files.length; i++) {
        const file = data.files[i];
        const parsedFileName = parseFileName(file);


        const collapsible = document.createElement('button');
        collapsible.textContent = parsedFileName;
        collapsible.classList.add('collapsible');
        rulesList.appendChild(collapsible);


        const ruleContent = document.createElement('div');
        ruleContent.classList.add('rule-content');
        ruleContent.style.display = 'none'; // Start hidden

        fetch(`/rules/${file}`)
          .then(response => response.json())
          .then(rules => {
            for (let j = 0; j < rules.length; j++) {
              const rule = rules[j];
              const parseRule = parseFileRule(rule);

              const checkbox = document.createElement('input');
              checkbox.type = 'checkbox';
              checkbox.id = `ruleCheckbox-${i}-${j}`;
              checkbox.name = 'ruleCheckbox';
              checkbox.value = rule;
              checkbox.checked = !rule.startsWith('#');

              const ruleElement = document.createElement('p');
              ruleElement.setAttribute('for', `ruleCheckbox-${i}-${j}`);
              ruleElement.textContent = parseRule;

              ruleElement.insertAdjacentElement('afterbegin', checkbox);
              ruleContent.appendChild(ruleElement);
            }
          })
          .catch(error => console.error(`Error fetching rules for file ${file}:`, error));

        rulesList.appendChild(ruleContent);

        collapsible.addEventListener('click', function () {
          const isVisible = ruleContent.style.display === 'block';
          ruleContent.style.display = isVisible ? 'none' : 'block';
        });
      }
    })
    .catch(error => console.error('Error fetching rules:', error));
});

function parseFileName(file) {
  return file.replace('.rules', '').replace(/-/g, ' ');
}

function parseFileRule(rule) {
  const isDisabled = rule.startsWith('#');
  const status = isDisabled ? 'disabled' : 'active';

  if (isDisabled) {
    rule = rule.slice(1).trim();
  }

  const parts = rule.split(' ');
  const action = parts[0] || 'N/A';
  const protocol = parts[1] || 'N/A';
  const srcAddress = parts[2] || 'N/A';
  const srcPort = parts[3] || 'N/A';
  const direction = parts[4] || 'N/A';
  const destAddress = parts[5] || 'N/A';
  const destPort = parts[6] || 'N/A';

  const optionsStartIndex = rule.indexOf('(');
  const optionsEndIndex = rule.lastIndexOf(')');
  const options = optionsStartIndex !== -1 && optionsEndIndex !== -1
    ? rule.slice(optionsStartIndex + 1, optionsEndIndex)
    : '';

  return `action:${action}, protocol:${protocol}, src:${srcAddress}:${srcPort}, dest:${destAddress}:${destPort}, state:${status}`;
}
