import { Fragment } from 'react';
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Menu as MenuIcon, X, User, Sun, Moon, LogOut, Settings } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function Navbar() {
  const { currentUser, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', current: location.pathname === '/' },
  ];

  if (currentUser && currentUser.userType === 'RIDER') {
    navigation.push(
      { name: 'Book a Ride', href: '/book-ride', current: location.pathname === '/book-ride' },
      { name: 'My Rides', href: '/my-rides', current: location.pathname === '/my-rides' }
    );
  }

  if (currentUser && currentUser.userType === 'DRIVER') {
    navigation.push(
      { name: 'Available Rides', href: '/available-rides', current: location.pathname === '/available-rides' },
      { name: 'My Rides', href: '/my-rides', current: location.pathname === '/my-rides' },
      { name: 'Set Availability', href: '/availability', current: location.pathname === '/availability' }
    );
  }

  navigation.push({ name: 'System Stats', href: '/stats', current: location.pathname === '/stats' });

  return (
    <Disclosure as="nav" className="bg-white dark:bg-gray-900 shadow-lg transition-colors duration-200">
      {({ open }) => (
        <>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 justify-between">
              <div className="flex">
                <div className="flex flex-shrink-0 items-center">
                  <Link to="/" className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                      <span className="text-white text-xl font-bold">C</span>
                    </div>
                    <span className="text-gray-900 dark:text-white text-xl font-bold">CabConnect</span>
                  </Link>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  {currentUser && navigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={classNames(
                        item.current
                          ? 'border-primary-500 text-gray-900 dark:text-white'
                          : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-primary-300 hover:text-gray-700 dark:hover:text-gray-200',
                        'inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium transition-colors duration-200'
                      )}
                      aria-current={item.current ? 'page' : undefined}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:items-center space-x-4">
                <button
                  onClick={toggleTheme}
                  className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200"
                  aria-label="Toggle theme"
                >
                  {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                </button>
                {currentUser ? (
                  <Menu as="div" className="relative ml-3">
                    <div>
                      <Menu.Button className="relative flex items-center space-x-2 rounded-full bg-gray-100 dark:bg-gray-800 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 transition-colors duration-200">
                        <User className="h-5 w-5" />
                        <span className="hidden md:block">{currentUser.name || currentUser.username}</span>
                      </Menu.Button>
                    </div>
                    <Transition as={Fragment} enter="transition ease-out duration-200" enterFrom="transform opacity-0 scale-95" enterTo="transform opacity-100 scale-100" leave="transition ease-in duration-75" leaveFrom="transform opacity-100 scale-100" leaveTo="transform opacity-0 scale-95">
                      <Menu.Items className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-lg bg-white dark:bg-gray-800 py-1 shadow-lg ring-1 ring-black ring-opacity-5 dark:ring-gray-700 focus:outline-none">
                        <div className="block px-4 py-3 text-sm border-b border-gray-200 dark:border-gray-700">
                          <div className="font-medium text-gray-900 dark:text-white">{currentUser.name || currentUser.username}</div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2 mt-1">
                            <span className="px-2 py-0.5 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 rounded-full text-xs font-medium">{currentUser.userType}</span>
                          </div>
                        </div>
                        <Menu.Item>
                          {({ active }) => (
                            <Link to="/profile" className={classNames(active ? 'bg-gray-100 dark:bg-gray-700' : '', 'flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-200')}>
                              <User className="h-4 w-4" />
                              Your Profile
                            </Link>
                          )}
                        </Menu.Item>
                        <Menu.Item>
                          {({ active }) => (
                            <Link to="/settings" className={classNames(active ? 'bg-gray-100 dark:bg-gray-700' : '', 'flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-200')}>
                              <Settings className="h-4 w-4" />
                              Settings
                            </Link>
                          )}
                        </Menu.Item>
                        <Menu.Item>
                          {({ active }) => (
                            <button onClick={logout} className={classNames(active ? 'bg-gray-100 dark:bg-gray-700' : '', 'flex w-full items-center gap-2 px-4 py-2 text-sm text-red-600 dark:text-red-400')}>
                              <LogOut className="h-4 w-4" />
                              Sign out
                            </button>
                          )}
                        </Menu.Item>
                      </Menu.Items>
                    </Transition>
                  </Menu>
                ) : (
                  <div className="flex space-x-4">
                    <Link to="/login" className="rounded-md bg-primary-600 px-3 py-2 text-sm font-medium text-white hover:bg-primary-500">Log in</Link>
                    <Link to="/register" className="rounded-md bg-white dark:bg-gray-800 px-3 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:bg-gray-50 dark:hover:bg-gray-700">Register</Link>
                  </div>
                )}
              </div>
              <div className="-mr-2 flex items-center sm:hidden">
                <button onClick={toggleTheme} className="mr-2 p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800" aria-label="Toggle theme">
                  {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                </button>
                <Disclosure.Button className="relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500">
                  <span className="absolute -inset-0.5" />
                  <span className="sr-only">Open main menu</span>
                  {open ? <X className="block h-6 w-6" aria-hidden="true" /> : <MenuIcon className="block h-6 w-6" aria-hidden="true" />}
                </Disclosure.Button>
              </div>
            </div>
          </div>
          <Disclosure.Panel className="sm:hidden">
            <div className="space-y-1 pb-3 pt-2">
              {currentUser && navigation.map((item) => (
                <Disclosure.Button key={item.name} as={Link} to={item.href} className={classNames(item.current ? 'border-primary-500 bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-200' : 'border-transparent text-gray-600 dark:text-gray-400 hover:border-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-800 dark:hover:text-gray-200', 'block border-l-4 py-2 pl-3 pr-4 text-base font-medium')} aria-current={item.current ? 'page' : undefined}>
                  {item.name}
                </Disclosure.Button>
              ))}
            </div>
            {currentUser && (
              <div className="border-t border-gray-200 dark:border-gray-700 pb-3 pt-4">
                <div className="flex items-center px-4">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-primary-200 dark:bg-primary-800 flex items-center justify-center">
                      <User className="h-6 w-6 text-primary-700 dark:text-primary-200" />
                    </div>
                  </div>
                  <div className="ml-3">
                    <div className="text-base font-medium text-gray-800 dark:text-white">{currentUser.name || currentUser.username}</div>
                    <div className="text-sm font-medium text-gray-500 dark:text-gray-400">{currentUser.email}</div>
                  </div>
                </div>
                <div className="mt-3 space-y-1">
                  <Disclosure.Button as={Link} to="/profile" className="block px-4 py-2 text-base font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-800 dark:hover:text-gray-200">
                    Your Profile
                  </Disclosure.Button>
                  <Disclosure.Button as={Link} to="/settings" className="block px-4 py-2 text-base font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-800 dark:hover:text-gray-200">
                    Settings
                  </Disclosure.Button>
                  <Disclosure.Button as="button" onClick={logout} className="block w-full text-left px-4 py-2 text-base font-medium text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-800">
                    Sign out
                  </Disclosure.Button>
                </div>
              </div>
            )}
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}
