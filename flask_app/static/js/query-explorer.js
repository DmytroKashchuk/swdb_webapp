const textarea = document.getElementById('sql-input');
const runButton = document.getElementById('run-query');
const statusText = document.getElementById('status-text');
const resultSummary = document.getElementById('result-summary');
const downloadCsv = document.getElementById('download-csv');
const downloadJson = document.getElementById('download-json');
const chips = document.querySelectorAll('.chip');

const table = new Tabulator('#results-table', {
  layout: 'fitDataStretch',
  height: '540px',
  placeholder: 'Results will appear here after you run a query.',
  pagination: false,
  reactiveData: true,
  columnDefaults: {
    headerSort: true,
    sorter: 'string',
  },
});

chips.forEach((chip) => {
  chip.addEventListener('click', () => {
    textarea.value = chip.dataset.query;
    textarea.focus();
  });
});

textarea.addEventListener('keydown', (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    runQuery();
  }
});

runButton.addEventListener('click', () => runQuery());

downloadCsv.addEventListener('click', () => {
  table.download('csv', 'swdb-query.csv');
});

downloadJson.addEventListener('click', () => {
  const data = table.getData();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'swdb-query.json';
  anchor.click();
  URL.revokeObjectURL(url);
});

async function runQuery() {
  const query = textarea.value.trim();
  if (!query) {
    updateStatus('Please enter a query first.', 'warn');
    return;
  }

  setRunningState(true);

  try {
    const response = await fetch('/api/run-query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || 'Query failed.');
    }

    const columns = (payload.columns || []).map((column) => ({
      title: column,
      field: column,
      headerHozAlign: 'left',
    }));

    if (!columns.length) {
      table.clearData();
      table.setColumns([]);
      resultSummary.textContent = 'Query succeeded but returned no rows.';
      updateStatus('Query finished with 0 rows.', 'ok');
    } else {
      table.setColumns(columns);
      table.setData(payload.rows || []);
      resultSummary.textContent = buildSummary(payload);
      updateStatus('Query finished successfully.', 'ok');
      toggleDownloads(true);
    }
  } catch (error) {
    table.clearData();
    table.setColumns([]);
    resultSummary.textContent = error.message;
    updateStatus(error.message, 'error');
    toggleDownloads(false);
  } finally {
    setRunningState(false);
  }
}

function buildSummary(payload) {
  const parts = [`${payload.row_count || 0} rows`, `${payload.elapsed_ms || 0} ms`];
  if (payload.truncated) {
    parts.push('capped at max rows');
  }
  return parts.join(' • ');
}

function updateStatus(message, variant = 'info') {
  statusText.textContent = message;
  statusText.dataset.variant = variant;
}

function setRunningState(isRunning) {
  runButton.disabled = isRunning;
  downloadCsv.disabled = isRunning;
  downloadJson.disabled = isRunning;
  if (isRunning) {
    statusText.textContent = 'Running query…';
    statusText.dataset.variant = 'info';
  }
}

function toggleDownloads(enabled) {
  downloadCsv.disabled = !enabled;
  downloadJson.disabled = !enabled;
}
