'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { authAPI, requestsAPI } from '@/lib/api';
import { User, PurchaseRequest } from '@/lib/types';
import { format } from 'date-fns';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    } else {
      router.push('/login');
    }
  }, [router]);

  const { data: requests, isLoading } = useQuery({
    queryKey: ['requests'],
    queryFn: async () => {
      const response = await requestsAPI.list();
      return response.data.results || response.data;
    },
    enabled: !!user,
  });

  const handleLogout = async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      try {
        await authAPI.logout(refresh);
      } catch (e) {
        // Ignore errors
      }
    }
    localStorage.clear();
    router.push('/login');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">Procure-to-Pay</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {user.username} ({user.role})
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-700 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
            {user.role === 'staff' && (
              <Link
                href="/requests/create"
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Create Request
              </Link>
            )}
          </div>

          {isLoading ? (
            <div className="text-center py-12">Loading requests...</div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {requests && requests.length > 0 ? (
                  requests.map((request: PurchaseRequest) => (
                    <li key={request.id}>
                      <Link
                        href={`/requests/${request.id}`}
                        className="block hover:bg-gray-50"
                      >
                        <div className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-indigo-600 truncate">
                              {request.title}
                            </p>
                            <div className="ml-2 flex-shrink-0 flex">
                              <span
                                className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                                  request.status
                                )}`}
                              >
                                {request.status}
                              </span>
                            </div>
                          </div>
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex">
                              <p className="flex items-center text-sm text-gray-500">
                                Amount: ${request.amount}
                              </p>
                            </div>
                            <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                              <p>
                                Created:{' '}
                                {format(
                                  new Date(request.created_at),
                                  'MMM d, yyyy'
                                )}
                              </p>
                            </div>
                          </div>
                        </div>
                      </Link>
                    </li>
                  ))
                ) : (
                  <li className="px-4 py-8 text-center text-gray-500">
                    No requests found
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

