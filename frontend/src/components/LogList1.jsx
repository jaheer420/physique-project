// frontend/src/components/LogList1.jsx
import React from "react";

export default function LogList1({ logs }) {
  return (
    <div style={{ marginTop: 20 }}>
      <h3>Recent Logs</h3>
      {logs.length === 0 ? (
        <p>No logs yet</p>
      ) : (
        logs.map((log) => (
          <div
            key={log.id}
            style={{
              padding: 12,
              border: "1px solid #eee",
              borderRadius: 6,
              marginBottom: 10,
            }}
          >
            <p><b>Text:</b> {log.raw_text}</p>
            <pre>{JSON.stringify(JSON.parse(log.totals_json), null, 2)}</pre>
          </div>
        ))
      )}
    </div>
  );
}
