import { useState, useEffect } from 'react';
import axios from 'axios';
import ProductCard from '../components/ProductCard';

export default function Dashboard() {
  const [products, setProducts] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [topStyles, setTopStyles] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [prodRes, statsRes, stylesRes] = await Promise.all([
        axios.get('http://localhost:8000/api/v1/products/'),
        axios.get('http://localhost:8000/api/v1/analytics/dashboard-stats'),
        axios.get('http://localhost:8000/api/v1/analytics/top-styles')
      ]);
      setProducts(prodRes.data);
      setStats(statsRes.data);
      setTopStyles(stylesRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleScrape = async () => {
    setLoading(true);
    try {
      await axios.post('http://localhost:8000/api/v1/scraper/scrape-mock-products');
      fetchData();
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleGenerate = (id: number) => {
    // Navigate or show modal
    console.log("Generate for", id);
    window.location.href = `/content?productId=${id}`;
  };

  const topProducts = products.filter(p => p.trend_score >= 80).length;

  return (
    <div className="py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Growth Engine Overview</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-indigo-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Total Conversions</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">{stats.total_conversions || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Conversion Rate</h3>
          <p className="mt-2 text-3xl font-bold text-green-600">{stats.conversion_rate || 0}%</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Total Clicks</h3>
          <p className="mt-2 text-3xl font-bold text-blue-600">{stats.total_clicks || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-purple-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Top Product Score</h3>
          <p className="mt-2 text-3xl font-bold text-purple-600" title={stats.top_product_name}>{stats.top_product_score || 0}</p>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Performing Styles (Strategy Engine)</h3>
        {topStyles.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {topStyles.map((s, idx) => (
              <li key={idx} className="py-3 flex justify-between items-center">
                <div>
                  <span className="font-medium text-gray-900">{s.metric_value}</span>
                  <span className="ml-2 text-xs text-gray-500 uppercase">({s.metric_type})</span>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-indigo-600">Score: {s.average_score.toFixed(1)}</p>
                  <p className="text-xs text-gray-500">Used {s.total_uses} times</p>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500">No performance data yet.</p>
        )}
      </div>

      <div className="flex justify-between items-center mb-6 mt-12">
        <h1 className="text-2xl font-semibold text-gray-900">Trending Products</h1>
        <button
          onClick={handleScrape}
          disabled={loading}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none disabled:opacity-50"
        >
          {loading ? 'Scraping...' : 'Fetch New Trends'}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} onGenerateClick={handleGenerate} />
        ))}
      </div>
    </div>
  );
}
