import React, { useState } from 'react';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

interface SessionInfo {
  Season: string;
  Round: string;
  Session: string;
  SessionID: string;
}

export default function SessionAnalyser() {
  const { data: sessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => {
      const { data } = await axios.get<SessionInfo[]>('/sessions');
      return data;
    },
  });

  const [year, setYear] = useState('');
  const [race, setRace] = useState('');
  const [sessionId, setSessionId] = useState('');

  const years = Array.from(new Set(sessions?.map(s => s.Season)));
  const races = sessions?.filter(s => s.Season === year);
  const sessionOpts = races?.filter(r => r.Round === race);

  return (
    <div>
      <select value={year} onChange={e => setYear(e.target.value)}>
        <option value="">Year</option>
        {years.map(y => (
          <option key={y}>{y}</option>
        ))}
      </select>

      <select value={race} onChange={e => setRace(e.target.value)} disabled={!year}>
        <option value="">Race</option>
        {races?.map(r => (
          <option key={r.Round}>{r.Round}</option>
        ))}
      </select>

      <select
        value={sessionId}
        onChange={e => setSessionId(e.target.value)}
        disabled={!race}
      >
        <option value="">Session</option>
        {sessionOpts?.map(s => (
          <option key={s.SessionID} value={s.SessionID}>
            {s.Session}
          </option>
        ))}
      </select>

      <button disabled={!sessionId}>Apply</button>
    </div>
  );
}
