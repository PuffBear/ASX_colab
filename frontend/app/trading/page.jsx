import React from 'react';
import StockDropdown from "@/components/StockDropdown";

const page = () => {
  return (
    <div className='flex flex-col'>
      <div alt='top-section' className='flex flex-row pt-9 px-10 bg-gray-800'>
        <h1 className='text-white ml-5 font-bold text-xl pb-5 my-auto'>Choose Security</h1>
        <div className='basis-3/5'><StockDropdown /></div>

        <div className='text-white font-bold text-2xl pb-5 my-auto'>Account Balance</div>
        <h1 className='text-red-500 ml-5 font-bold text-2xl pb-5 my-auto'>$200,000</h1>

      </div>

      <div alt='trading section' className='flex flex-row'>
        <div alt='charts' className='flex basis-3/4 bg-blue-500'>Charting width</div>

        <div alt='Orders section' className='flex flex-col bg-red-500 basis-1/4'>
          <div alt='DOM/Orderbook'>DOM and Placing orders' width</div>
          <div alt='Place orders'></div>
        </div>
      </div>

      
    </div>
  )
}

export default page
