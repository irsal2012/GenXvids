import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

interface VideoElement {
  id: string;
  type: 'text' | 'image' | 'video' | 'audio';
  content: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  style: {
    fontSize?: number;
    fontFamily?: string;
    color?: string;
    backgroundColor?: string;
    opacity?: number;
  };
  timing: {
    start: number;
    duration: number;
  };
}

interface Project {
  id: number;
  name: string;
  description: string;
  elements: VideoElement[];
  duration: number;
  template_id?: number;
}

interface Template {
  id: number;
  name: string;
  description: string;
  elements: any;
  duration: number;
}

const VideoEditor: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<Project | null>(null);
  const [template, setTemplate] = useState<Template | null>(null);
  const [elements, setElements] = useState<VideoElement[]>([]);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(30);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showElementPanel, setShowElementPanel] = useState(false);

  const projectId = searchParams.get('project');
  const templateId = searchParams.get('template');

  useEffect(() => {
    loadEditor();
  }, [projectId, templateId]);

  const loadEditor = async () => {
    try {
      setIsLoading(true);
      
      if (projectId) {
        // Load existing project
        await loadProject(parseInt(projectId));
      } else if (templateId) {
        // Load template
        await loadTemplate(parseInt(templateId));
      } else {
        // Create new blank project
        createBlankProject();
      }
    } catch (error) {
      console.error('Error loading editor:', error);
      createBlankProject();
    } finally {
      setIsLoading(false);
    }
  };

  const loadProject = async (id: number) => {
    try {
      const response = await axios.get(`/api/v1/projects/${id}`);
      if (response.data.success) {
        const projectData = response.data.data;
        setProject(projectData);
        setElements(projectData.elements || []);
        setDuration(projectData.duration || 30);
      }
    } catch (error) {
      console.error('Error loading project:', error);
      createBlankProject();
    }
  };

  const loadTemplate = async (id: number) => {
    try {
      const response = await axios.get(`/api/v1/templates/${id}`);
      if (response.data.success) {
        const templateData = response.data.data;
        setTemplate(templateData);
        
        // Convert template elements to video elements
        const templateElements = convertTemplateElements(templateData.elements);
        setElements(templateElements);
        setDuration(templateData.duration || 30);
      }
    } catch (error) {
      console.error('Error loading template:', error);
      createBlankProject();
    }
  };

  const convertTemplateElements = (_templateElements: any): VideoElement[] => {
    // Convert template elements to video elements format
    // This is a simplified conversion - in a real app, this would be more complex
    return [
      {
        id: '1',
        type: 'text',
        content: 'Sample Title',
        position: { x: 50, y: 50 },
        size: { width: 300, height: 60 },
        style: {
          fontSize: 24,
          fontFamily: 'Arial',
          color: '#ffffff',
          backgroundColor: 'transparent'
        },
        timing: { start: 0, duration: 5 }
      },
      {
        id: '2',
        type: 'text',
        content: 'Sample Subtitle',
        position: { x: 50, y: 120 },
        size: { width: 250, height: 40 },
        style: {
          fontSize: 16,
          fontFamily: 'Arial',
          color: '#cccccc',
          backgroundColor: 'transparent'
        },
        timing: { start: 1, duration: 4 }
      }
    ];
  };

  const createBlankProject = () => {
    setProject({
      id: 0,
      name: 'New Project',
      description: 'A new video project',
      elements: [],
      duration: 30
    });
    setElements([]);
    setDuration(30);
  };

  const addTextElement = () => {
    const newElement: VideoElement = {
      id: Date.now().toString(),
      type: 'text',
      content: 'New Text',
      position: { x: 100, y: 100 },
      size: { width: 200, height: 50 },
      style: {
        fontSize: 18,
        fontFamily: 'Arial',
        color: '#ffffff',
        backgroundColor: 'transparent'
      },
      timing: { start: currentTime, duration: 5 }
    };
    
    setElements([...elements, newElement]);
    setSelectedElement(newElement.id);
    setShowElementPanel(true);
  };

  const updateElement = (id: string, updates: Partial<VideoElement>) => {
    setElements(elements.map(el => 
      el.id === id ? { ...el, ...updates } : el
    ));
  };

  const deleteElement = (id: string) => {
    setElements(elements.filter(el => el.id !== id));
    if (selectedElement === id) {
      setSelectedElement(null);
    }
  };

  const saveProject = async () => {
    try {
      const projectData = {
        name: project?.name || 'Untitled Project',
        description: project?.description || '',
        elements: elements,
        duration: duration
      };

      if (project?.id && project.id > 0) {
        // Update existing project
        await axios.put(`/api/v1/projects/${project.id}`, projectData);
        alert('Project saved successfully!');
      } else {
        // Create new project
        const response = await axios.post('/api/v1/projects', projectData);
        if (response.data.success) {
          alert('Project created successfully!');
          // Update URL to reflect the new project
          navigate(`/video-editor?project=${response.data.data.id}`);
        }
      }
    } catch (error) {
      console.error('Error saving project:', error);
      alert('Failed to save project. Please try again.');
    }
  };

  const exportVideo = async () => {
    try {
      const exportData = {
        elements: elements,
        duration: duration,
        resolution: '1920x1080',
        fps: 30
      };

      alert('Video export started! This may take a few minutes...');
      
      const response = await axios.post('/api/v1/videos/export', exportData);
      if (response.data.success) {
        alert('Video exported successfully!');
      }
    } catch (error) {
      console.error('Error exporting video:', error);
      alert('Failed to export video. Please try again.');
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const selectedElementData = selectedElement 
    ? elements.find(el => el.id === selectedElement)
    : null;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Loading Video Editor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/projects')}
              className="text-gray-400 hover:text-white"
            >
              ← Back to Projects
            </button>
            <h1 className="text-xl font-bold">
              {project?.name || template?.name || 'Video Editor'}
            </h1>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={saveProject}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm"
            >
              Save Project
            </button>
            <button
              onClick={exportVideo}
              className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm"
            >
              Export Video
            </button>
          </div>
        </div>
      </div>

      <div className="flex h-screen">
        {/* Left Sidebar - Tools */}
        <div className="w-64 bg-gray-800 border-r border-gray-700 p-4">
          <h3 className="text-lg font-semibold mb-4">Tools</h3>
          
          <div className="space-y-2">
            <button
              onClick={addTextElement}
              className="w-full bg-gray-700 hover:bg-gray-600 p-3 rounded text-left"
            >
              📝 Add Text
            </button>
            <button
              onClick={() => setShowElementPanel(true)}
              className="w-full bg-gray-700 hover:bg-gray-600 p-3 rounded text-left"
            >
              🖼️ Add Image
            </button>
            <button
              onClick={() => setShowElementPanel(true)}
              className="w-full bg-gray-700 hover:bg-gray-600 p-3 rounded text-left"
            >
              🎵 Add Audio
            </button>
            <button
              onClick={() => setShowElementPanel(true)}
              className="w-full bg-gray-700 hover:bg-gray-600 p-3 rounded text-left"
            >
              🎬 Add Video
            </button>
          </div>

          <div className="mt-8">
            <h4 className="text-md font-semibold mb-3">Elements</h4>
            <div className="space-y-1">
              {elements.map((element) => (
                <div
                  key={element.id}
                  onClick={() => setSelectedElement(element.id)}
                  className={`p-2 rounded cursor-pointer text-sm ${
                    selectedElement === element.id
                      ? 'bg-blue-600'
                      : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                >
                  {element.type === 'text' ? '📝' : '🖼️'} {element.content.substring(0, 20)}
                  {element.content.length > 20 && '...'}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Canvas Area */}
        <div className="flex-1 flex flex-col">
          {/* Canvas */}
          <div className="flex-1 bg-black relative overflow-hidden">
            <div className="absolute inset-4 bg-gray-900 rounded border-2 border-gray-600">
              {/* Video Preview Area */}
              <div className="w-full h-full relative">
                {elements.map((element) => {
                  // Only show elements that are active at current time
                  const isActive = currentTime >= element.timing.start && 
                                 currentTime < element.timing.start + element.timing.duration;
                  
                  if (!isActive) return null;
                  
                  return (
                    <div
                      key={element.id}
                      onClick={() => setSelectedElement(element.id)}
                      className={`absolute cursor-pointer ${
                        selectedElement === element.id ? 'ring-2 ring-blue-500' : ''
                      }`}
                      style={{
                        left: element.position.x,
                        top: element.position.y,
                        width: element.size.width,
                        height: element.size.height,
                        fontSize: element.style.fontSize,
                        fontFamily: element.style.fontFamily,
                        color: element.style.color,
                        backgroundColor: element.style.backgroundColor,
                        opacity: element.style.opacity || 1
                      }}
                    >
                      {element.type === 'text' && (
                        <div className="w-full h-full flex items-center">
                          {element.content}
                        </div>
                      )}
                      {element.type === 'image' && (
                        <div className="w-full h-full bg-gray-600 flex items-center justify-center text-xs">
                          Image Placeholder
                        </div>
                      )}
                    </div>
                  );
                })}
                
                {elements.length === 0 && (
                  <div className="w-full h-full flex items-center justify-center text-gray-500">
                    <div className="text-center">
                      <div className="text-4xl mb-4">🎬</div>
                      <p>Your video canvas</p>
                      <p className="text-sm">Add elements to get started</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="h-32 bg-gray-800 border-t border-gray-700 p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
                >
                  {isPlaying ? '⏸️' : '▶️'}
                </button>
                <span className="text-sm">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <label className="text-sm">Duration:</label>
                <input
                  type="number"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value) || 30)}
                  className="w-16 px-2 py-1 bg-gray-700 rounded text-sm"
                  min="1"
                  max="300"
                />
                <span className="text-sm">seconds</span>
              </div>
            </div>
            
            {/* Timeline Scrubber */}
            <div className="relative">
              <input
                type="range"
                min="0"
                max={duration}
                value={currentTime}
                onChange={(e) => setCurrentTime(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
              
              {/* Element Timeline Bars */}
              <div className="absolute top-6 left-0 right-0 h-4">
                {elements.map((element, index) => (
                  <div
                    key={element.id}
                    className="absolute h-3 bg-blue-500 rounded opacity-75"
                    style={{
                      left: `${(element.timing.start / duration) * 100}%`,
                      width: `${(element.timing.duration / duration) * 100}%`,
                      top: `${index * 16}px`
                    }}
                    title={`${element.content} (${element.timing.start}s - ${element.timing.start + element.timing.duration}s)`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar - Properties */}
        {showElementPanel && selectedElementData && (
          <div className="w-80 bg-gray-800 border-l border-gray-700 p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Element Properties</h3>
              <button
                onClick={() => setShowElementPanel(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Content</label>
                <input
                  type="text"
                  value={selectedElementData.content}
                  onChange={(e) => updateElement(selectedElementData.id, { content: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 rounded"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium mb-1">X Position</label>
                  <input
                    type="number"
                    value={selectedElementData.position.x}
                    onChange={(e) => updateElement(selectedElementData.id, {
                      position: { ...selectedElementData.position, x: parseInt(e.target.value) || 0 }
                    })}
                    className="w-full px-2 py-1 bg-gray-700 rounded text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Y Position</label>
                  <input
                    type="number"
                    value={selectedElementData.position.y}
                    onChange={(e) => updateElement(selectedElementData.id, {
                      position: { ...selectedElementData.position, y: parseInt(e.target.value) || 0 }
                    })}
                    className="w-full px-2 py-1 bg-gray-700 rounded text-sm"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium mb-1">Width</label>
                  <input
                    type="number"
                    value={selectedElementData.size.width}
                    onChange={(e) => updateElement(selectedElementData.id, {
                      size: { ...selectedElementData.size, width: parseInt(e.target.value) || 100 }
                    })}
                    className="w-full px-2 py-1 bg-gray-700 rounded text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Height</label>
                  <input
                    type="number"
                    value={selectedElementData.size.height}
                    onChange={(e) => updateElement(selectedElementData.id, {
                      size: { ...selectedElementData.size, height: parseInt(e.target.value) || 50 }
                    })}
                    className="w-full px-2 py-1 bg-gray-700 rounded text-sm"
                  />
                </div>
              </div>
              
              {selectedElementData.type === 'text' && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">Font Size</label>
                    <input
                      type="number"
                      value={selectedElementData.style.fontSize || 16}
                      onChange={(e) => updateElement(selectedElementData.id, {
                        style: { ...selectedElementData.style, fontSize: parseInt(e.target.value) || 16 }
                      })}
                      className="w-full px-2 py-1 bg-gray-700 rounded text-sm"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Color</label>
                    <input
                      type="color"
                      value={selectedElementData.style.color || '#ffffff'}
                      onChange={(e) => updateElement(selectedElementData.id, {
                        style: { ...selectedElementData.style, color: e.target.value }
                      })}
                      className="w-full h-10 bg-gray-700 rounded"
                    />
                  </div>
                </>
              )}
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium mb-1">Start Time</label>
                  <input
                    type="number"
                    value={selectedElementData.timing.start}
                    onChange={(e) => updateElement(selectedElementData.id, {
                      timing: { ...selectedElementData.timing, start: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full px-2 py-1 bg-gray-700 rounded text-sm"
                    step="0.1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Duration</label>
                  <input
                    type="number"
                    value={selectedElementData.timing.duration}
                    onChange={(e) => updateElement(selectedElementData.id, {
                      timing: { ...selectedElementData.timing, duration: parseFloat(e.target.value) || 1 }
                    })}
                    className="w-full px-2 py-1 bg-gray-700 rounded text-sm"
                    step="0.1"
                  />
                </div>
              </div>
              
              <button
                onClick={() => deleteElement(selectedElementData.id)}
                className="w-full bg-red-600 hover:bg-red-700 py-2 rounded"
              >
                Delete Element
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoEditor;
