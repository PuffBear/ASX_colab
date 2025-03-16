"use client";
import React, { useState, useEffect, useRef } from "react";
import { ColorType, createChart, LineSeries } from "lightweight-charts";
import StockDropdown from "@/components/StockDropdown";
import OrderBook from "@/components/OrderBook";
import PlaceTrades from "@/components/PlaceTrades";
import { snippet } from "@heroui/theme";

const Page = () => {
  const chartContainerRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const [chartWidth, setChartWidth] = useState(75); // Default: Chart takes 75% of the screen
  const [selectedStock, setSelectedStock] = useState("AAPL");
  const [chartData, setChartData] = useState([]);
  
  const [LTP, setLTP] = useState(null);
  const [bufferedLTP, setBufferedLTP] = useState(null);
  const [lastKnownLTP, setLastKnownLTP] = useState(null);


  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart instance (chart rendering start)
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "black" },
        textColor: "white",
      },
      grid: {
        vertLines: { color: "rgba(255, 255, 255, 0.1)", visible: true },
        horzLines: { color: "rgba(255, 255, 255, 0.1)", visible: true },
      },
      autoSize: true,
      priceScale: { borderVisible: false, textColor: "white" },
      timeScale: {
        borderVisible: false, 
        textColor: "white",
        timeVisible: true,
        secondsVisible: false,
        tickMarkFormatter: (timestamp) => {
          const date = new Date(timestamp * 1000);
          return `${date.getHours()}:${date.getMinutes().toString().padStart(2, "0")}`;
        }
      },
    });

    chartInstanceRef.current = chart;
    const newSeries = chart.addSeries(LineSeries, { color: "#2962ff" });
    newSeries.setData(chartData);

    // Resize observer
    const resizeObserver = new ResizeObserver(() => {
      if (chartContainerRef.current) {
        const { clientWidth, clientHeight } = chartContainerRef.current;
        chart.resize(clientWidth, clientHeight);
      }
    });
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [chartData]);

  //Update Buffered LTP when LTP changes
  useEffect(() => {
    if (LTP !== null) {
      console.log("Buffered LTP updated:", LTP);
      setBufferedLTP(LTP);
      setLastKnownLTP(LTP);
    }
  }, [LTP]);
  
  // Update chart data with a buffer of 2 seconds, data is checked every milisecond
  useEffect(() => {
    let lastUpdateTime = Date.now(); // Track the last update timestamp
    const interval = setInterval(() => {
      const now = new Date();
      if (now - lastUpdateTime >= 2000) { // Check if it's the start of a new minute
        if (bufferedLTP !== null || lastKnownLTP !== null) {
          const timestamp = Math.floor(now.getTime() / 1000); // Convert to Unix timestamp
          const newDataPoint = { time: timestamp, value: bufferedLTP !== null ? bufferedLTP : lastKnownLTP };
          setChartData((prevData) => [...prevData, newDataPoint]);
          setBufferedLTP(null); // Clear the buffered LTP after updating
          lastUpdateTime = now; // Reset the last update time
        }
      }
    }, 100); // Check every milisecond

    return () => clearInterval(interval);
  }, [bufferedLTP]);
  //chart rendering end

  // Prevent Chrome Back/Forward Gesture When Dragging Chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const preventNavigation = (event) => {
      if (event.deltaX !== 0 || event.touches) {
        event.preventDefault();
      }
    };

    chartContainerRef.current.addEventListener("wheel", preventNavigation, { passive: false });
    chartContainerRef.current.addEventListener("touchstart", preventNavigation, { passive: false });

    return () => {
      chartContainerRef.current.removeEventListener("wheel", preventNavigation);
      chartContainerRef.current.removeEventListener("touchstart", preventNavigation);
    };
  }, []);

  // Handle Dragging to Resize (Vertical Divider)
  const handleMouseDown = (e) => {
    e.preventDefault();
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  const handleMouseMove = (e) => {
    const newWidth = (e.clientX / window.innerWidth) * 100;
    if (newWidth > 20 && newWidth < 80) {
      setChartWidth(newWidth);
    }
  };

  const handleMouseUp = () => {
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);
  };

  const [selectedTrade, setSelectedTrade] = useState(null);

  return (
    <div className="flex flex-col h-screen">
      {/* Top Section */}
      <div className="flex flex-row pt-8 pl-10 bg-gray-800 items-center">
        <h1 className="text-white ml-5 pb-4 font-bold text-xl">Choose Security</h1>
        <div className="basis-3/5">
          <StockDropdown selectedStock={selectedStock} setSelectedStock={setSelectedStock} />
        </div>
        <div className="text-white font-bold ml-20 text-xl pb-4">Account Balance</div>
        <h1 className="text-red-500 ml-5 font-bold text-2xl pb-4">$200,000</h1>
      </div>

      {/* Trading Section */}
      <div className="flex flex-row flex-grow z-[0]">
        {/* Chart Section */}
        <div className="bg-black p-2" style={{ width: `${chartWidth}%` }}>
          {chartData.length === 0 ? (
            <div className="text-white text-center mt-10">Loading Chart...</div>
          ) : (
            <div ref={chartContainerRef} className="w-full h-full"></div>
          )}
        </div>

        {/* Draggable Divider */}
        <div
          className="w-1 bg-gray-800 cursor-ew-resize"
          onMouseDown={handleMouseDown}
        ></div>

        {/* Orders Section */}
        <div className="flex flex-col bg-black" style={{ width: `${100 - chartWidth}%` }}>
          {/* DOM/ORDERBOOK Section (Fixed 50%) */}
          <div className="flex justify-center items-center h-1/2 bg-gray-800">
            <OrderBook setSelectedTrade={setSelectedTrade} selectedStock={selectedStock} setLTP={setLTP} LTP={LTP} />
          </div>

          {/* Static Horizontal Divider */}
          <div className="h-1 bg-gray-800" />

          {/* Trade Placing Section (Fixed 50%) */}
          <div className="h-1/2 bg-gray-800 p-4">
            <PlaceTrades selectedTrade={selectedTrade} selectedStock={selectedStock} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Page;
