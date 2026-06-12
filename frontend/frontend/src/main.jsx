import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { BrowserRouter } from 'react-router-dom';

const generateUUID = () =>
  crypto.randomUUID?.() || Math.random().toString(36).substring(2, 15);

if (!document.cookie.includes('client_uuid')) {
  const uuid = generateUUID();
  document.cookie = `client_uuid=${uuid}; path=/; max-age=86400`;
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
