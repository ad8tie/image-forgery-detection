import { Link } from "react-router-dom";

export function CtaBanner() {
  return (
    <Link to="/how-it-works" className="mt-10 block rounded-[20px] bg-gradient-to-r from-[#312e81] to-[#4F46E5] px-6 py-8 text-white">
      <p className="text-2xl font-semibold">Curious how it works?</p>
      <p className="mt-1 text-indigo-100">A short look at the three steps, without the lab jargon.</p>
    </Link>
  );
}
