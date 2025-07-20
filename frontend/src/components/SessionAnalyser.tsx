import React, { useState } from 'react';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

interface SessionInfo {
  year: number;
  event_name: string;
  session_type: string;
  session_id: string;
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

  const years = Array.from(
    new Set((sessions ?? []).map(s => String(s.year)))
  );
  const races = Array.from(
    new Set(
      (sessions ?? [])
        .filter(s => String(s.year) === year)
        .map(s => s.event_name)
    )
  );
  const sessionOpts = (sessions ?? []).filter(
    s => String(s.year) === year && s.event_name === race
  );

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
        {races.map(r => (
          <option key={r}>{r}</option>
        ))}
      </select>

      <select
        value={sessionId}
        onChange={e => setSessionId(e.target.value)}
        disabled={!race}
      >
        <option value="">Session</option>
        {sessionOpts?.map(s => (
          <option key={s.session_id} value={s.session_id}>
            {s.session_type}
          </option>
        ))}
      </select>

      <button disabled={!sessionId}>Apply</button>
    </div>
  );
}
