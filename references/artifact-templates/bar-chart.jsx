import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/*
 * Bar chart template used by agent-skill-creator v6.
 * Phase 2 replaces AGENT_SKILL_DATA with skill-specific data shape
 * instructions describing the category and value columns.
 */

const data = /* AGENT_SKILL_DATA */ [
  { category: 'Sample-A', value: 0 },
  { category: 'Sample-B', value: 0 },
];

export default function SkillBarChart() {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="category" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" />
      </BarChart>
    </ResponsiveContainer>
  );
}
