import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import Home from './pages/Home';
import Pipeline from './pages/Pipeline';
import Experiments from './pages/Experiments';
import Models from './pages/Models';
import Results from './pages/Results';
import SURS from './pages/SURS';
import Docs from './pages/Docs';
import Citation from './pages/Citation';

function App() {
  return (
    <div className="min-h-screen text-slate-50 selection:bg-cyan-500/30 font-sans flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/experiments" element={<Experiments />} />
          <Route path="/models" element={<Models />} />
          <Route path="/results" element={<Results />} />
          <Route path="/surs" element={<SURS />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/citation" element={<Citation />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
