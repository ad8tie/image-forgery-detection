import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { getHealth } from "./lib/api";
import CheckImage from "./pages/CheckImage";
import HowItWorks from "./pages/HowItWorks";
import Results from "./pages/Results";

export default function App() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    getHealth().then((health) => setOnline(health.connected)).catch(() => setOnline(false));
  }, []);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A] dark:bg-slate-950 dark:text-slate-100">
      <Navbar online={online} />
      <main className="pt-16">
        <Routes>
          <Route path="/" element={<CheckImage />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </main>
    </div>
  );
}
