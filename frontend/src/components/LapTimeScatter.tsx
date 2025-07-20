import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip } from 'recharts';

interface LapPoint {
  Team: string;
  Driver: string;
  LapTime: number;
}

interface Props {
  data: LapPoint[];
}

export default function LapTimeScatter({ data }: Props) {
  return (
    <ScatterChart width={400} height={300} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
      <XAxis type="category" dataKey="Team" />
      <YAxis dataKey="LapTime" />
      <Tooltip />
      <Scatter data={data} fill="#8884d8" />
    </ScatterChart>
  );
}
