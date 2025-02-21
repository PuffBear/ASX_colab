import React from "react";

const OrderBook = ({ setSelectedTrade }) => {

  const asks = [
    { price: 101.5, quantity: 2, total: 203 },
    { price: 101.4, quantity: 3, total: 304.2 },
    { price: 101.3, quantity: 1.5, total: 151.95 },
  ];

  const bids = [
    { price: 101.2, quantity: 2.5, total: 253 },
    { price: 101.1, quantity: 1, total: 101.1 },
    { price: 101.0, quantity: 4, total: 404 },
  ];

  const midPrice = (asks[0].price + bids[0].price) / 2;

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
            onClick={() => setSelectedTrade({ type: "buy", price: ask.price, quantity: ask.quantity })}
          >
            <span>{ask.price.toFixed(2)}</span>
            <span>{ask.quantity}</span>
            <span>{ask.total.toFixed(2)}</span>
          </button>
        ))}
      </div>

      {/* Mid Price */}
      <div className="text-center bg-gray-900 py-2 font-bold rounded-lg">{midPrice.toFixed(2)}</div>

      {/* Bid Orders */}
      <div className="flex flex-col bg-gray-800 p-2 rounded-lg">
        {bids.map((bid, index) => (
          <button
            key={index}
            className="flex justify-between px-4 py-1 hover:bg-green-500 rounded-lg"
            onClick={() => setSelectedTrade({ type: "sell", price: bid.price, quantity: bid.quantity })}
          >
            <span>{bid.price.toFixed(2)}</span>
            <span>{bid.quantity}</span>
            <span>{bid.total.toFixed(2)}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default OrderBook;
