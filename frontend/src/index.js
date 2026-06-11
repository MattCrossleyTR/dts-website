import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './app';
import { HashRouter } from 'react-router';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    {/* wrap whole app in router so we have access to useLocation throughout the app */}
    <HashRouter>
      <App />
    </HashRouter>
  </React.StrictMode>
);
