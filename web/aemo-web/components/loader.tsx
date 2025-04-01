"use client";

export const Loader = () => {
  return (
    <div className="flex items-center justify-center h-84">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="25"
        height="25"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="lucide lucide-trees"
      >
        <path
          d="M10 10v.2A3 3 0 0 1 8.9 16H5a3 3 0 0 1-1-5.8V10a3 3 0 0 1 6 0Z"
          className="svg-elem-1"
        ></path>
        <path d="M7 16v6" className="svg-elem-2"></path>
        <path d="M13 19v3" className="svg-elem-3"></path>
        <path
          d="M12 19h8.3a1 1 0 0 0 .7-1.7L18 14h.3a1 1 0 0 0 .7-1.7L16 9h.2a1 1 0 0 0 .8-1.7L13 3l-1.4 1.5"
          className="svg-elem-4"
        ></path>
      </svg>
      <style>{`
        @keyframes animate-svg-stroke-1 {
          0% { stroke-dashoffset: 32.32px; stroke-dasharray: 32.32px; }
          100% { stroke-dashoffset: 0; stroke-dasharray: 32.32px; }
        }
        .svg-elem-1 { animation: animate-svg-stroke-1 1s linear 0s both; }

        @keyframes animate-svg-stroke-2 {
          0% { stroke-dashoffset: 8px; stroke-dasharray: 8px; }
          100% { stroke-dashoffset: 0; stroke-dasharray: 8px; }
        }
        .svg-elem-2 { animation: animate-svg-stroke-2 1s linear 0.24s both; }

        @keyframes animate-svg-stroke-3 {
          0% { stroke-dashoffset: 5px; stroke-dasharray: 5px; }
          100% { stroke-dashoffset: 0; stroke-dasharray: 5px; }
        }
        .svg-elem-3 { animation: animate-svg-stroke-3 1s linear 0.48s both; }

        @keyframes animate-svg-stroke-4 {
          0% { stroke-dashoffset: 34.75px; stroke-dasharray: 34.75px; }
          100% { stroke-dashoffset: 0; stroke-dasharray: 34.75px; }
        }
        .svg-elem-4 { animation: animate-svg-stroke-4 1s linear 0.36s both; }
      `}</style>
      <p className="ml-2">Loading Forecasts</p>
    </div>
  );
};
