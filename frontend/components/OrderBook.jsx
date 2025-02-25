import React from "react";
import { useEffect, useState } from "react";

const OrderBook = ({ setSelectedTrade, selectedStock, setLTP, LTP }) => {

  const [bids, setBids] = useState([]);
  const [asks, setAsks] = useState([]);

  const fetchOrderBook = async () => {
    if(!selectedStock) return;

    try {
      const response = await fetch(`http://127.0.0.1:5000/get_orderbook/${selectedStock}`);
      const data = await response.json();

      if (response.ok) {
        setBids(data.bids || []);
        setAsks(data.asks || []);
        setLTP(data.ltp);
      }
      else {
        console.error("Error fetching order book:", data.error)
      }
    }
    catch (error) {
      console.error("Failed to fetch order book:", error)
    }
  }

  useEffect(() => {
    fetchOrderBook();

    const interval = setInterval(fetchOrderBook, 2000);

    return () => clearInterval(interval);
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
            <span>{ask.price}</span>
            <span>{ask.quantity}</span>
            <span>{(ask.price * ask.quantity)}</span>
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
            <span>{bid.price}</span>
            <span>{bid.quantity}</span>
            <span>{(bid.price * bid.quantity)}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default OrderBook;
