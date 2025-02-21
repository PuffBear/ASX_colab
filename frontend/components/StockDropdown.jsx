"use client"; // Ensure this is a client component

import { useState, useEffect, useRef } from "react";

export default function StockDropdown() {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState("Apple");
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Fetch stocks from public/stocks.json
    fetch("/stocks.json")
      .then((res) => res.json())
      .then((data) => setStocks(data))
      .catch((err) => console.error("Error fetching stocks:", err));

    // Event listener for closing on 'Esc' key
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    // Event listener for closing when clicking outside
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("click", handleClickOutside);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  return (
    <div className="relative w-64 mb-5 ml-5" ref={dropdownRef}>
      {/* Selected Stock Button */}
      <button
        className="px-4 py-2 bg-[#8a0100] text-white font-bold rounded-lg shadow-md focus:outline-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        {selectedStock} ▼
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute mt-2 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-40 overflow-y-auto z-[1]">
          {stocks
            .filter((stock) => stock.name !== selectedStock) // Exclude selected stock
            .map((stock) => (
              <div
                key={stock.name}
                className="px-3 py-1.5 hover:bg-gray-100 cursor-pointer text-black"
                onClick={() => {
                  setSelectedStock(stock.name);
                  setIsOpen(false);
                }}
              >
                {stock.name}
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
