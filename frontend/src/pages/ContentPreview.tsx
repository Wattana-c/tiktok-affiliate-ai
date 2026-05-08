import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';

export default function ContentPreview() {
  const [searchParams] = useSearchParams();
  const productId = searchParams.get('productId');
  const [language, setLanguage] = useState('Thai');
  const [variants, setVariants] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(0);

  const generateVariants = async () => {
    if (!productId) return;
    setLoading(true);
    try {
      const res = await api.post(`/v1/ai/generate-variants/${productId}?language=${language}`);
      setVariants(res.data);
      setSelectedVariant(0);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="py-6 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">AI Content Studio</h1>

      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex items-center space-x-4 mb-4">
          <label className="text-sm font-medium text-gray-700">Language:</label>
          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
            className="block w-48 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option value="Thai">Thai</option>
            <option value="English">English</option>
          </select>
          <button
            onClick={generateVariants}
            disabled={loading || !productId}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Generating Variants...' : 'Generate A/B Variants'}
          </button>
        </div>

        {variants.length > 0 && (
          <div className="mt-8">
            <div className="flex space-x-4 mb-6 overflow-x-auto border-b border-gray-200 pb-2">
              {variants.map((v, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedVariant(idx)}
                  className={`px-4 py-2 font-medium text-sm rounded-t-lg transition-colors ${
                    selectedVariant === idx ? 'bg-indigo-100 text-indigo-700 border-b-2 border-indigo-700' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {v.variant_name || `Variant ${idx + 1}`}
                </button>
              ))}
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-medium text-gray-500 flex items-center justify-between">
                  <span>Viral Hook</span>
                  <span className="text-xs bg-gray-200 px-2 py-1 rounded-full">{variants[selectedVariant].content_mode}</span>
                </h3>
                <p className="mt-1 text-sm text-gray-900 font-bold bg-gray-50 p-3 rounded">{variants[selectedVariant].hook}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500">Caption</h3>
                <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap bg-gray-50 p-3 rounded">{variants[selectedVariant].caption}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500">Video Script Idea</h3>
                <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap bg-gray-50 p-3 rounded">{variants[selectedVariant].video_script}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500">Call to Action</h3>
                <p className="mt-1 text-sm text-gray-900 bg-gray-50 p-3 rounded">{variants[selectedVariant].cta}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500">Hashtags</h3>
                <p className="mt-1 text-sm text-blue-600 bg-gray-50 p-3 rounded">{variants[selectedVariant].hashtags}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
