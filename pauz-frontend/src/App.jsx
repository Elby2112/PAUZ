/*
import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer"
import Hero from "./components/Hero"
import JournalingChoice from "./components/JournalingChoice"
import JournalingInfo from "./components/JournalingInfo";
;function App() {
  return (
    <div>
      <Navbar />
      <Hero />
      <JournalingChoice />
      <JournalingInfo />
       <Footer />
    </div>
  );
}



export default App;
*/

import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import Home from "./pages/Home";
import Garden from "./pages/Garden";
/*import Journal from "./pages/Journal";`*/
import FreeJournal from "./Journals/freeJournal";
import GuidedJournaling from "./Journals/guidedJournal"; // ⭐ Import the new guided journaling component
function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/garden" element={<Garden />} />
        <Route path="/journal" element={<FreeJournal />} />

        {/* ⭐ New route for guided journaling */}
       <Route path="/guided/:category" element={<GuidedJournaling />} />

      </Routes>
      <Footer />
    </Router>
  );
}
export default App;

 /* <Route path="/journal" element={<Journal />} />*/



/*
function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <h1 className="text-3xl font-bold">PAUZ Minimal Test</h1>
    </div>
  );
}

export default App;
*/