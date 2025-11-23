'use client';

import { use } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { requestsAPI } from '@/lib/api';
import { PurchaseRequest, User } from '@/lib/types';
import { format } from 'date-fns';
import { useState } from 'react';

export default function RequestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(params.id as string);
  const [comment, setComment] = useState('');
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);

  const user: User | null = typeof window !== 'undefined' 
    ? JSON.parse(localStorage.getItem('user') || 'null')
    : null;

  const { data: request, isLoading, refetch } = useQuery({
    queryKey: ['request', id],
    queryFn: async () => {
      const response = await requestsAPI.get(id);
      return response.data;
    },
  });

  const approveMutation = useMutation({
    mutationFn: async (comment?: string) => {
      await requestsAPI.approve(id, comment);
    },
    onSuccess: () => {
      refetch();
      setShowApproveModal(false);
      setComment('');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: async (comment: string) => {
      await requestsAPI.reject(id, comment);
    },
    onSuccess: () => {
      refetch();
      setShowRejectModal(false);
      setComment('');
    },
  });

  const canApprove = user && (user.role === 'approver_level_1' || user.role === 'approver_level_2');
  const canViewAll = user && (canApprove || user.role === 'finance');

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  if (!request) {
    return <div className="text-center py-12">Request not found</div>;
  }

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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold">{request.title}</h2>
              <span
                className={`mt-2 inline-block px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(
                  request.status
                )}`}
              >
                {request.status.toUpperCase()}
              </span>
            </div>
            {canApprove && request.can_approve && (
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowApproveModal(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Approve
                </button>
                <button
                  onClick={() => setShowRejectModal(true)}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Reject
                </button>
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">Description</h3>
              <p className="text-gray-700">{request.description}</p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Amount</h3>
              <p className="text-2xl font-bold text-indigo-600">
                ${request.amount}
              </p>
            </div>

            {request.items && request.items.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2">Items</h3>
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Item
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Quantity
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {request.items.map((item, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.item_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.quantity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ${item.price}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ${item.total}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {request.approvals && request.approvals.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2">Approval History</h3>
                <div className="space-y-4">
                  {request.approvals.map((approval) => (
                    <div
                      key={approval.id}
                      className="border-l-4 border-indigo-500 pl-4 py-2"
                    >
                      <div className="flex justify-between">
                        <span className="font-medium">
                          Level {approval.level} - {approval.approver_name}
                        </span>
                        <span
                          className={`px-2 py-1 rounded text-xs ${getStatusColor(
                            approval.status
                          )}`}
                        >
                          {approval.status}
                        </span>
                      </div>
                      {approval.comment && (
                        <p className="text-sm text-gray-600 mt-1">
                          {approval.comment}
                        </p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        {format(new Date(approval.updated_at), 'MMM d, yyyy HH:mm')}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Created by:</span>{' '}
                <span className="font-medium">{request.created_by_name}</span>
              </div>
              <div>
                <span className="text-gray-500">Created at:</span>{' '}
                <span className="font-medium">
                  {format(new Date(request.created_at), 'MMM d, yyyy HH:mm')}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Approve Modal */}
      {showApproveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Approve Request</h3>
            <textarea
              className="w-full border rounded-md p-2 mb-4"
              placeholder="Comment (optional)"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => {
                  setShowApproveModal(false);
                  setComment('');
                }}
                className="px-4 py-2 border rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={() => approveMutation.mutate(comment)}
                disabled={approveMutation.isPending}
                className="px-4 py-2 bg-green-600 text-white rounded-md disabled:opacity-50"
              >
                {approveMutation.isPending ? 'Approving...' : 'Approve'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Reject Request</h3>
            <textarea
              className="w-full border rounded-md p-2 mb-4"
              placeholder="Rejection reason (required)"
              required
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setComment('');
                }}
                className="px-4 py-2 border rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (comment.trim()) {
                    rejectMutation.mutate(comment);
                  }
                }}
                disabled={rejectMutation.isPending || !comment.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded-md disabled:opacity-50"
              >
                {rejectMutation.isPending ? 'Rejecting...' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

