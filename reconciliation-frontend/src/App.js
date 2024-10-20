import React, { useState } from 'react';
import axios from 'axios';


function App() {
  const [sourceFile, setSourceFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);
  const [formatType, setFormatType] = useState('json');
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e, setFile) => {
    setFile(e.target.files[0]);
  };

  const handleFormatChange = (e) => {
    setFormatType(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!sourceFile || !targetFile) {
      setError('Please upload both source and target files.');
      return;
    }

    const formData = new FormData();
    formData.append('source_file', sourceFile);
    formData.append('target_file', targetFile);

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/reconcile/?format=${formatType}`,
        formData,
        {
          responseType:
            formatType === 'csv' || formatType === 'html' ? 'blob' : 'json',
        }
      );

      if (formatType === 'json') {
        setReport(response.data);
      } else {
        const blob = new Blob([response.data], {
          type: formatType === 'csv' ? 'text/csv' : 'text/html',
        });
        const url = URL.createObjectURL(blob);
        window.open(url);
      }

      setError('');
    } catch (err) {
      setError(err.message);
      console.error(err);
    }
  };

  return (
    <div className='App'>
      <h1>CSV Reconciliation Tool</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Upload Source File: </label>
          <input
            type='file'
            accept='.csv'
            onChange={(e) => handleFileChange(e, setSourceFile)}
          />
        </div>
        <div>
          <label>Upload Target File: </label>
          <input
            type='file'
            accept='.csv'
            onChange={(e) => handleFileChange(e, setTargetFile)}
          />
        </div>
        <div>
          <label>Select Format: </label>
          <select value={formatType} onChange={handleFormatChange}>
            <option value='json'>JSON</option>
            <option value='csv'>CSV</option>
            <option value='html'>HTML</option>
          </select>
        </div>
        <button type='submit'>Submit</button>
      </form>

      {error && <p className='error'>{error}</p>}

      {report && formatType === 'json' && (
        <div className='report'>
          <h2>Reconciliation Report</h2>
          <div>
            <h3>Missing in Target:</h3>
            <pre>{JSON.stringify(report.missing_in_target, null, 2)}</pre>
          </div>
          <div>
            <h3>Missing in Source:</h3>
            <pre>{JSON.stringify(report.missing_in_source, null, 2)}</pre>
          </div>
          <div>
            <h3>Discrepancies:</h3>
            <pre>{JSON.stringify(report.discrepancies, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
