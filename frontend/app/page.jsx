"use client";
import React, { useEffect } from 'react';
import { signIn, signOut, useSession } from "next-auth/react";
import { useRouter } from 'next/navigation';
import { Button } from "@heroui/button";

const Page = () => {
  const {data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") {
      router.push("/trading");
    }
  }, [status, router]);

  return (
      <>
        <div alt='hero-section' className='flex flex-col bg-gradient-to-br from-blue-900 to-gray-900 h-screen w-screen justify-center items-center'
          style={{
            background: "linear-gradient(to bottom right, #1e3a8a, #111827), url('/stockmarket.jpg')",
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
            backgroundBlendMode: "overlay",
          }}
          >
          <div className='flex flex-col color-white text-white text-center'>
            <h1 className='text-4xl font-bold text-white-500 mb-5'>Welcome to the</h1>
            <h1 className="text-6xl font-bold text-white">
              <span className="text-red-800">A</span>shoka
              <span className="text-red-800"> S</span>tock
              <span className="text-red-800"> X</span>change
            </h1>
            <p className='mt-3'>Trade Startup@Ashoka's company stocks to</p>
            <p>determine who deserves the most funding.</p>
          </div>

          <div className='flex justify-center items-center mt-5'>
            <Button onClick={() => signIn("google")} color='secondary' size='lg' className='font-bold rounded-medium bg-clip-border border-black'>Register</Button>
          </div>
        </div>

        <div alt='section-2' className="flex flex-row h-screen w-full justify-center items-center bg-gray-900 text-white text-center">
          <div alt='left-sec' className='flex flex-col basis-1/2 justify-center items-center'>
            <h1 className='text-4xl font-bold text-white-500 mb-5'>How it works?</h1>
            <p className='mx-12'>Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</p>
          </div>
          <div alt='right-sec' className='flex flex-col basis-1/2 justify-center items-center'>
            <h1 className='text-4xl font-bold text-white-500 mb-5'>Today's Market</h1>
            <div alt='prices'></div>
          </div>
        </div>
      </>  
  )
}

export default Page;

