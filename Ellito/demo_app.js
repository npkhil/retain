const form = document.getElementById('uploadForm');
const result = document.getElementById('result');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const file = document.getElementById('fileInput').files[0];
  const username = document.getElementById('username').value.trim();
  const fullName = document.getElementById('fullName').value.trim();
  const description = document.getElementById('description').value || '';

  if (!file) {
    result.textContent = 'Choose a file first.';
    return;
  }

  if (!username) {
    result.textContent = 'Enter a username for the database record.';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('username', username);
  formData.append('full_name', fullName || username);
  formData.append('description', description);

  result.textContent = 'Uploading...';

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData
    });

    const payload = await response.json();
    result.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    result.textContent = 'Upload failed: ' + String(error);
  }
});
