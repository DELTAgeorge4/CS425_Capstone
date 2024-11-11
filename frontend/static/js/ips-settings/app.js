fetch('/rules')
  .then(response => response.json())
  .then(data => {
    const rulesList = document.getElementById('rules-list');
    // console.log("thelength is: " , data.files.length);
    // console.log("the data is: " , data.files[0]);
    for (let i = 0; i < data.files.length; i++) {
        const file = data.files[i];
        const listItem = document.createElement('option');
        listItem.textContent = file; 
        listItem.value = file; 
        rulesList.appendChild(listItem); 
    }

  })
  .catch(error => console.error("Error fetching rules:", error));

const showRulesButton = document.getElementById('show-rules');

showRulesButton.addEventListener('click', () => {
    // Clear the previous content
    const rulesContent = document.getElementById('rules-content');
    while (rulesContent.firstChild) {
        rulesContent.removeChild(rulesContent.firstChild);
        }
  const rulesList = document.getElementById('rules-list');
  const selectedRule = rulesList.options[rulesList.selectedIndex].value; // Use value instead of label
  console.log(`Selected rule file: ${selectedRule}`);

  // Fetch the content of the selected rule file
  fetch(`/rules/${selectedRule}`)
    .then(response => response.json()) // Ensure it's parsed as JSON
    .then(data => {
      console.log(data[0]); // Log the type of the content
      for (let i = 0; i < data.length; i++) {
        const listItem = document.createElement('li');
        listItem.textContent = data[i];
        document.getElementById('rules-content').appendChild(listItem);
      }
    })
    .catch(error => console.error("Error fetching rule content:", error));
});
