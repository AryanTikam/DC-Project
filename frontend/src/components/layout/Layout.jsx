import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import { Toaster } from 'react-hot-toast';

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Navbar />
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        <Outlet />
      </main>
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 py-6 mt-10 transition-colors duration-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <div className="mb-4 sm:mb-0">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">CabConnect</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">A distributed cab booking system</p>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
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