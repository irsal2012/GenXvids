import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Video } from 'lucide-react'

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  avatar_url?: string;
}

const Navbar: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check authentication status
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing user data:', error);
        // Clear invalid data
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleLogout = () => {
    // Clear stored data
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    // Update state
    setUser(null);
    setIsAuthenticated(false);
    
    // Redirect to home page
    navigate('/');
  };

  return (
    <nav className="bg-gray-900/80 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <Video className="w-8 h-8 text-blue-500" />
            <span className="text-xl font-bold text-white">GenXvids</span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/templates" className="text-gray-300 hover:text-white transition-colors">
              Templates
            </Link>
            {isAuthenticated && (
              <>
                <Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors">
                  Dashboard
                </Link>
                <Link to="/projects" className="text-gray-300 hover:text-white transition-colors">
                  Projects
                </Link>
                <Link to="/video-editor" className="text-gray-300 hover:text-white transition-colors">
                  Video Editor
                </Link>
              </>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <span className="text-gray-300">
                  Welcome, {user?.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
