import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { 
  PerspectiveCamera, 
  Float, 
  Environment,
  MeshDistortMaterial,
  Sphere,
  useScroll,
  Html
} from '@react-three/drei'
import { motion } from 'framer-motion'
import { Film, Sparkles, Zap, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

console.log('Landing.jsx loaded')

function AnimatedSphere({ position, color, speed = 1 }) {
  const meshRef = useRef()
  
  useFrame((state) => {
    meshRef.current.rotation.x = state.clock.getElapsedTime() * speed * 0.2
    meshRef.current.rotation.y = state.clock.getElapsedTime() * speed * 0.3
  })

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <Sphere ref={meshRef} args={[1, 64, 64]} position={position}>
        <MeshDistortMaterial
          color={color}
          attach="material"
          distort={0.4}
          speed={2}
          roughness={0.2}
          metalness={0.8}
        />
      </Sphere>
    </Float>
  )
}

function Scene() {
  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 0, 10]} />
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -5]} intensity={0.5} color="#8b5cf6" />
      
      <AnimatedSphere position={[-3, 2, 0]} color="#0ea5e9" speed={1} />
      <AnimatedSphere position={[3, -1, -2]} color="#8b5cf6" speed={0.8} />
      <AnimatedSphere position={[0, -2, -3]} color="#ec4899" speed={1.2} />
      
      <Environment preset="night" />
    </>
  )
}

export default function LandingPage() {
  console.log('LandingPage rendering')
  
  return (
    <div className="relative min-h-screen bg-dark-50 overflow-hidden">
      {/* 3D Background */}
      <div className="fixed inset-0 z-0">
        <Canvas 
          fallback={<div className="w-full h-full bg-gradient-to-br from-primary-500/10 via-accent-purple/10 to-accent-pink/10" />}
          onCreated={() => console.log('Canvas created successfully')}
        >
          <Scene />
        </Canvas>
      </div>

      {/* Gradient Overlay */}
      <div className="fixed inset-0 z-10 bg-gradient-to-b from-dark-50/50 via-dark-50/80 to-dark-50 pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-20 glass border-b border-dark-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Film className="w-8 h-8 text-primary-500" />
              <span className="text-xl font-display font-bold gradient-text">CineForge AI</span>
            </div>
            
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-dark-700 hover:text-dark-900 transition-colors">Features</a>
              <a href="#how-it-works" className="text-dark-700 hover:text-dark-900 transition-colors">How It Works</a>
              <a href="#pricing" className="text-dark-700 hover:text-dark-900 transition-colors">Pricing</a>
            </div>

            <div className="flex items-center gap-4">
              <Link to="/login" className="btn-ghost">Sign In</Link>
              <Link to="/register" className="btn-primary">Get Started</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-20 section-container">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-display font-bold mb-6 leading-tight">
              Transform Scripts into{' '}
              <span className="gradient-text">Visual Stories</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-dark-600 mb-8 text-balance">
              AI-powered pre-production platform that converts screenplays into stunning 
              storyboards, saving time and bringing your vision to life.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link to="/register" className="btn-primary flex items-center gap-2 text-lg">
                Start Creating Free
                <ArrowRight className="w-5 h-5" />
              </Link>
              <button className="btn-secondary text-lg">
                Watch Demo
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="text-center"
              >
                <div className="text-3xl font-bold gradient-text">10x</div>
                <div className="text-sm text-dark-600 mt-1">Faster Production</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.3 }}
                className="text-center"
              >
                <div className="text-3xl font-bold gradient-text">5000+</div>
                <div className="text-sm text-dark-600 mt-1">Filmmakers</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="text-center"
              >
                <div className="text-3xl font-bold gradient-text">50K+</div>
                <div className="text-sm text-dark-600 mt-1">Storyboards</div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-20 section-container">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-4">
            Powerful Features for{' '}
            <span className="gradient-text">Storytellers</span>
          </h2>
          <p className="text-xl text-dark-600">Everything you need for seamless pre-production</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Sparkles className="w-8 h-8" />}
            title="AI-Powered Analysis"
            description="Automatically extract scenes, characters, and locations from your script with advanced NLP."
            delay={0.1}
          />
          <FeatureCard
            icon={<Film className="w-8 h-8" />}
            title="Visual Storyboards"
            description="Generate stunning storyboard panels with AI-assisted image generation and mood boards."
            delay={0.2}
          />
          <FeatureCard
            icon={<Zap className="w-8 h-8" />}
            title="Real-time Collaboration"
            description="Work together with your team in C-Space with live chat, comments, and version control."
            delay={0.3}
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-20 section-container">
        <div className="card max-w-4xl mx-auto text-center p-12 bg-gradient-to-br from-primary-600 to-accent-purple">
          <h2 className="text-4xl font-display font-bold text-white mb-4">
            Ready to Transform Your Workflow?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Join thousands of filmmakers creating better stories faster.
          </p>
          <Link to="/register" className="bg-white text-primary-600 px-8 py-4 rounded-lg font-bold text-lg hover:shadow-2xl transition-all duration-300 inline-block">
            Get Started for Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-20 border-t border-dark-200 mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <Film className="w-6 h-6 text-primary-500" />
              <span className="text-lg font-display font-bold gradient-text">CineForge AI</span>
            </div>
            <div className="text-sm text-dark-600">
              © 2024 CineForge AI. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      viewport={{ once: true }}
      className="card group hover:border-primary-500"
    >
      <div className="text-primary-500 mb-4 group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2 text-dark-900">{title}</h3>
      <p className="text-dark-600">{description}</p>
    </motion.div>
  )
}
