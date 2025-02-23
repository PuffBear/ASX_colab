import React from "react";
import { useEffect, useState } from "react";

const OrderBook = ({ setSelectedTrade, selectedStock }) => {

  const [bids, setBids] = useState([]);
  const [asks, setAsks] = useState([]);
  const [LTP, setLTP] = useState(null); // Fix: Initialize LTP state

  useEffect(() => {
    if (!selectedStock) return;

    fetch("/stocks_historical_data.json")
      .then((response) => response.json())
      .then((data) => {
        if (!data || !data[selectedStock] || !Array.isArray(data[selectedStock])) {
          console.warn("No valid historical data found for:", selectedStock);
          setLTP(null);
          return;
        }
        const stockData = data[selectedStock];
        setLTP(stockData.length > 0 ? stockData[stockData.length - 1].value : null);
      })
      .catch((error) => console.error("Error loading JSON:", error));
  }, [selectedStock]);


  return (
    <div className="flex flex-col w-full text-white bg-gray-800">
      <div className="text-center bg-gray-800 py-2 font-bold text-lg rounded-t-lg">Order Book</div>

      {/* Headers */}
      <div className="flex justify-between px-4 py-2 rounded-lg bg-gray-900 font-bold text-sm">
        <span>Price</span>
        <span>Quantity</span>
        <span>Total</span>
      </div>

      {/* Ask Orders */}
      <div className="flex flex-col-reverse bg-gray-800 p-2">
        {asks.map((ask, index) => (
          <button
            key={index}
            className="flex justify-between px-4 py-1 hover:bg-red-700 rounded-lg"
            onClick={() => setSelectedTrade({ type: "BUY", price: ask.price, quantity: ask.quantity })}
          >
            <span>{ask.price.toFixed(2)}</span>
            <span>{ask.quantity}</span>
            <span>{ask.total?.toFixed(2) || "N/A"}</span>
          </button>
        ))}
      </div>

      {/* Current Price */}
      <div className="text-center bg-gray-900 py-2 font-bold rounded-lg">{LTP !== null ? LTP.toFixed(2) : "N/A"}</div>

      {/* Bid Orders */}
      <div className="flex flex-col bg-gray-800 p-2 rounded-lg">
        {bids.map((bid, index) => (
          <button
            key={index}
            className="flex justify-between px-4 py-1 hover:bg-green-500 rounded-lg"
            onClick={() => setSelectedTrade({ type: "SELL", price: bid.price, quantity: bid.quantity })}
          >
            <span>{bid.price.toFixed(2)}</span>
            <span>{bid.quantity}</span>
            <span>{bid.total?.toFixed(2) || "N/A"}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default OrderBook;
