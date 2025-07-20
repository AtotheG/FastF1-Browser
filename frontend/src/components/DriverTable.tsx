import React from 'react';

export interface DriverRow {
  team: string;
  driver: string;
  tyres: string;
  fastLapRank: number;
  laps: number;
  totalTime: string;
  trackWarnings: number;
  avgStint: number;
  tyreAgeFastest: number;
}

interface Props {
  rows: DriverRow[];
}

export default function DriverTable({ rows }: Props) {
  return (
    <table>
      <thead>
        <tr>
          <th>Team</th>
          <th>Driver</th>
          <th>Tyres</th>
          <th>Fast Lap</th>
          <th>Laps</th>
          <th>Time</th>
          <th>Warnings</th>
          <th>Avg Stint</th>
          <th>Tyre Age</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(r => (
          <tr key={r.driver}>
            <td>{r.team}</td>
            <td>{r.driver}</td>
            <td>{r.tyres}</td>
            <td>{r.fastLapRank}</td>
            <td>{r.laps}</td>
            <td>{r.totalTime}</td>
            <td>{r.trackWarnings}</td>
            <td>{r.avgStint}</td>
            <td>{r.tyreAgeFastest}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
