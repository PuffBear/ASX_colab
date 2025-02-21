import React, { useState, useEffect } from "react";

const PlaceTrades = ({ selectedTrade }) => {
  const [tradeType, setTradeType] = useState(null); // "buy" or "sell"
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState("");

  const accountBalance = 10000; // Example: User's balance in dollars
  const sharesOwned = 50; // Example: Number of shares user owns

  const handleTradeType = (type) => {
    if (tradeType === type) return; // Prevent redundant clicks
    setTradeType(type);
  };

  useEffect(() => {
    if (selectedTrade) {
      setTradeType(selectedTrade.type);
      setPrice(selectedTrade.price);
      setQuantity(selectedTrade.quantity)
    }
  }, [selectedTrade]);

  const handleConfirmTrade = () => {
    if (!tradeType || !quantity || !price) {
      alert("Please fill all fields before confirming.");
      return;
    }
    console.log(`Trade Confirmed: ${tradeType.toUpperCase()} ${quantity} shares at $${price}`);
    // TODO: Implement actual trade execution logic (API call or state update)
  };

  const handleCancel = () => {
    setTradeType(null);
    setQuantity("");
    setPrice("");
  };

  return (
    <div className="p-4 bg-gray-900 rounded-lg text-white w-full">
      <h2 className="text-xl font-bold mb-3">Place Trade</h2>

      {/* Buy/Sell Toggle Buttons */}
      <div className="flex gap-2 mb-3">
        <button
          className={`w-1/2 py-2 font-bold rounded-lg ${tradeType === "buy" ? "bg-green-500" : "bg-gray-700"
            }`}
          onClick={() => handleTradeType("buy")}
        >
          Buy
        </button>
        <button
          className={`w-1/2 py-2 font-bold rounded-lg ${tradeType === "sell" ? "bg-red-500" : "bg-gray-700"
            }`}
          onClick={() => handleTradeType("sell")}
        >
          Sell
        </button>
      </div>

      {/* Display Account Balance or Shares Owned */}
      <p className="mb-2 text-sm">
        {tradeType === "buy" ? `Account Balance: $${accountBalance.toFixed(2)}` :
          tradeType === "sell" ? `Shares Owned: ${sharesOwned}` :
            "Select Buy or Sell"}
      </p>

      {/* Quantity Input */}
      <input
        type="number"
        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
        placeholder="Enter quantity"
        className="w-full mb-2 p-2 rounded-lg bg-gray-700 text-white placeholder-gray-400"
      />

      {/* Price Input */}
      <input
        type="number"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
        placeholder="Enter price"
        className="w-full mb-4 p-2 rounded-lg bg-gray-700 text-white placeholder-gray-400"
      />

      {/* Confirm & Cancel Buttons */}
      <div className="flex gap-2">
        <button
          className="w-1/2 py-2 bg-blue-500 font-bold rounded-lg hover:bg-blue-600"
          onClick={handleConfirmTrade}
          
        >
          Confirm
        </button>
        <button
          className="w-1/2 py-2 bg-gray-600 font-bold rounded-lg hover:bg-gray-700"
          onClick={handleCancel}
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

export default PlaceTrades;
