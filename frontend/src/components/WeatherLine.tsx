import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

interface WeatherPoint {
  SessionTime: number;
  AirTemp: number;
  Rainfall: boolean;
}

interface Props {
  data: WeatherPoint[];
}

export default function WeatherLine({ data }: Props) {
  return (
    <LineChart width={400} height={200} data={data}>
      <XAxis dataKey="SessionTime" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="AirTemp" stroke="#8884d8" />
    </LineChart>
  );
}
