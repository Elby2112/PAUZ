"""
Clear all caches for fresh testing
"""
import sys
sys.path.append('.')

try:
    from app.services.stats_service import stats_service
    stats_service.cache.clear()
    print("✅ Stats cache cleared")
except:
    print("⚠️  Stats cache not available")

try:
    from app.services.journal_loading_service import journal_loading_service
    journal_loading_service.cache.clear()
    print("✅ Journal loading cache cleared")
except:
    print("⚠️  Journal loading cache not available")

print()
print("🎯 All caches cleared!")
print("🚀 Ready for fresh testing of performance optimizations!")