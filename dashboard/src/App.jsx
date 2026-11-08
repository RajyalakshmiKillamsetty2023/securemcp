import { NavLink, Route, Routes } from "react-router-dom";
import LiveFeed from "./pages/LiveFeed.jsx";

export default function App() {
  return (
    <>
      <header className="topbar">
        <h1>SecureMCP</h1>
        <nav>
          <NavLink to="/" end>Live feed</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<LiveFeed />} />
          <Route path="*" element={<p>Page not found.</p>} />
        </Routes>
      </main>
    </>
  );
}
