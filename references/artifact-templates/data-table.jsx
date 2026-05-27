import React from 'react';

/*
 * Data table template used by agent-skill-creator v6 as the baseline
 * artifact when data is structured but no chart fits.
 * Phase 2 replaces AGENT_SKILL_DATA with skill-specific column and
 * row instructions.
 */

const table = /* AGENT_SKILL_DATA */ {
  columns: ['Column A', 'Column B', 'Column C'],
  rows: [
    ['Sample', 0, ''],
    ['Sample', 0, ''],
  ],
};

export default function SkillDataTable() {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
        <thead>
          <tr>
            {table.columns.map((c) => (
              <th key={c} style={{ textAlign: 'left', padding: 8, borderBottom: '2px solid #e5e7eb' }}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j} style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{String(cell)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
