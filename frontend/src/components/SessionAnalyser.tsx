import React, { useState } from 'react';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

interface SessionInfo {
  year: string;
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
  const [eventName, setEventName] = useState('');
  const [sessionId, setSessionId] = useState('');

  const years = Array.from(new Set(sessions?.map(s => s.year)));
  const events = sessions?.filter(s => s.year === year);
  const sessionOpts = events?.filter(e => e.event_name === eventName);

  return (
    <div>
      <select value={year} onChange={e => setYear(e.target.value)}>
        <option value="">Year</option>
        {years.map(y => (
          <option key={y}>{y}</option>
        ))}
      </select>

      <select value={eventName} onChange={e => setEventName(e.target.value)} disabled={!year}>
        <option value="">Event</option>
        {events?.map(e => (
          <option key={e.event_name}>{e.event_name}</option>
        ))}
      </select>

      <select
        value={sessionId}
        onChange={e => setSessionId(e.target.value)}
        disabled={!eventName}
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
