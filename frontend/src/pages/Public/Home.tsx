import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-light">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-brand-dark mb-4">
          Welcome to <span className="text-brand-orange">TableWise</span>
        </h1>
        <p className="text-lg text-gray-600">
          Routing, Global State, and API Interceptors are now active!
        </p>
      </div>
    </div>
  );
};

export default Home;