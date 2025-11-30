#!/usr/bin/env python3
"""
Fix npm issues and deploy Raindrop app
"""
import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"  STDOUT: {result.stdout}")
            print(f"  STDERR: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("🚀 Fixing npm issues and deploying PAUZ app...")
    
    # Step 1: Clean npm cache
    if not run_command("npm cache clean --force", "Cleaning npm cache"):
        print("⚠️ Cache clean failed, continuing...")
    
    # Step 2: Delete node_modules and package-lock.json
    if not run_command("rm -rf node_modules package-lock.json", "Removing node_modules and lock file"):
        print("⚠️ Removal failed, continuing...")
    
    # Step 3: Install fresh dependencies
    if not run_command("npm install", "Installing dependencies"):
        print("❌ npm install failed")
        return False
    
    # Step 4: Try to deploy the app
    if not run_command("raindrop build deploy --start", "Deploying Raindrop app"):
        print("❌ Deployment failed")
        return False
    
    print("✅ App deployment completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)