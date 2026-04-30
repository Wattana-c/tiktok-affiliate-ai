import { useState, useEffect } from 'react';
import axios from 'axios';

export default function PostQueue() {
  const [queue, setQueue] = useState<any[]>([]);

  const fetchQueue = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/v1/queue/');
      setQueue(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleAction = async (id: number, action: 'approve' | 'retry') => {
    try {
      await axios.put(`http://localhost:8000/api/v1/queue/${id}/${action}`);
      fetchQueue();
    } catch (err) {
      console.error(err);
      alert('Action failed. Check console.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'review': return 'bg-blue-100 text-blue-800';
      case 'posted': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Automation Queue</h1>

      <div className="flex flex-col">
        <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product ID</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account ID</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Retries</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {queue.map((item) => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.product_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.account_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(item.status)}`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.retry_count}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {item.status === 'review' && (
                          <button onClick={() => handleAction(item.id, 'approve')} className="text-indigo-600 hover:text-indigo-900 mr-4">Approve</button>
                        )}
                        {item.status === 'failed' && (
                          <button onClick={() => handleAction(item.id, 'retry')} className="text-red-600 hover:text-red-900 mr-4">Retry</button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {queue.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">No items in the queue</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
