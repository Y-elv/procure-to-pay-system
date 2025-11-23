'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { requestsAPI } from '@/lib/api';
import { RequestItem } from '@/lib/types';

export default function CreateRequestPage() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [proformaFile, setProformaFile] = useState<File | null>(null);
  const [items, setItems] = useState<RequestItem[]>([
    { item_name: '', quantity: 1, price: 0, total: 0 },
  ]);

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await requestsAPI.create(data);
      return response.data;
    },
    onSuccess: () => {
      router.push('/dashboard');
    },
  });

  const handleAddItem = () => {
    setItems([...items, { item_name: '', quantity: 1, price: 0, total: 0 }]);
  };

  const handleItemChange = (index: number, field: keyof RequestItem, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    if (field === 'quantity' || field === 'price') {
      newItems[index].total =
        Number(newItems[index].quantity) * Number(newItems[index].price);
    }
    setItems(newItems);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const totalAmount = items.reduce((sum, item) => sum + item.total, 0);
    
    const formData: any = {
      title,
      description,
      amount: totalAmount || amount,
      items: items.filter((item) => item.item_name),
    };

    if (proformaFile) {
      formData.proforma_file = proformaFile;
    }

    createMutation.mutate(formData);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-6">Create Purchase Request</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Title
              </label>
              <input
                type="text"
                required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                required
                rows={4}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Proforma File (Optional)
              </label>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                onChange={(e) => setProformaFile(e.target.files?.[0] || null)}
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Items
                </label>
                <button
                  type="button"
                  onClick={handleAddItem}
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  + Add Item
                </button>
              </div>
              <div className="space-y-4">
                {items.map((item, index) => (
                  <div key={index} className="flex gap-4 items-end">
                    <div className="flex-1">
                      <label className="block text-xs text-gray-600">
                        Item Name
                      </label>
                      <input
                        type="text"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                        value={item.item_name}
                        onChange={(e) =>
                          handleItemChange(index, 'item_name', e.target.value)
                        }
                      />
                    </div>
                    <div className="w-24">
                      <label className="block text-xs text-gray-600">
                        Quantity
                      </label>
                      <input
                        type="number"
                        min="1"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                        value={item.quantity}
                        onChange={(e) =>
                          handleItemChange(
                            index,
                            'quantity',
                            parseInt(e.target.value) || 1
                          )
                        }
                      />
                    </div>
                    <div className="w-32">
                      <label className="block text-xs text-gray-600">Price</label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                        value={item.price}
                        onChange={(e) =>
                          handleItemChange(
                            index,
                            'price',
                            parseFloat(e.target.value) || 0
                          )
                        }
                      />
                    </div>
                    <div className="w-32">
                      <label className="block text-xs text-gray-600">Total</label>
                      <div className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50">
                        ${item.total.toFixed(2)}
                      </div>
                    </div>
                    {items.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveItem(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <div className="mt-4 text-right">
                <span className="text-lg font-semibold">
                  Total: ${items.reduce((sum, item) => sum + item.total, 0).toFixed(2)}
                </span>
              </div>
            </div>

            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Request'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

