// src/App.tsx
import React from 'react';
import './App.css';
import ResumeUpload from './components/ResumeUpload/UploadResume';

const App: React.FC = () => {
  return (
    <div className="App">
      <ResumeUpload />
    </div>
  );
};

export default App;
