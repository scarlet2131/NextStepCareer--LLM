import React, { useState } from 'react';
import axios from 'axios';
import './UploadResume.css';

const ResumeUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!file) {
      setMessage('Please upload a file.');
      return;
    }

    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/upload-resume', formData);
      setMessage(response.data.message);
    } catch (error) {
      console.error('Error response:', error);
      setMessage('Failed to upload resume.');
    }
  };

  return (
    <div>
      <header className="header">
        <h1>Next Step Career</h1>
      </header>
      <div className="resume-upload-container">
        <h1>Upload Your Resume</h1>
        <form onSubmit={handleSubmit}>
          <input type="file" onChange={handleFileChange} accept=".pdf,.doc,.docx" />
          <button type="submit">Upload</button>
        </form>
        {message && <p>{message}</p>}
      </div>
    </div>
  );
};

export default ResumeUpload;
