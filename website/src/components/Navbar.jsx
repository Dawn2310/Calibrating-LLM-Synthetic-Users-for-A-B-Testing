import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const links = [
    { name: 'Home', path: '/' },
    { name: 'Pipeline', path: '/pipeline' },
    { name: 'Experiments', path: '/experiments' },
    { name: 'Models', path: '/models' },
    { name: 'Results', path: '/results' },
    { name: 'SURS', path: '/surs' },
    { name: 'Docs', path: '/docs' },
  ];

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'bg-[#0a0f1d]/90 backdrop-blur-md border-b border-white/10 py-3 shadow-2xl' : 'bg-transparent py-5'}`}>
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold text-white tracking-tighter flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-indigo-500 flex items-center justify-center text-sm shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            CS
          </div>
          CSUP
        </Link>
        
        <div className="hidden lg:flex items-center gap-6">
          {links.map((link) => {
            const isActive = location.pathname === link.path;
            return (
              <Link 
                key={link.name} 
                to={link.path}
                className={`text-sm font-medium transition-colors ${isActive ? 'text-cyan-400' : 'text-slate-300 hover:text-white'}`}
              >
                {link.name}
              </Link>
            );
          })}
          <Link to="/citation" className="px-5 py-2 rounded-full bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors border border-white/10 hover:shadow-lg">
            Citation
          </Link>
        </div>
      </div>
    </nav>
  );
}
