import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './app';
import { BrowserRouter } from 'react-router-dom';
import { BASE_URL } from './constants';

const root = ReactDOM.createRoot(document.getElementById('root'));
console.log("BAEURL", BASE_URL)
root.render(
  <React.StrictMode>
    {/* wrap whole app in router so we have access to useLocation throughout the app */}
    <BrowserRouter basename={BASE_URL}>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
