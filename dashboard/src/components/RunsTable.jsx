function outcome(run) {
  if (run.call?.parse_error) return { cls: "bad", text: `parse error: ${run.call.parse_error}` };
  if (!run.call?.tool) return { cls: "muted", text: "no tool chosen" };
  if (!run.result) return { cls: "muted", text: "not executed" };
  if (!run.result.ok) return { cls: "bad", text: run.result.error };
  return { cls: "ok", text: JSON.stringify(run.result.output) };
}

const short = (s, n = 80) => (s.length > n ? `${s.slice(0, n)}…` : s);

export default function RunsTable({ runs }) {
  if (runs.length === 0) return <p className="muted">No runs yet. Ask the agent something above.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Time</th><th>Query</th><th>Tool</th><th>Arguments</th>
            <th>Result</th><th className="num">ms</th><th>Saved</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => {
            const o = outcome(run);
            return (
              <tr key={run.request_id}>
                <td>{new Date(run.created_at).toLocaleTimeString()}</td>
                <td>{run.query}</td>
                <td><code>{run.call?.tool ?? "—"}</code></td>
                <td><code>{short(JSON.stringify(run.call?.arguments ?? {}), 50)}</code></td>
                <td className={o.cls}>{short(o.text)}</td>
                <td className="num">{run.latency_ms}</td>
                <td>{run.logged === false ? "no" : "yes"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
