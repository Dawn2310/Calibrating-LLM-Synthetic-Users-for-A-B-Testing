import React from 'react';

/* Custom chart tooltip used across pages */
export const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#12121a',
      border: '1px solid rgba(255,255,255,0.12)',
      borderRadius: '10px',
      padding: '10px 16px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
    }}>
      <p style={{ color: '#f0f0f5', fontWeight: 600, marginBottom: 4, fontSize: '0.85rem' }}>
        {label || payload[0]?.payload?.name || payload[0]?.payload?.stage}
      </p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || '#9b6dff', fontSize: '0.85rem' }}>
          {p.dataKey === 'value' ? `${p.value}%` : p.value}
        </p>
      ))}
    </div>
  );
};

/* Page wrapper that scrolls to top on mount */
export function PageWrapper({ children }) {
  React.useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return <>{children}</>;
}
