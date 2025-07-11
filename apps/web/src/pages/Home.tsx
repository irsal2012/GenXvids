import React from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Play, Sparkles, Video, Zap } from 'lucide-react'

const Home: React.FC = () => {
  return (
    <div className="min-h-screen text-white">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center py-20"
      >
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent"
        >
          GenXvids
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-xl mb-8 text-gray-300 max-w-2xl mx-auto"
        >
          Create stunning videos with AI-powered tools. From text-to-video generation to professional templates, 
          bring your ideas to life effortlessly.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex gap-4 justify-center flex-wrap"
        >
          <Link
            to="/register"
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 px-8 py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105"
          >
            Get Started Free
          </Link>
          <Link
            to="/templates"
            className="border border-gray-600 hover:border-gray-400 px-8 py-3 rounded-lg font-semibold transition-all duration-300 hover:bg-gray-800"
          >
            Browse Templates
          </Link>
        </motion.div>
      </motion.section>

      {/* Features Section */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.8 }}
        className="py-20"
      >
        <h2 className="text-4xl font-bold text-center mb-16">Powerful Features</h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-xl border border-gray-700"
          >
            <Sparkles className="w-12 h-12 text-blue-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">AI-Powered Generation</h3>
            <p className="text-gray-400">Transform text descriptions into engaging videos with advanced AI technology.</p>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-xl border border-gray-700"
          >
            <Video className="w-12 h-12 text-purple-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Professional Templates</h3>
            <p className="text-gray-400">Choose from hundreds of professionally designed templates for any occasion.</p>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-xl border border-gray-700"
          >
            <Play className="w-12 h-12 text-green-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Easy Editor</h3>
            <p className="text-gray-400">Intuitive drag-and-drop editor with real-time preview and collaboration.</p>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-xl border border-gray-700"
          >
            <Zap className="w-12 h-12 text-yellow-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
            <p className="text-gray-400">Generate and export videos in minutes, not hours. Optimized for speed.</p>
          </motion.div>
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 1.0 }}
        className="text-center py-20"
      >
        <h2 className="text-4xl font-bold mb-6">Ready to Create Amazing Videos?</h2>
        <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          Join thousands of creators who are already using GenXvids to bring their stories to life.
        </p>
        <Link
          to="/register"
          className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 px-12 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 inline-block"
        >
          Start Creating Now
        </Link>
      </motion.section>
    </div>
  )
}

export default Home
