import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import VideoEditor from './pages/VideoEditor'
import Templates from './pages/Templates'
import Projects from './pages/Projects'
import Login from './pages/Login'
import Register from './pages/Register'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <Navbar />
      <motion.main
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="container mx-auto px-4 py-8"
      >
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/editor" element={<VideoEditor />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/projects" element={<Projects />} />
        </Routes>
      </motion.main>
    </div>
  )
}

export default App
