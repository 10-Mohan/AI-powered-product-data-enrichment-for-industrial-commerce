document.addEventListener('DOMContentLoaded', () => {
    const extractBtn = document.getElementById('extract-btn');
    const enrichBtn = document.getElementById('enrich-btn');
    const saveBtn = document.getElementById('save-btn');
    const rawTextInput = document.getElementById('raw-text');
    const jsonOutput = document.getElementById('json-output');
    const statusMessage = document.getElementById('status-message');

    function showStatus(message, isError = false) {
        statusMessage.textContent = message;
        statusMessage.className = isError ? 'error' : 'success';
        statusMessage.style.display = 'block';
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 5000);
    }

    extractBtn.addEventListener('click', async () => {
        const text = rawTextInput.value.trim();
        if (!text) {
            showStatus('Please enter some raw text first.', true);
            return;
        }

        extractBtn.textContent = 'Extracting...';
        extractBtn.disabled = true;
        jsonOutput.value = '';
        enrichBtn.disabled = true;
        saveBtn.disabled = true;

        try {
            const response = await fetch('/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ raw_text: text })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to extract data');
            }

            const data = await response.json();
            jsonOutput.value = JSON.stringify(data, null, 2);
            enrichBtn.disabled = false;
            saveBtn.disabled = false;
            showStatus('Extraction successful!');
        } catch (error) {
            showStatus(`Error: ${error.message}`, true);
        } finally {
            extractBtn.textContent = 'Extract Data';
            extractBtn.disabled = false;
        }
    });

    enrichBtn.addEventListener('click', async () => {
        const jsonStr = jsonOutput.value.trim();
        if (!jsonStr) return;

        let parsedData;
        try {
            parsedData = JSON.parse(jsonStr);
        } catch (e) {
            showStatus('Invalid JSON format. Please correct it before enriching.', true);
            return;
        }

        enrichBtn.textContent = 'Enriching...';
        enrichBtn.disabled = true;
        saveBtn.disabled = true;

        try {
            const response = await fetch('/enrich', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(parsedData)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to enrich data');
            }

            const data = await response.json();
            jsonOutput.value = JSON.stringify(data, null, 2);
            showStatus('Enrichment successful!');
        } catch (error) {
            showStatus(`Error enriching: ${error.message}`, true);
        } finally {
            enrichBtn.textContent = 'Enrich Data';
            enrichBtn.disabled = false;
            saveBtn.disabled = false;
        }
    });

    saveBtn.addEventListener('click', async () => {
        const jsonStr = jsonOutput.value.trim();
        if (!jsonStr) return;

        let parsedData;
        try {
            parsedData = JSON.parse(jsonStr);
        } catch (e) {
            showStatus('Invalid JSON format. Please correct it before saving.', true);
            return;
        }

        saveBtn.textContent = 'Saving...';
        saveBtn.disabled = true;

        try {
            const response = await fetch('/products', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(parsedData)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(JSON.stringify(errData.detail) || 'Failed to save data');
            }

            showStatus('Product saved successfully to database!');
        } catch (error) {
            showStatus(`Error saving: ${error.message}`, true);
            saveBtn.disabled = false;
        } finally {
            saveBtn.textContent = 'Save to Database';
        }
    });
});
