import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server forwards /api to the Node API, so the browser never needs CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:3001" },
  },
});
