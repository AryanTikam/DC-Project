import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import { Toaster } from 'react-hot-toast';

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        <Outlet />
      </main>
      <footer className="bg-gray-800 text-white py-6 mt-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <div className="mb-4 sm:mb-0">
              <h2 className="text-xl font-bold">CabConnect</h2>
              <p className="text-sm text-gray-300">A distributed cab booking system</p>
            </div>
            <div className="text-sm text-gray-300">
              <p>© {new Date().getFullYear()} CabConnect. All rights reserved.</p>
              <p>Powered by Distributed Systems</p>
            </div>
          </div>
        </div>
      </footer>
      <Toaster position="top-right" />
    </div>
  );
}