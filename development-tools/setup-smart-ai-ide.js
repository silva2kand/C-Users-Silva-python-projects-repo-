#!/usr/bin/env node

/**
 * Smart AI IDE Integration Setup
 * Combines: Better Auth Next.js + Smart AI IDE Backend + SuperAgent Firewall + Halo Gaming Elements
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Setting up Smart AI IDE Integration...\n');

const SETUP_STEPS = [
  {
    name: 'Create Unified Project Structure',
    action: () => createProjectStructure()
  },
  {
    name: 'Configure Authentication Bridge',
    action: () => configureAuthBridge()
  },
  {
    name: 'Setup SuperAgent Security Layer',
    action: () => setupSuperAgentSecurity()
  },
  {
    name: 'Add Halo Gaming Elements',
    action: () => addHaloGamingElements()
  },
  {
    name: 'Configure Environment Variables',
    action: () => configureEnvironment()
  },
  {
    name: 'Setup Database Connections',
    action: () => setupDatabases()
  },
  {
    name: 'Create Startup Scripts',
    action: () => createStartupScripts()
  }
];

async function main() {
  try {
    for (let i = 0; i < SETUP_STEPS.length; i++) {
      const step = SETUP_STEPS[i];
      console.log(`\n${i + 1}/${SETUP_STEPS.length} ${step.name}...`);
      await step.action();
      console.log(`✅ ${step.name} completed`);
    }
    
    console.log('\n🎉 Smart AI IDE Integration Setup Complete!');
    showNextSteps();
    
  } catch (error) {
    console.error('\n❌ Setup failed:', error.message);
    process.exit(1);
  }
}

function createProjectStructure() {
  const baseDir = '/c/Users/Silva/Desktop/smart-ai-ide-integrated';
  
  const structure = [
    'frontend',           // Better Auth Next.js
    'backend',            // Smart AI IDE Backend  
    'security',           // SuperAgent Firewall
    'shared',             // Shared utilities
    'docs',               // Documentation
    'scripts',            // Setup/deployment scripts
    'config',             // Configuration files
    'database',           // Database schemas/migrations
  ];
  
  if (!fs.existsSync(baseDir)) {
    fs.mkdirSync(baseDir, { recursive: true });
  }
  
  structure.forEach(dir => {
    const dirPath = path.join(baseDir, dir);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  });
  
  console.log(`📁 Created project structure at: ${baseDir}`);
}

function configureAuthBridge() {
  const authBridgeConfig = {
    frontend: {
      port: 3000,
      auth: 'better-auth',
      database: 'postgresql'
    },
    backend: {
      port: 3001, 
      auth: 'jwt-bridge',
      database: 'mongodb'
    },
    security: {
      port: 8080,
      firewall: 'superagent'
    }
  };
  
  const configPath = '/c/Users/Silva/Desktop/smart-ai-ide-integrated/config/integration.json';
  fs.writeFileSync(configPath, JSON.stringify(authBridgeConfig, null, 2));
  
  console.log('🔐 Authentication bridge configured');
}

function setupSuperAgentSecurity() {
  const securityConfig = `
models:
  - model_name: "gpt-4o"
    provider: "openai"
    api_base: "https://api.openai.com"
    
  - model_name: "claude-3-7-sonnet-20250219"
    provider: "anthropic"
    api_base: "https://api.anthropic.com/v1"

# Smart AI IDE Backend protection
proxy_rules:
  - path: "/api/super-agent/*"
    protection_level: "high"
    allow_code_generation: true
    
  - path: "/api/health"
    protection_level: "low"
    
telemetry_webhook:
  url: "http://localhost:3001/api/security-logs"
  headers:
    x-source: "superagent-firewall"
`;
  
  const configPath = '/c/Users/Silva/Desktop/smart-ai-ide-integrated/security/superagent.yaml';
  fs.writeFileSync(configPath, securityConfig);
  
  console.log('🛡️ SuperAgent security layer configured');
}

function addHaloGamingElements() {
  const haloThemeConfig = {
    theme: {
      name: "halo-spartan",
      colors: {
        primary: "#00ff41",      // Matrix green (Halo tech feel)
        secondary: "#0080ff",    // Electric blue  
        accent: "#ff6b35",       // Energy orange
        background: "#0a0a0a",   // Deep black
        surface: "#1a1a1a",     // Dark surface
        text: "#ffffff"          // White text
      },
      fonts: {
        mono: "JetBrains Mono",
        ui: "Inter"
      },
      animations: {
        bootSequence: true,
        holographicEffects: true,
        particleSystem: true
      }
    },
    gamification: {
      achievements: true,
      codeRanks: ["Recruit", "Private", "Corporal", "Sergeant", "Lieutenant", "Captain", "Major", "Colonel", "Spartan"],
      progressBars: true,
      soundEffects: false  // Optional Halo sounds
    }
  };
  
  const themePath = '/c/Users/Silva/Desktop/smart-ai-ide-integrated/frontend/theme/halo-theme.json';
  const dir = path.dirname(themePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(themePath, JSON.stringify(haloThemeConfig, null, 2));
  
  console.log('🎮 Halo gaming elements configured');
}

function configureEnvironment() {
  const envConfig = `# Smart AI IDE Integrated Environment Configuration
# Frontend (Next.js)
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_SECURITY_URL=http://localhost:8080
NEXT_PUBLIC_THEME=halo-spartan

# Backend (Smart AI IDE)
PORT=3001
NODE_ENV=development
JWT_SECRET=your-jwt-secret-here
MONGODB_URI=mongodb://localhost:27017/smart-ai-ide

# Security (SuperAgent)
SECURITY_PORT=8080
REDACTION_API_URL=http://localhost:3001/api/redaction

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/smart_ai_ide
POSTGRES_DB=smart_ai_ide
POSTGRES_USER=username
POSTGRES_PASSWORD=password

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Gaming Features  
ENABLE_HALO_THEME=true
ENABLE_GAMIFICATION=true
`;
  
  const envPath = '/c/Users/Silva/Desktop/smart-ai-ide-integrated/.env';
  fs.writeFileSync(envPath, envConfig);
  
  console.log('⚙️ Environment variables configured');
}

function setupDatabases() {
  const dbSetupSQL = `
-- Smart AI IDE Database Schema
CREATE DATABASE IF NOT EXISTS smart_ai_ide;

-- User management (works with better-auth)
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  path VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Agent Analysis Results
CREATE TABLE IF NOT EXISTS agent_analyses (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  analysis_type VARCHAR(100),
  results JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gaming/Gamification Data
CREATE TABLE IF NOT EXISTS user_achievements (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  achievement_type VARCHAR(100),
  achievement_data JSONB,
  unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
`;
  
  const schemaPath = '/c/Users/Silva/Desktop/smart-ai-ide-integrated/database/schema.sql';
  fs.writeFileSync(schemaPath, dbSetupSQL);
  
  console.log('🗄️ Database schemas created');
}

function createStartupScripts() {
  const startupScript = `#!/bin/bash

echo "🚀 Starting Smart AI IDE Integrated System..."

# Start databases (if not running)
echo "📊 Checking databases..."

# Start PostgreSQL (adjust for your system)
# systemctl start postgresql  # Linux
# brew services start postgresql  # macOS
# net start postgresql-x64-14  # Windows

# Start MongoDB (adjust for your system)  
# systemctl start mongod  # Linux
# brew services start mongodb-community  # macOS
# net start MongoDB  # Windows

# Start security layer first
echo "🛡️ Starting SuperAgent Security Layer (Port 8080)..."
cd security && npm start &
SECURITY_PID=$!

# Wait for security layer
sleep 3

# Start backend API
echo "🔧 Starting Smart AI IDE Backend (Port 3001)..."  
cd ../backend && npm run dev &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Start frontend
echo "🎨 Starting Frontend (Port 3000)..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo "✅ All services started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:3001"  
echo "🛡️ Security Layer: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle shutdown
trap 'echo "Stopping services..."; kill $SECURITY_PID $BACKEND_PID $FRONTEND_PID; exit' INT

# Wait for all processes
wait
`;

  const scriptPath = '/c/Users/Silva/Desktop/smart-ai-ide-integrated/scripts/start-all.sh';
  fs.writeFileSync(scriptPath, startupScript);
  
  // Make executable on Unix systems
  try {
    fs.chmodSync(scriptPath, '755');
  } catch (e) {
    // Windows doesn't support chmod, that's fine
  }
  
  console.log('📜 Startup scripts created');
}

function showNextSteps() {
  console.log('\n📋 Next Steps:');
  console.log('================');
  console.log('1. 📁 Navigate to: /c/Users/Silva/Desktop/smart-ai-ide-integrated');
  console.log('2. 📦 Copy your existing code into the new structure:');
  console.log('   • Copy better-auth-nextjs-starter/* → frontend/');  
  console.log('   • Copy smart-ai-ide/backend/* → backend/');
  console.log('   • Copy superagent/* → security/');
  console.log('3. 🔧 Install dependencies in each folder');
  console.log('4. 🗄️ Set up your databases (PostgreSQL + MongoDB)');
  console.log('5. ⚙️ Configure your .env file with real API keys');
  console.log('6. 🚀 Run: ./scripts/start-all.sh');
  console.log('\n🎮 Halo-themed Smart AI IDE with enterprise security!');
}

// Run the setup
main().catch(console.error);