
import React from "react";
import Hero from "../components/Hero";
import JournalingChoice from "../components/JournalingChoice";
import JournalingInfo from "../components/JournalingInfo";

const Home = () => {
  return (
    <div className="bg-[#F4F6F7] min-h-screen">
      <Hero />
      <JournalingChoice />
      <JournalingInfo />
    </div>
  );
};

export default Home;



/*
import React from "react";
// import Hero from "../components/Hero";
// import JournalingChoice from "../components/JournalingChoice";
// import JournalingInfo from "../components/JournalingInfo";

const Home = () => {
  return (
    <div className="bg-[#F4F6F7] min-h-screen flex items-center justify-center">
      <h1 className="text-3xl font-bold">Hello PAUZ</h1>
    </div>
  );
};

export default Home;
*/