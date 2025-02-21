'use client';
import { Button } from '@nextui-org/react';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { signIn, signOut, useSession } from "next-auth/react";

const Navigation = () => {

  const [selectedTab, setselectedTab] = useState()
  const { data: session, status } = useSession();
  const router = useRouter()

  useEffect(() => {
    if (status === "authenticated") {
      console.log("User is logged in:", session.user);
    }
  }, [status, session]);

  const handleClick = (tab) => {
    setselectedTab(tab)
    if(tab==='Home')
      router.push('/')
    else
      router.push(`/${tab}`)
  }

  const handleSignOut = async () => {
    await signOut({ redirect: false }); // Prevents NextAuth from redirecting
    router.push('/'); // Redirects to Home manually
  };

  return (
    <nav className='flex justify-center top-0 left-0 right-0'>
      <div className='flex fixed text-white px-3 py-1.5 border-1 border-black  mt-5
        rounded-full shadow-black shadow-md transform transition-all duration-100 delay-100 
        ease-in-out hover:px-5 hover:cursor-pointer bg-[#000315] bg-opacity-100 z-[1]'>
        <button onClick={() => handleClick('Home')} className='hover:opacity-75 transition-opacity duration-250'>
          <Image
            alt='Ashoka Logo'
            src='/4pointlogo.png'
            width={40}
            height={40}
          />
        </button>
        <button onClick={() => handleClick('portfolio')} className={`ml-5 hover:opacity-75 transition-opacity duration-250 ${selectedTab === 'portfolio' ? 'text-[#8a0100]' : 'text-white'}`}>
          <h1 className="py-2 px-2 font-bold">Portfolio</h1>
        </button>
        <button onClick={() => handleClick('trading')} className={`hover:opacity-75 transition-opacity duration-250 ${selectedTab === 'trading' ? 'text-[#8a0100]' : 'text-white'}`}>
          <h1 className="py-2 px-2 font-bold">Trading</h1>
        </button>
        <button onClick={() => handleClick('account')} className={`hover:opacity-75 transition-opacity duration-250 ${selectedTab === 'account' ? 'text-[#8a0100]' : 'text-white'} `}>
          <h1 className="py-2 px-2 font-bold">Account</h1>
        </button>
        <button onClick={() => handleClick('listings')} className={`mr-5 hover:opacity-75 transition-opacity duration-250 ${selectedTab === 'listings' ? 'text-[#8a0100]' : 'text-white'} `}>
          <h1 className="py-2 px-2 font-bold">Listings</h1>
        </button>
        {status === "authenticated" ? (
          <Button 
            color='secondary' 
            onClick={handleSignOut} 
            className='font-bold rounded-full bg-clip-border border-3' 
            style={{ border: "#000516" }}>
            Sign Out
          </Button>
        ) : (
          <Button 
            color='secondary' 
            onClick={() => signIn("google")} 
            className='font-bold rounded-full bg-clip-border border-3' 
            style={{ border: "#000516" }}>
            Sign In
          </Button>
        )}
      </div>
    </nav>
  )
};

export default Navigation;