"use client";
import React, { useState, useEffect, useRef } from "react";
import { ColorType, createChart, LineSeries } from "lightweight-charts";
import StockDropdown from "@/components/StockDropdown";
import OrderBook from "@/components/OrderBook";
import PlaceTrades from "@/components/PlaceTrades";

const Page = () => {
  const chartContainerRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const [stockData, setStockData] = useState([]);
  const [chartWidth, setChartWidth] = useState(75); // Default: Chart takes 75% of the screen
  const [selectedStock, setSelectedStock] = useState("Apple");

  // Load data.json immediately
  useEffect(() => {
    // Load stock historical data
    fetch("/stocks_historical_data.json")
      .then((response) => response.json())
      .then((data) => {
        if (data[selectedStock]) {
          setStockData(data[selectedStock]); // Filter data based on selected stock
        }
      })
      .catch((error) => console.error("Error loading stock data:", error));
  }, [selectedStock]); // Runs when selectedStock changes

  useEffect(() => {
    if (!chartContainerRef.current || stockData.length === 0) return;

    // Create chart instance
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
      timeScale: { borderVisible: false, textColor: "white" },
    });

    chartInstanceRef.current = chart;
    const newSeries = chart.addSeries(LineSeries, { color: "#2962ff" });
    newSeries.setData(stockData);

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
  }, [stockData]);

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
          {stockData.length === 0 ? (
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
            <OrderBook setSelectedTrade={setSelectedTrade} />
          </div>

          {/* Static Horizontal Divider */}
          <div className="h-1 bg-gray-800" />

          {/* Trade Placing Section (Fixed 50%) */}
          <div className="h-1/2 bg-gray-800 p-4">
            <PlaceTrades selectedTrade={selectedTrade} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Page;
