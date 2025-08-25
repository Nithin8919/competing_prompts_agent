#!/usr/bin/env python3
"""
Setup script for CTA Focus Analyzer - Virtual Environment Isolated
"""

import subprocess
import sys
import os
import venv

def run_command(command, cwd=None, use_shell=True):
    """Run a command and handle errors"""
    try:
        if use_shell:
            result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        else:
            # For commands with spaces in paths, use list format
            result = subprocess.run(command, check=True, cwd=cwd, capture_output=True, text=True)
        print(f"✅ {command if isinstance(command, str) else ' '.join(command)}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {command if isinstance(command, str) else ' '.join(command)}")
        print(f"Error: {e.stderr}")
        return None

def create_isolated_venv():
    """Create a completely isolated virtual environment"""
    print("\n🔒 Creating isolated Python virtual environment...")
    
    venv_path = os.path.join(os.getcwd(), '.venv')
    
    if os.path.exists(venv_path):
        print("📦 Virtual environment already exists")
        return venv_path
    
    # Create virtual environment with system site packages disabled for complete isolation
    venv.create(venv_path, system_site_packages=False, clear=True, with_pip=True)
    print("✅ Created isolated virtual environment at .venv/")
    
    return venv_path

def setup_backend():
    """Setup backend dependencies in isolated environment"""
    print("\n🐍 Setting up Python backend in virtual environment...")
    
    # Create isolated virtual environment
    venv_path = create_isolated_venv()
    
    # Get the correct pip path for the virtual environment
    if sys.platform == "win32":
        pip_cmd = os.path.join(venv_path, 'Scripts', 'pip')
        python_cmd = os.path.join(venv_path, 'Scripts', 'python')
    else:
        pip_cmd = os.path.join(venv_path, 'bin', 'pip')
        python_cmd = os.path.join(venv_path, 'bin', 'python')
    
    # Verify we're using the virtual environment
    result = run_command([python_cmd, '-c', 'import sys; print(sys.prefix)'], use_shell=False)
    if result and '.venv' in result:
        print("✅ Confirmed using isolated virtual environment")
    else:
        print("⚠️  Warning: May not be using virtual environment")
    
    # Upgrade pip in virtual environment
    run_command([python_cmd, '-m', 'pip', 'install', '--upgrade', 'pip'], use_shell=False)
    
    # Install backend dependencies in virtual environment
    requirements_path = os.path.join('backend', 'requirements.txt')
    run_command([pip_cmd, 'install', '-r', requirements_path], use_shell=False)
    
    print("🔒 All Python packages installed in isolated environment (.venv/)")
    print("💡 System Python remains unchanged")

def setup_frontend():
    """Setup frontend dependencies"""
    print("\n⚛️  Setting up React frontend...")
    
    # Install frontend dependencies
    run_command('npm install', cwd='frontend')

def main():
    """Main setup function with isolation checks"""
    print("🚀 Setting up CTA Focus Analyzer with Virtual Environment Isolation...")
    print("🔒 This setup will NOT affect your system Python or global packages")
    
    # Check if we're in the right directory
    if not os.path.exists('backend') or not os.path.exists('frontend'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Verify we're not in a conda environment or other virtual env
    if 'CONDA_DEFAULT_ENV' in os.environ:
        print("⚠️  Detected conda environment. This setup will create an isolated venv.")
    
    if 'VIRTUAL_ENV' in os.environ:
        print("⚠️  Detected existing virtual environment. This setup will create a new isolated venv.")
    
    # Setup backend in isolated environment
    setup_backend()
    
    # Setup frontend (also isolated via npm)
    setup_frontend()
    
    print("\n✅ Setup complete with full isolation!")
    print("\n🔒 Virtual Environment Details:")
    print("   - Python packages: .venv/ (isolated)")
    print("   - Node packages: frontend/node_modules/ (isolated)")
    print("   - No system packages affected")
    
    print("\n📋 Safe execution steps:")
    print("1. Always activate venv first:")
    print("   source .venv/bin/activate  # On Mac/Linux")
    print("   .venv\\Scripts\\activate    # On Windows")
    print("2. Backend: cd backend && python main.py")
    print("3. Frontend: cd frontend && npm run dev")
    print("4. Open http://localhost:3000")
    print("\n💡 Use 'deactivate' to exit the virtual environment when done")

if __name__ == "__main__":
    main()
