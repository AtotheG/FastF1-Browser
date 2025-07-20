import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip } from 'recharts';

interface PacePoint {
  SessionTime: number;
  LapTime: number;
  Team: string;
}

interface Props {
  data: PacePoint[];
}

export default function PaceVsTimeScatter({ data }: Props) {
  return (
    <ScatterChart width={400} height={300} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
      <XAxis dataKey="SessionTime" />
      <YAxis dataKey="LapTime" />
      <Tooltip />
      <Scatter data={data} fill="#82ca9d" />
    </ScatterChart>
  );
}
