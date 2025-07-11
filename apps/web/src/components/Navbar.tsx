import React from 'react'
import { Link } from 'react-router-dom'
import { Video } from 'lucide-react'

const Navbar: React.FC = () => {
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
            <Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link to="/projects" className="text-gray-300 hover:text-white transition-colors">
              Projects
            </Link>
          </div>

          <div className="flex items-center space-x-4">
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
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
