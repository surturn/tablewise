import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center bg-brand-light">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-brand-dark mb-6">
          The Best Food in <span className="text-brand-orange">Nairobi</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Order online, track your delivery in real-time, and enjoy meals cooked to perfection.
        </p>
        <Link
          to="/menu"
          className="px-8 py-3 bg-brand-orange text-white text-lg font-semibold rounded shadow hover:bg-orange-600 transition"
        >
          View Menu
        </Link>
      </div>
    </div>
  );
};

export default Home;