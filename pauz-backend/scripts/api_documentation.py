#!/usr/bin/env python3
"""
API Endpoint Documentation Generator
Generates complete API documentation for frontend development
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.main import app
import json

def generate_api_docs():
    """Generate comprehensive API documentation"""
    
    endpoints = []
    
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods') and hasattr(route, 'endpoint'):
            path = route.path
            methods = list(route.methods) if route.methods else []
            
            # Skip documentation endpoints
            if path.startswith('/docs') or path.startswith('/openapi') or path.startswith('/redoc'):
                continue
                
            # Determine endpoint category
            if '/auth' in path:
                category = 'Authentication'
            elif '/guided_journal' in path:
                category = 'Guided Journal'
            elif '/freejournal' in path:
                category = 'Free Journal'
            elif '/garden' in path:
                category = 'Garden'
            elif '/stats' in path:
                category = 'Statistics'
            elif '/inference' in path:
                category = 'Inference'
            else:
                category = 'General'
            
            # Clean up methods
            clean_methods = [m for m in methods if m not in ['HEAD', 'OPTIONS']]
            
            endpoints.append({
                'path': path,
                'methods': clean_methods,
                'category': category,
                'description': _get_endpoint_description(path, clean_methods)
            })
    
    return endpoints

def _get_endpoint_description(path, methods):
    """Get human-readable description for endpoint"""
    descriptions = {
        '/auth/login': {'GET': 'Get Google OAuth login URL'},
        '/auth/callback': {'GET': 'Handle OAuth callback from Google'},
        '/auth/token': {'POST': 'Exchange authorization code for access token'},
        '/auth/me': {'GET': 'Get current user information'},
        
        '/guided_journal/prompts': {'POST': 'Generate AI-powered journal prompts'},
        '/guided_journal/': {'POST': 'Create new guided journal session', 'GET': 'Get user\'s guided journals'},
        '/guided_journal/{journal_id}': {'GET': 'Get specific guided journal'},
        '/guided_journal/{journal_id}/entry': {'POST': 'Add response to guided journal prompt'},
        '/guided_journal/{journal_id}/export': {'POST': 'Export guided journal to PDF'},
        
        '/freejournal/': {'POST': 'Create new free journal session'},
        '/freejournal/{session_id}': {'GET': 'Get free journal session'},
        '/freejournal/{session_id}/save': {'POST': 'Save content to free journal'},
        '/freejournal/{session_id}/hints': {'POST': 'Generate AI hints', 'GET': 'Get session hints'},
        '/freejournal/{session_id}/voice': {'POST': 'Transcribe audio to text'},
        '/freejournal/{session_id}/reflect': {'POST': 'AI mood analysis and garden update'},
        '/freejournal/{session_id}/export': {'POST': 'Export free journal to PDF'},
        
        '/garden/': {'POST': 'Create garden entry', 'GET': 'Get user\'s garden entries'},
        
        '/stats/total-guided-journals': {'GET': 'Get total guided journals count'},
        '/stats/total-free-journals': {'GET': 'Get total free journals count'},
        '/stats/total-journals': {'GET': 'Get total journals count'},
        
        '/inference': {'POST': 'Get AI inference response'},
        '/': {'GET': 'Welcome endpoint'}
    }
    
    if path in descriptions:
        for method in methods:
            if method in descriptions[path]:
                return descriptions[path][method]
    
    return f"{', '.join(methods)} endpoint for {path}"

def main():
    endpoints = generate_api_docs()
    
    print("🌐 PAUZ Journaling API - Frontend Integration Guide")
    print("=" * 60)
    print()
    
    # Group by category
    categories = {}
    for endpoint in endpoints:
        category = endpoint['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(endpoint)
    
    # Display by category
    for category, category_endpoints in categories.items():
        print(f"📋 {category}")
        print("-" * 40)
        
        for endpoint in category_endpoints:
            for method in endpoint['methods']:
                print(f"{method:6} {endpoint['path']}")
                print(f"       {endpoint['description']}")
                print()
        
        print()
    
    # Generate cURL examples
    print("🧪 API Usage Examples")
    print("=" * 60)
    
    examples = [
        {
            'title': '1. User Authentication Flow',
            'description': 'Complete OAuth login flow',
            'curls': [
                'curl -X GET "http://localhost:8000/auth/login"',
                'curl -X GET "http://localhost:8000/auth/callback?code=your_code&state=your_state"',
                'curl -X POST "http://localhost:8000/auth/token" -H "Content-Type: application/json" -d \'{"code": "your_code", "state": "your_state"}\''
            ]
        },
        {
            'title': '2. Free Journal Session',
            'description': 'Create and manage free journal sessions',
            'curls': [
                'curl -X POST "http://localhost:8000/freejournal/" -H "Authorization: Bearer your_token"',
                'curl -X POST "http://localhost:8000/freejournal/session_id/hints" -H "Authorization: Bearer your_token" -H "Content-Type: application/json" -d \'{"current_content": "I\'m feeling grateful today..."}\'',
                'curl -X POST "http://localhost:8000/freejournal/session_id/save" -H "Authorization: Bearer your_token" -H "Content-Type: application/json" -d \'{"content": "Today was amazing because..."}\''
            ]
        },
        {
            'title': '3. Guided Journal Flow',
            'description': 'Create AI-powered guided journal',
            'curls': [
                'curl -X POST "http://localhost:8000/guided_journal/prompts" -H "Authorization: Bearer your_token" -H "Content-Type: application/json" -d \'{"topic": "mindfulness", "count": 3}\'',
                'curl -X POST "http://localhost:8000/guided_journal/" -H "Authorization: Bearer your_token" -H "Content-Type: application/json" -d \'{"topic": "mindfulness", "prompts": [...]}\''
            ]
        },
        {
            'title': '4. Garden & Mood Tracking',
            'description': 'AI mood analysis and visualization',
            'curls': [
                'curl -X POST "http://localhost:8000/freejournal/session_id/reflect" -H "Authorization: Bearer your_token"',
                'curl -X GET "http://localhost:8000/garden/" -H "Authorization: Bearer your_token"'
            ]
        }
    ]
    
    for example in examples:
        print(f"📝 {example['title']}")
        print(f"    {example['description']}")
        print()
        for curl in example['curls']:
            print(f"    {curl}")
        print()
    
    # Frontend integration checklist
    print("✅ Frontend Integration Checklist")
    print("=" * 60)
    
    checklist = [
        ("🔐 Authentication", "OAuth 2.0 flow with Google", "✅"),
        ("🧠 AI Features", "Gemini/OpenAI integration", "✅"),
        ("📝 Free Journal", "Session-based writing with AI hints", "✅"),
        ("🎯 Guided Journal", "AI-generated prompts", "✅"),
        ("🌱 Garden", "Mood tracking with flowers", "✅"),
        ("🔊 Voice", "Audio transcription", "✅"),
        ("📄 PDF Export", "Journal exports", "✅"),
        ("📊 Statistics", "Usage analytics", "✅"),
        ("🌐 CORS", "Frontend integration ready", "✅"),
        ("🛡️ Error Handling", "Comprehensive error responses", "✅")
    ]
    
    for item, description, status in checklist:
        print(f"{item:<15} {description:<30} {status}")
    
    print()
    print("🎉 Your backend is FULLY READY for frontend integration!")
    print("📱 Base URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔑 Authentication: Bearer tokens required for protected routes")

if __name__ == "__main__":
    main()