
interface ProductCardProps {
  product: any;
  onGenerateClick: (id: number) => void;
}

export default function ProductCard({ product, onGenerateClick }: ProductCardProps) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg flex flex-col h-full">
      <div className="p-5 flex-grow">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg leading-6 font-medium text-gray-900 truncate" title={product.name}>{product.name}</h3>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Trend: {product.trend_score || 'N/A'}
          </span>
        </div>
        <p className="mt-1 max-w-2xl text-sm text-gray-500 line-clamp-3">{product.description}</p>
        <div className="mt-4">
          <p className="text-sm font-semibold text-gray-900">{product.price} {product.currency}</p>
        </div>
      </div>
      <div className="bg-gray-50 px-5 py-3 border-t border-gray-200">
         <button
            onClick={() => onGenerateClick(product.id)}
            className="w-full flex justify-center items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Generate AI Content
          </button>
      </div>
    </div>
  );
}
