import { useCallback, useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchRuns, subscribeToRuns } from "../api/client.js";
import QueryForm from "../components/QueryForm.jsx";
import RunsTable from "../components/RunsTable.jsx";

const KEY = ["runs"];
const MAX_ROWS = 200;

export default function LiveFeed() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("connecting");
  const { data, isLoading, error } = useQuery({ queryKey: KEY, queryFn: () => fetchRuns() });

  // A run can arrive twice (live event and the form's own response), so merge by request_id.
  const addRun = useCallback((run) => {
    queryClient.setQueryData(KEY, (old) => {
      const items = old?.items ?? [];
      if (items.some((r) => r.request_id === run.request_id)) return old;
      return { items: [run, ...items].slice(0, MAX_ROWS), total: (old?.total ?? 0) + 1 };
    });
  }, [queryClient]);

  useEffect(() => subscribeToRuns(addRun, setStatus), [addRun]);

  return (
    <>
      <QueryForm onResult={addRun} />
      <section>
        <div className="section-head">
          <h2>Recent calls {data ? <small>({data.total} total)</small> : null}</h2>
          <span className={`pill ${status}`} role="status" aria-live="polite">{status}</span>
        </div>
        {isLoading && <p className="muted">Loading…</p>}
        {error && <p className="error" role="alert">Could not load runs: {error.message}</p>}
        {data && <RunsTable runs={data.items} />}
      </section>
    </>
  );
}
