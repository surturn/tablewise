import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import ConfigErrorScreen from './ConfigErrorScreen.tsx';
import { isApiMisconfigured } from './api/client';
import './index.css';

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    void navigator.serviceWorker.register('/sw.js');
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {isApiMisconfigured ? <ConfigErrorScreen /> : <App />}
  </React.StrictMode>,
);
