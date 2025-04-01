"use client";

import { useEffect, useState } from "react";
import { fetchChartData } from "@/app/actions/fetchPriceData";
import dynamic from "next/dynamic";
import { Loader } from "./loader";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function PriceChart() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [chartData, setChartData] = useState(0 as any);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchChartData()
        .then((data) => {
          setChartData(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Error fetching chart data:", err);
          setLoading(false);
        });
    }, 5000);
    return () => clearTimeout(timer);
  }, []);
  return (
    <>
      {loading ? (
        <Loader />
      ) : chartData && chartData.data ? (
        <Plot data={chartData.data} layout={chartData.layout} />
      ) : (
        <div className="text-center p-4 text-gray-600">
          Please refresh for updated forecasts
        </div>
      )}
    </>
  );
}
