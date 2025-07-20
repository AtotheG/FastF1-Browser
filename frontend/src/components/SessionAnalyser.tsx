import React, { useState, useMemo } from 'react';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

interface SessionInfo {
  year: string;
  event_name: string;
  session_type: string;
  session_id: string;
  sid?: string;
}

interface Props {
  onApply?: (session: SessionInfo) => void;
}

const SessionAnalyser: React.FC<Props> = ({ onApply }) => {
  const { data: sessions = [], isLoading, isError } = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => {
      const { data } = await axios.get<SessionInfo[]>('/sessions');
      return data;
    },
  });

  const [year, setYear] = useState('');
  const [eventName, setEventName] = useState('');
  const [sessionId, setSessionId] = useState('');

  // Distinct years (sorted descending for convenience)
  const years = useMemo(
    () =>
      Array.from(new Set(sessions.map(s => s.year)))
        .sort()
        .reverse(),
    [sessions]
  );

  // Distinct events for the chosen year
  const events = useMemo(
    () =>
      Array.from(
        new Set(
            sessions
              .filter(s => s.year === year)
              .map(s => s.event_name)
        )
      ).sort(),
    [sessions, year]
  );

  // Session options for chosen event
  const sessionOpts = useMemo(
    () =>
      sessions.filter(
        s => s.year === year && s.event_name === eventName
      ),
    [sessions, year, eventName]
  );

  const selectedSession = sessionOpts.find(s => s.session_id === sessionId);

  function handleYearChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const newYear = e.target.value;
    setYear(newYear);
    setEventName('');
    setSessionId('');
  }

  function handleEventChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const ev = e.target.value;
    setEventName(ev);
    setSessionId('');
  }

  function handleApply() {
    if (selectedSession && onApply) {
      onApply(selectedSession);
    }
  }

  return (
    <div className="space-y-2">
      {isLoading && <div>Loading sessions…</div>}
      {isError && <div className="text-red-600">Failed to load sessions.</div>}

      <div className="flex gap-2">
        <select value={year} onChange={handleYearChange}>
          <option value="">Year</option>
          {years.map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>

        <select
          value={eventName}
            onChange={handleEventChange}
            disabled={!year}
        >
          <option value="">Event</option>
          {events.map(ev => (
            <option key={ev} value={ev}>{ev}</option>
          ))}
        </select>

        <select
          value={sessionId}
          onChange={e => setSessionId(e.target.value)}
          disabled={!eventName}
        >
          <option value="">Session</option>
          {sessionOpts.map(s => (
            <option key={s.session_id} value={s.session_id}>
              {s.session_type}
            </option>
          ))}
        </select>

        <button
          onClick={handleApply}
          disabled={!sessionId}
        >
          Apply
        </button>
      </div>
    </div>
  );
};

export default SessionAnalyser;
