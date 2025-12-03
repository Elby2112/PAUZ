try:
    import raindrop.raindrop
    print("✅ raindrop.raindrop submodule found")
    print(f"📍 Location: {raindrop.raindrop.__file__}")
    print(f"📦 Contents: {dir(raindrop.raindrop)}")
except ImportError as e:
    print(f"❌ raindrop.raindrop import failed: {e}")

try:
    from raindrop.raindrop import ClientRaindropPartner
    print("✅ ClientRaindropPartner imported successfully")
except Exception as e:
    print(f"❌ ClientRaindropPartner failed: {e}")