import React, { useState, useEffect } from "react";

const PlaceTrades = ({ selectedTrade, selectedStock }) => {
  const [tradeType, setTradeType] = useState(null); // "buy" or "sell"
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState("");
  const [message, setMessage] = useState("");

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

  const handleConfirmTrade = async () => {
    if (!tradeType || !quantity || !price) {
      setMessage({ type: "error", text: "Please fill in all fields." });
      return;
    }

    const tradeData = {
      stock: selectedStock,
      quantity: parseInt(quantity, 10),
      order_side: tradeType,
      price: parseFloat(price),
    };

    console.log("Trade Data:", tradeData); // Debugging output

    try {
        const response = await fetch("http://127.0.0.1:5000/place_trade", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(tradeData),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ type: "success", text: `Trade placed: ${JSON.stringify(data)}` });
      } else {
        setMessage({ type: "error", text: `Error: ${data.error}` });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Failed to connect to the server." });
    }
  };

  const handleCancel = () => {
    setTradeType(null);
    setQuantity("");
    setPrice("");
  };

  return (
    <div className="p-4 bg-gray-900 rounded-lg text-white w-full">
      <div className="flex flex-row">
        <h2 className="text-xl font-bold mb-3 basis-11/12">Place Trade</h2>
        <h2 className="text-xl font-bold mb-3">{selectedStock}</h2>
      </div>
      
      {/* Buy/Sell Toggle Buttons */}
      <div className="flex flex-row gap-2 mb-3">
        <button
          className={`w-1/2 py-2 font-bold rounded-lg ${tradeType === "BUY" ? "bg-green-500" : "bg-gray-700"
            }`}
          onClick={() => handleTradeType("BUY")}
        >
          Buy
        </button>
        <button
          className={`w-1/2 py-2 font-bold rounded-lg ${tradeType === "SELL" ? "bg-red-500" : "bg-gray-700"
            }`}
          onClick={() => handleTradeType("SELL")}
        >
          Sell
        </button>
      </div>

      {/* Display Account Balance or Shares Owned */}
      <p className="mb-2 text-sm">
        {tradeType === "BUY" ? `Account Balance: $${accountBalance.toFixed(2)}` :
          tradeType === "SELL" ? `Shares Owned: ${sharesOwned}` :
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
