import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Template {
  id: number;
  name: string;
  description: string;
  category: string;
  tags: string[];
  thumbnail_path?: string;
  preview_video_path?: string;
  duration: number;
  is_public: boolean;
  is_featured: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

interface TemplateStats {
  total_templates: number;
  categories: Record<string, number>;
  featured_count: number;
  public_count: number;
}

const Templates: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [featuredTemplates, setFeaturedTemplates] = useState<Template[]>([]);
  const [stats, setStats] = useState<TemplateStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    { value: 'all', label: 'All Templates' },
    { value: 'business', label: 'Business' },
    { value: 'marketing', label: 'Marketing' },
    { value: 'education', label: 'Education' },
    { value: 'entertainment', label: 'Entertainment' },
    { value: 'social_media', label: 'Social Media' },
    { value: 'presentation', label: 'Presentation' },
    { value: 'tutorial', label: 'Tutorial' },
    { value: 'promotional', label: 'Promotional' }
  ];

  useEffect(() => {
    fetchTemplates();
    fetchFeaturedTemplates();
    fetchStats();
  }, [selectedCategory, searchQuery]);

  const fetchTemplates = async () => {
    try {
      setIsLoading(true);
      const params = new URLSearchParams();
      
      if (selectedCategory !== 'all') {
        params.append('category', selectedCategory);
      }
      
      if (searchQuery) {
        params.append('search', searchQuery);
      }
      
      params.append('limit', '20');
      
      const response = await axios.get(`/api/v1/templates?${params.toString()}`);
      
      if (response.data.success) {
        setTemplates(response.data.data);
      } else {
        setError('Failed to fetch templates');
      }
    } catch (error: any) {
      console.error('Error fetching templates:', error);
      setError('Failed to load templates. Please try again.');
      // Set empty array to show empty state instead of error
      setTemplates([]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchFeaturedTemplates = async () => {
    try {
      const response = await axios.get('/api/v1/templates/featured?limit=6');
      
      if (response.data.success) {
        setFeaturedTemplates(response.data.data);
      }
    } catch (error: any) {
      console.error('Error fetching featured templates:', error);
      setFeaturedTemplates([]);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/v1/templates/stats');
      
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error: any) {
      console.error('Error fetching template stats:', error);
      setStats(null);
    }
  };

  const handleUseTemplate = async (templateId: number) => {
    try {
      await axios.post(`/api/v1/templates/${templateId}/use`);
      // You could redirect to video editor or show a success message
      alert('Template selected! Redirecting to video editor...');
      // navigate(`/video-editor?template=${templateId}`);
    } catch (error: any) {
      console.error('Error using template:', error);
      alert('Failed to use template. Please try again.');
    }
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const TemplateCard: React.FC<{ template: Template }> = ({ template }) => (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="relative">
        {template.thumbnail_path ? (
          <img
            src={template.thumbnail_path}
            alt={template.name}
            className="w-full h-48 object-cover"
          />
        ) : (
          <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl text-gray-400 mb-2">🎬</div>
              <p className="text-gray-500 text-sm">No Preview</p>
            </div>
          </div>
        )}
        
        {template.is_featured && (
          <div className="absolute top-2 left-2 bg-yellow-500 text-white px-2 py-1 rounded text-xs font-semibold">
            Featured
          </div>
        )}
        
        <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs">
          {formatDuration(template.duration)}
        </div>
      </div>
      
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2 text-gray-900">{template.name}</h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{template.description}</p>
        
        <div className="flex flex-wrap gap-1 mb-3">
          {template.tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
            >
              {tag}
            </span>
          ))}
          {template.tags.length > 3 && (
            <span className="text-gray-500 text-xs">+{template.tags.length - 3} more</span>
          )}
        </div>
        
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            <span className="capitalize">{template.category}</span>
            <span className="mx-2">•</span>
            <span>{template.usage_count} uses</span>
          </div>
          
          <button
            onClick={() => handleUseTemplate(template.id)}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded text-sm"
          >
            Use Template
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Video Templates</h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choose from our collection of professional video templates to create stunning videos in minutes
            </p>
          </div>
          
          {/* Stats */}
          {stats && (
            <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.total_templates}</div>
                <div className="text-sm text-blue-800">Total Templates</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600">{stats.featured_count}</div>
                <div className="text-sm text-green-800">Featured</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-purple-600">{Object.keys(stats.categories).length}</div>
                <div className="text-sm text-purple-800">Categories</div>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-orange-600">{stats.public_count}</div>
                <div className="text-sm text-orange-800">Public Templates</div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Featured Templates */}
        {featuredTemplates.length > 0 && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredTemplates.map((template) => (
                <TemplateCard key={template.id} template={template} />
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {categories.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Templates Grid */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {selectedCategory === 'all' ? 'All Templates' : `${categories.find(c => c.value === selectedCategory)?.label} Templates`}
          </h2>
          
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="text-red-500 mb-4">⚠️ {error}</div>
              <button
                onClick={() => fetchTemplates()}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Try Again
              </button>
            </div>
          ) : templates.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 011 1v1a1 1 0 01-1 1h-1v12a2 2 0 01-2 2H6a2 2 0 01-2-2V7H3a1 1 0 01-1-1V5a1 1 0 011-1h4z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
              <p className="text-gray-500">
                {searchQuery || selectedCategory !== 'all' 
                  ? 'Try adjusting your search or filter criteria.' 
                  : 'Templates will appear here once they are added to the system.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {templates.map((template) => (
                <TemplateCard key={template.id} template={template} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Templates;
