import { Fragment } from 'react';
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Bars3Icon, XMarkIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const userNavigation = [
  { name: 'Your Profile', href: '/profile' },
  { name: 'Settings', href: '/settings' },
];

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function Navbar() {
  const { currentUser, logout } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', current: location.pathname === '/' },
    { name: 'Book a Ride', href: '/book-ride', current: location.pathname === '/book-ride' },
    { name: 'My Rides', href: '/my-rides', current: location.pathname === '/my-rides' },
  ];

  // Add driver-specific navigation items
  if (currentUser && currentUser.userType === 'DRIVER') {
    navigation.push(
      { name: 'Available Rides', href: '/available-rides', current: location.pathname === '/available-rides' },
      { name: 'Set Availability', href: '/availability', current: location.pathname === '/availability' }
    );
  }

  // Add system stats for all users
  navigation.push({ name: 'System Stats', href: '/stats', current: location.pathname === '/stats' });

  return (
    <Disclosure as="nav" className="bg-primary-800 shadow-lg">
      {({ open }) => (
        <>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 justify-between">
              <div className="flex">
                <div className="flex flex-shrink-0 items-center">
                  <Link to="/">
                    <span className="text-white text-2xl font-bold">CabConnect</span>
                  </Link>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  {/* Current: "border-primary-500 text-gray-900", Default: "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700" */}
                  {currentUser && navigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={classNames(
                        item.current
                          ? 'border-primary-500 text-white'
                          : 'border-transparent text-gray-300 hover:border-primary-300 hover:text-white',
                        'inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium'
                      )}
                      aria-current={item.current ? 'page' : undefined}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:items-center">
                {/* Profile dropdown */}
                {currentUser ? (
                  <Menu as="div" className="relative ml-3">
                    <div>
                      <Menu.Button className="relative flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                        <span className="absolute -inset-1.5" />
                        <span className="sr-only">Open user menu</span>
                        <UserCircleIcon className="h-8 w-8 rounded-full bg-primary-200 p-1 text-primary-800" />
                      </Menu.Button>
                    </div>
                    <Transition
                      as={Fragment}
                      enter="transition ease-out duration-200"
                      enterFrom="transform opacity-0 scale-95"
                      enterTo="transform opacity-100 scale-100"
                      leave="transition ease-in duration-75"
                      leaveFrom="transform opacity-100 scale-100"
                      leaveTo="transform opacity-0 scale-95"
                    >
                      <Menu.Items className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                        <div className="block px-4 py-2 text-sm text-gray-700 border-b border-gray-200">
                          <div className="font-medium">{currentUser.name || currentUser.username}</div>
                          <div className="text-xs text-gray-500">{currentUser.userType}</div>
                        </div>
                        {userNavigation.map((item) => (
                          <Menu.Item key={item.name}>
                            {({ active }) => (
                              <Link
                                to={item.href}
                                className={classNames(
                                  active ? 'bg-gray-100' : '',
                                  'block px-4 py-2 text-sm text-gray-700'
                                )}
                              >
                                {item.name}
                              </Link>
                            )}
                          </Menu.Item>
                        ))}
                        <Menu.Item>
                          {({ active }) => (
                            <a
                              href="#"
                              onClick={(e) => {
                                e.preventDefault();
                                logout();
                              }}
                              className={classNames(
                                active ? 'bg-gray-100' : '',
                                'block px-4 py-2 text-sm text-gray-700'
                              )}
                            >
                              Sign out
                            </a>
                          )}
                        </Menu.Item>
                      </Menu.Items>
                    </Transition>
                  </Menu>
                ) : (
                  <div className="flex space-x-4">
                    <Link
                      to="/login"
                      className="rounded-md bg-primary-600 px-3 py-2 text-sm font-medium text-white hover:bg-primary-500"
                    >
                      Log in
                    </Link>
                    <Link
                      to="/register"
                      className="rounded-md bg-white px-3 py-2 text-sm font-medium text-primary-600 hover:bg-gray-50"
                    >
                      Register
                    </Link>
                  </div>
                )}
              </div>
              <div className="-mr-2 flex items-center sm:hidden">
                {/* Mobile menu button */}
                <Disclosure.Button className="relative inline-flex items-center justify-center rounded-md p-2 text-gray-200 hover:bg-primary-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
                  <span className="absolute -inset-0.5" />
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Disclosure.Button>
              </div>
            </div>
          </div>

          <Disclosure.Panel className="sm:hidden">
            <div className="space-y-1 pb-3 pt-2">
              {currentUser && navigation.map((item) => (
                <Disclosure.Button
                  key={item.name}
                  as={Link}
                  to={item.href}
                  className={classNames(
                    item.current
                      ? 'bg-primary-700 text-white'
                      : 'text-gray-300 hover:bg-primary-700 hover:text-white',
                    'block py-2 pl-3 pr-4 text-base font-medium'
                  )}
                  aria-current={item.current ? 'page' : undefined}
                >
                  {item.name}
                </Disclosure.Button>
              ))}
            </div>
            <div className="border-t border-primary-700 pb-3 pt-4">
              {currentUser ? (
                <>
                  <div className="flex items-center px-4">
                    <div className="flex-shrink-0">
                      <UserCircleIcon className="h-8 w-8 rounded-full bg-primary-200 p-1 text-primary-800" />
                    </div>
                    <div className="ml-3">
                      <div className="text-base font-medium text-white">{currentUser.name || currentUser.username}</div>
                      <div className="text-sm font-medium text-gray-300">{currentUser.userType}</div>
                    </div>
                  </div>
                  <div className="mt-3 space-y-1">
                    {userNavigation.map((item) => (
                      <Disclosure.Button
                        key={item.name}
                        as={Link}
                        to={item.href}
                        className="block px-4 py-2 text-base font-medium text-gray-300 hover:bg-primary-700 hover:text-white"
                      >
                        {item.name}
                      </Disclosure.Button>
                    ))}
                    <Disclosure.Button
                      as="a"
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        logout();
                      }}
                      className="block px-4 py-2 text-base font-medium text-gray-300 hover:bg-primary-700 hover:text-white"
                    >
                      Sign out
                    </Disclosure.Button>
                  </div>
                </>
              ) : (
                <div className="flex flex-col space-y-2 px-4">
                  <Link
                    to="/login"
                    className="w-full rounded-md bg-primary-600 px-3 py-2 text-center text-sm font-medium text-white hover:bg-primary-500"
                  >
                    Log in
                  </Link>
                  <Link
                    to="/register"
                    className="w-full rounded-md bg-white px-3 py-2 text-center text-sm font-medium text-primary-600 hover:bg-gray-50"
                  >
                    Register
                  </Link>
                </div>
              )}
            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}