import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { runAgent } from "../api/client.js";

const EXAMPLES = [
  "What is the weather in Hyderabad today?",
  "What is 15 * 4?",
  "Convert 100 USD to INR",
  "Find flights from Delhi to Mumbai on 2026-12-01",
];

export default function QueryForm({ onResult }) {
  const [query, setQuery] = useState("");
  const [order, setOrder] = useState("given");
  const [nTools, setNTools] = useState("");
  const [seed, setSeed] = useState("0");

  const mutation = useMutation({ mutationFn: runAgent, onSuccess: onResult });

  function submit(e) {
    e.preventDefault();
    if (!query.trim()) return;
    const payload = { query: query.trim(), order, seed: Number(seed) || 0 };
    if (nTools) payload.n_tools = Number(nTools);
    mutation.mutate(payload);
  }

  return (
    <form className="card" onSubmit={submit}>
      <label htmlFor="query">Ask the agent</label>
      <div className="row">
        <input
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          maxLength={2000}
          placeholder="e.g. What is 15 * 4?"
          autoComplete="off"
        />
        <button type="submit" disabled={mutation.isPending || !query.trim()}>
          {mutation.isPending ? "Running…" : "Run"}
        </button>
      </div>

      <div className="chips" aria-label="Example queries">
        {EXAMPLES.map((q) => (
          <button type="button" className="chip" key={q} onClick={() => setQuery(q)}>{q}</button>
        ))}
      </div>

      <details>
        <summary>Tool set options</summary>
        <div className="row options">
          <label>Order
            <select value={order} onChange={(e) => setOrder(e.target.value)}>
              <option value="given">given</option>
              <option value="reverse">reverse</option>
              <option value="shuffle">shuffle</option>
            </select>
          </label>
          <label>Seed
            <input type="number" value={seed} onChange={(e) => setSeed(e.target.value)} />
          </label>
          <label>Tools offered
            <input type="number" min="1" max="10" placeholder="all" value={nTools}
                   onChange={(e) => setNTools(e.target.value)} />
          </label>
        </div>
      </details>

      {mutation.isError && <p className="error" role="alert">{mutation.error.message}</p>}
    </form>
  );
}
