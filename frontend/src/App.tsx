import React, { useState } from 'react';
import SessionAnalyser from './components/SessionAnalyser';
import CacheConfigurator from './components/CacheConfigurator';

export default function App() {
  const [configured, setConfigured] = useState(false);

  return (
    <div>
      <h1>FastF1 Browser</h1>
      {configured ? (
        <SessionAnalyser />
      ) : (
        <CacheConfigurator onConfigured={() => setConfigured(true)} />
      )}
    </div>
  );
}
