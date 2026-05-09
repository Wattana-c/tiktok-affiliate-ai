import { useState, useEffect } from 'react';
import api from '../api';

export default function Settings() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [platform, setPlatform] = useState('tiktok');
  const [accountName, setAccountName] = useState('');

  const fetchAccounts = async () => {
    try {
      const res = await api.get('/v1/accounts/');
      setAccounts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleAddAccount = async () => {
    try {
      await api.post('/v1/accounts/', {
        platform,
        account_name: accountName,
        access_token: 'mock_token_for_now',
        is_active: true
      });
      setAccountName('');
      fetchAccounts();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="py-6 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">ตั้งค่า (Settings)</h1>

      <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6 mb-8 border-t-4 border-indigo-500">
        <div className="md:grid md:grid-cols-3 md:gap-6">
          <div className="md:col-span-1">
            <h3 className="text-lg font-medium leading-6 text-gray-900">การโพสต์อัตโนมัติ (Auto-Post Logic)</h3>
            <p className="mt-1 text-sm text-gray-500">ตั้งค่าคะแนนเทรนด์สำหรับเงื่อนไขการโพสต์หรือรอตรวจสอบ</p>
          </div>
          <div className="mt-5 md:mt-0 md:col-span-2 space-y-6">
            <div className="grid grid-cols-6 gap-6">
              <div className="col-span-6 sm:col-span-3">
                <label className="block text-sm font-medium text-gray-700">เกณฑ์การโพสต์อัตโนมัติ (คะแนนเทรนด์)</label>
                <input type="number" defaultValue={80} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 sm:text-sm" />
                <p className="mt-1 text-xs text-gray-500">หากคะแนน &ge; จะถูกโพสต์โดยอัตโนมัติ</p>
              </div>
              <div className="col-span-6 sm:col-span-3">
                <label className="block text-sm font-medium text-gray-700">เกณฑ์การรออนุมัติ (คะแนนเทรนด์)</label>
                <input type="number" defaultValue={50} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 sm:text-sm" />
                <p className="mt-1 text-xs text-gray-500">หากคะแนนต่ำกว่าเกณฑ์โพสต์แต่มากกว่าค่านี้ จะถูกส่งไปที่คิวรอการตรวจสอบ</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6 mb-8 border-t-4 border-blue-500">
        <div className="md:grid md:grid-cols-3 md:gap-6">
          <div className="md:col-span-1">
            <h3 className="text-lg font-medium leading-6 text-gray-900">บัญชีที่เชื่อมต่อ (Linked Accounts)</h3>
            <p className="mt-1 text-sm text-gray-500">จัดการบัญชีโซเชียลมีเดียที่ใช้สำหรับการโพสต์</p>
          </div>
          <div className="mt-5 md:mt-0 md:col-span-2 space-y-6">
            <div className="grid grid-cols-6 gap-6">
              <div className="col-span-6 sm:col-span-3">
                <label className="block text-sm font-medium text-gray-700">แพลตฟอร์ม (Platform)</label>
                <select value={platform} onChange={e => setPlatform(e.target.value)} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                  <option value="tiktok">TikTok</option>
                  <option value="facebook">Facebook</option>
                </select>
              </div>
              <div className="col-span-6 sm:col-span-3">
                <label className="block text-sm font-medium text-gray-700">ชื่อบัญชี (Account Name)</label>
                <input type="text" value={accountName} onChange={e => setAccountName(e.target.value)} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
              </div>
            </div>
            <button onClick={handleAddAccount} className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
              เพิ่มบัญชี (Add Account)
            </button>

            <div className="mt-6 border-t border-gray-200 pt-6">
              <ul className="divide-y divide-gray-200">
                {accounts.map(acc => (
                  <li key={acc.id} className="py-4 flex justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{acc.account_name}</p>
                      <p className="text-sm text-gray-500 capitalize">{acc.platform}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${acc.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                        {acc.is_active ? 'ใช้งานอยู่ (Active)' : 'ไม่ได้ใช้งาน (Inactive)'}
                      </span>
                      {acc.is_shadowbanned && (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                          ถูกระงับ (Shadowbanned)
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
