"use client";

import { useEffect, useState } from "react";

export default function MobileModal() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const isMobile = window.matchMedia("(max-width: 768px)").matches;
    const visited = localStorage.getItem("visitedMobile");
    if (isMobile && !visited) {
      setShow(true);
      localStorage.setItem("visitedMobile", "true");
    }
  }, []);

  if (!show) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60">
      <div className="max-w-[80%] rounded-lg bg-black p-4 shadow">
        <p className="text-lg text-white">
          TranspareNC isn&apos;t optimized for mobile. Try visiting on your
          computer!
        </p>
        <button
          onClick={() => setShow(false)}
          className="mt-2 rounded bg-[#C00] px-4 py-2 text-white"
        >
          I understand
        </button>
      </div>
    </div>
  );
}
