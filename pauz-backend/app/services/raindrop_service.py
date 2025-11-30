"""
Raindrop Service for Application Cataloguing and Integration
"""
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from raindrop import Raindrop

load_dotenv()

class RaindropService:
    """Service for managing Raindrop application integration and cataloguing"""
    
    def __init__(self):
        self.api_key = os.getenv('AI_API_KEY')
        self.application_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
        self.organization_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
        self.client = None
        
        if self.api_key:
            try:
                self.client = Raindrop(api_key=self.api_key)
                print(f"✅ Raindrop client initialized for application: {self.application_name}")
            except Exception as e:
                print(f"❌ Failed to initialize Raindrop client: {e}")
        else:
            print("⚠️ AI_API_KEY not found - Raindrop features will be limited")
    
    def register_application(self) -> Dict[str, Any]:
        """
        Register the application with Raindrop by testing connection and preparing resources
        """
        if not self.client:
            return {"error": "Raindrop client not available"}
        
        try:
            # Load application configuration
            app_config_path = "raindrop-app.json"
            if not os.path.exists(app_config_path):
                return {"error": "raindrop-app.json configuration file not found"}
            
            with open(app_config_path, 'r') as f:
                app_config = json.load(f)
            
            print(f"📝 Setting up application: {self.application_name}")
            
            # Test connection first
            test_result = self.test_connection()
            if not test_result.get("success"):
                return {"error": f"Connection test failed: {test_result.get('error')}"}
            
            # Initialize buckets (they will be created on first use)
            bucket_result = self.initialize_application_buckets()
            
            # Store application metadata in a bucket for catalogue purposes
            registration_data = {
                "application_name": self.application_name,
                "metadata": {
                    "name": app_config["name"],
                    "description": app_config["description"],
                    "version": app_config["version"],
                    "category": app_config["category"],
                    "tags": app_config["tags"],
                    "author": app_config["author"],
                    "api_routes": app_config["api_routes"],
                    "smart_buckets": app_config["smart_buckets"],
                    "auth": app_config["auth"],
                    "external_integrations": app_config["external_integrations"],
                    "registered_at": str(os.path.getctime(__file__))
                }
            }
            
            # Store in the journal-prompts bucket as a registration record
            try:
                self.client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "journal-prompts",
                            "application_name": self.application_name
                        }
                    },
                    key="app-registration-info",
                    content=json.dumps(registration_data, indent=2),
                    content_type="application/json"
                )
                print(f"✅ Application metadata stored for: {self.application_name}")
            except Exception as e:
                print(f"⚠️ Could not store metadata in journal-prompts bucket: {e}")
                # Try without application_name (global scope)
                try:
                    self.client.bucket.put(
                        bucket_location={
                            "bucket": {
                                "name": "journal-prompts"
                            }
                        },
                        key="app-registration-info",
                        content=json.dumps(registration_data, indent=2),
                        content_type="application/json"
                    )
                    print(f"✅ Application metadata stored for: {self.application_name}")
                except Exception as e2:
                    print(f"⚠️ Could not store metadata: {e2}")
            
            return {
                "success": True,
                "application_name": self.application_name,
                "message": "Application set up successfully",
                "buckets": bucket_result,
                "catalogue_ready": True
            }
            
        except Exception as e:
            print(f"❌ Failed to set up application: {e}")
            return {"error": str(e)}
    
    def initialize_application_buckets(self) -> Dict[str, Any]:
        """
        Initialize all required SmartBuckets for the application
        """
        if not self.client:
            return {"error": "Raindrop client not available"}
        
        buckets_config = [
            {"name": "journal-prompts", "description": "AI-generated journal prompts and hints"},
            {"name": "journal-analysis", "description": "AI analysis of journal entries for mood and insights"},
            {"name": "FreeJournals", "description": "User's free-form journal entries"},
            {"name": "Hints", "description": "Writing hints and suggestions"},
            {"name": "Garden", "description": "Mood tracking and personal insights"}
        ]
        
        results = {}
        
        for bucket in buckets_config:
            # Try to check if bucket exists by listing it (without application_name for now)
            try:
                existing_buckets = self.client.bucket.list(
                    bucket_location={
                        "bucket": {
                            "name": bucket["name"]
                        }
                    }
                )
                print(f"✅ Bucket '{bucket['name']}' already exists")
                results[bucket["name"]] = {"success": True, "status": "exists"}
            except Exception as e:
                print(f"ℹ️ Bucket '{bucket['name']}' will be created on first use")
                results[bucket["name"]] = {"success": True, "status": "will_create_on_use"}
        
        return {
            "application_name": self.application_name,
            "buckets_status": results,
            "note": "Buckets will be automatically created when first used"
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Raindrop connection and basic functionality
        """
        if not self.client:
            return {"error": "Raindrop client not available"}
        
        try:
            # Try to list buckets from the manifest to test connection
            bucket_name = "journal-prompts"
            response = self.client.bucket.list(
                bucket_location={
                    "bucket": {
                        "name": bucket_name,
                        "application_name": self.organization_name
                    }
                }
            )
            
            return {
                "success": True,
                "application_name": self.application_name,
                "organization_name": self.organization_name,
                "message": "Connection successful",
                "bucket_response": str(response)[:100]
            }
            
        except Exception as e:
            # If bucket doesn't exist, that's still a successful connection
            if "not found" in str(e) and ("SmartBucket" in str(e) or "bucket" in str(e)):
                return {
                    "success": True,
                    "application_name": self.application_name,
                    "organization_name": self.organization_name,
                    "message": "Connection successful (buckets will be created on first use)",
                    "note": "Buckets need to be created via manifest or will be auto-created"
                }
            
            return {
                "success": False,
                "application_name": self.application_name,
                "organization_name": self.organization_name,
                "error": str(e)
            }
    
    def get_application_status(self) -> Dict[str, Any]:
        """
        Get the current status of the application in Raindrop
        """
        if not self.client:
            return {"error": "Raindrop client not available"}
        
        try:
            # Try to retrieve the registration metadata from journal-prompts bucket
            try:
                response = self.client.bucket.get(
                    bucket_location={
                        "bucket": {
                            "name": "journal-prompts",
                            "application_name": self.application_name
                        }
                    },
                    key="app-registration-info"
                )
            except:
                # Try without application_name (global scope)
                try:
                    response = self.client.bucket.get(
                        bucket_location={
                            "bucket": {
                                "name": "journal-prompts"
                            }
                        },
                        key="app-registration-info"
                    )
                except Exception as e:
                    return {
                        "application_name": self.application_name,
                        "status": "not_registered",
                        "is_catalogued": False,
                        "error": str(e)
                    }
            
            if response:
                content_str = getattr(response, 'content', str(response))
                try:
                    metadata = json.loads(content_str)
                    return {
                        "application_name": self.application_name,
                        "status": "registered",
                        "is_catalogued": True,
                        "metadata": metadata
                    }
                except json.JSONDecodeError:
                    return {
                        "application_name": self.application_name,
                        "status": "registered",
                        "is_catalogued": True,
                        "raw_response": content_str
                    }
            else:
                return {
                    "application_name": self.application_name,
                    "status": "not_registered",
                    "is_catalogued": False
                }
                
        except Exception as e:
            return {
                "application_name": self.application_name,
                "status": "unknown",
                "is_catalogued": False,
                "error": str(e)
            }
    
    def get_application_info(self) -> Dict[str, Any]:
        """
        Get information about the current application setup
        """
        return {
            "application_name": self.application_name,
            "api_key_configured": bool(self.api_key),
            "client_initialized": self.client is not None,
            "environment": os.getenv('ENVIRONMENT', 'development')
        }

# Global service instance
raindrop_service = RaindropService()