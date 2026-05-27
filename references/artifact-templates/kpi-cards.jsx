import React from 'react';

/*
 * KPI cards template used by agent-skill-creator v6.
 * Phase 2 replaces AGENT_SKILL_DATA with skill-specific data shape
 * instructions for the cards array.
 */

const cards = /* AGENT_SKILL_DATA */ [
  { label: 'Sample KPI A', value: '0', delta: '+0%' },
  { label: 'Sample KPI B', value: '0', delta: '+0%' },
];

export default function SkillKpiCards() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
      {cards.map((c, i) => (
        <div key={i} style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16 }}>
          <div style={{ fontSize: 12, color: '#6b7280', textTransform: 'uppercase' }}>{c.label}</div>
          <div style={{ fontSize: 28, fontWeight: 600, marginTop: 4 }}>{c.value}</div>
          <div style={{ fontSize: 12, color: '#16a34a', marginTop: 4 }}>{c.delta}</div>
        </div>
      ))}
    </div>
  );
}
