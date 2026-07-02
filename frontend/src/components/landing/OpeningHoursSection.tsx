import React from 'react';

export const OpeningHoursSection: React.FC = () => {
  return (
    <section className="py-24 bg-[#1e2024]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-white mb-4">Opening Hours</h2>
          <div className="flex items-center justify-center gap-2">
            <div className="h-[1px] w-12 bg-yellow-600/50" />
            <div className="w-2 h-2 rotate-45 border border-yellow-600/50" />
            <div className="h-[1px] w-12 bg-yellow-600/50" />
          </div>
        </div>

        <div className="flex flex-col lg:flex-row justify-center items-center gap-16 lg:gap-0 mt-12">
          
          {/* Hours Card */}
          <div className="w-full lg:w-[500px] bg-[#15161a] p-10 rounded-sm shadow-2xl relative z-10 border border-gray-800">
            {/* Decorative Corner Patterns */}
            <div className="absolute -top-4 -left-4 w-12 h-12 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPjxyZWN0IHdpZHRoPSI0IiBoZWlnaHQ9IjQiIGZpbGw9IiNkNGFmMzciIGZpbGwtb3BhY2l0eT0iMC4zIi8+PC9zdmc+')] opacity-50" />
            <div className="absolute -bottom-4 right-8 w-16 h-12 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPjxyZWN0IHdpZHRoPSI0IiBoZWlnaHQ9IjQiIGZpbGw9IiNkNGFmMzciIGZpbGwtb3BhY2l0eT0iMC4zIi8+PC9zdmc+')] opacity-50" />

            <div className="space-y-6">
              {/* Everyday */}
              <div className="flex justify-between items-center border-b border-gray-800 pb-4">
                <div className="text-sm">
                  <p className="text-white font-medium">Monday,</p>
                  <p className="text-gray-400">Wednesday - Sunday</p>
                </div>
                <div className="text-white text-sm font-medium">05:00 pm - 10:00 pm</div>
              </div>

              {/* Pickup Service */}
              <div className="flex justify-between items-center border-b border-gray-800 pb-4">
                <div className="text-sm">
                  <p className="text-[#d4af37] font-semibold mb-1">Pickup Service</p>
                  <p className="text-white font-medium">Monday,</p>
                  <p className="text-gray-400">Wednesday - Sunday</p>
                </div>
                <div className="text-white text-sm font-medium">05:00 pm - 10:00 pm</div>
              </div>

              {/* Delivery Service */}
              <div className="flex justify-between items-center border-b border-gray-800 pb-4">
                <div className="text-sm">
                  <p className="text-[#d4af37] font-semibold mb-1">Delivery Service</p>
                  <p className="text-white font-medium">Monday,</p>
                  <p className="text-gray-400">Wednesday - Sunday</p>
                </div>
                <div className="text-white text-sm font-medium">05:00 pm - 10:00 pm</div>
              </div>

              {/* Table Reservation */}
              <div className="flex justify-between items-center">
                <div className="text-sm">
                  <p className="text-[#d4af37] font-semibold mb-1">Table Reservation</p>
                  <p className="text-white font-medium">Monday,</p>
                  <p className="text-gray-400">Wednesday - Sunday</p>
                </div>
                <div className="text-white text-sm font-medium">04:45 pm - 10:00 pm</div>
              </div>
            </div>
          </div>

          {/* Restaurant Interior Image Overlap */}
          <div className="w-full lg:w-[400px] h-[500px] lg:-ml-16 relative z-0 mt-8 lg:mt-16">
            <img 
              src="/images/landingPage/BarSection.jpg" 
              alt="Restaurant Interior" 
              className="w-full h-full object-cover rounded-md shadow-2xl brightness-75"
              style={{ borderRadius: '4px 100px 4px 4px' }}
            />
          </div>

        </div>

      </div>
    </section>
  );
};
