"use client";
import { useState } from "react";
import { getPriceSpike } from "@/app/actions/getPriceSpike";

export default function Simulate() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  return (
    <div>
      <button
        className="bg-green-600 hover:bg-green-700 text-white text-xs font-medium py-2 px-4 rounded-full ml-4"
        onClick={async () => {
          try {
            setLoading(true);
            const result = await getPriceSpike();
            setMessage(result);
          } catch (error) {
            setMessage("Failed to simulate price spike");
            console.error(error);
          } finally {
            setLoading(false);
          }
        }}
      >
        {loading ? "Simulating..." : "Simulate Price Spike"}
      </button>

      {message && (
        <div className="mt-4 px-2 bg-amber-200 rounded-lg text-sm">
          {message}
        </div>
      )}
    </div>
  );
}
