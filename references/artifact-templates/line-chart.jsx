import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/*
 * Line chart template used by agent-skill-creator v6.
 *
 * Phase 2 inlines this file into a generated SKILL.md and replaces the
 * AGENT_SKILL_DATA marker with skill-specific instructions describing
 * how the skill should populate the `data` array (column names, units,
 * source).
 */

const data = /* AGENT_SKILL_DATA */ [
  { period: 'Sample-1', value: 0 },
  { period: 'Sample-2', value: 0 },
];

export default function SkillLineChart() {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="period" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
