'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { authAPI } from '@/lib/api';

export default function Home() {
  const router = useRouter();

  const { data: user } = useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const response = await authAPI.me();
      return response.data;
    },
    retry: false,
  });

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
    } else if (user) {
      router.push('/dashboard');
    }
  }, [user, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Loading...</h1>
      </div>
    </div>
  );
}

