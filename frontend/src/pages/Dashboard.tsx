import { useState, useEffect } from 'react';
import axios from 'axios';
import ProductCard from '../components/ProductCard';

export default function Dashboard() {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchProducts = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/v1/products/');
      setProducts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleScrape = async () => {
    setLoading(true);
    try {
      await axios.post('http://localhost:8000/api/v1/scraper/scrape-mock-products');
      fetchProducts();
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-indigo-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Total Products</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">{products.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Top Trends (&gt;80)</h3>
          <p className="mt-2 text-3xl font-bold text-green-600">{topProducts}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-500 uppercase">Auto-Post Ready</h3>
          <p className="mt-2 text-3xl font-bold text-blue-600">{topProducts} items</p>
        </div>
      </div>

      <div className="flex justify-between items-center mb-6">
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
