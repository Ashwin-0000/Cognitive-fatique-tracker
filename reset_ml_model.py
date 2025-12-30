"""Reset ML model and start fresh for real data"""
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ml.ml_predictor import MLPredictor
from src.ml.personalization import PersonalizationEngine
from src.ml.model_manager import ModelManager

print("="*70)
print("RESETTING ML MODEL FOR REAL DATA")
print("="*70)

# Initialize components
model_manager = ModelManager()
personalization = PersonalizationEngine()

print("\n📊 Current Model State:")
stats = model_manager.get_training_stats()
print(f"   Total versions: {stats['total_versions']}")
print(f"   Has model: {stats['has_model']}")

pers_stats = personalization.get_profile_stats()
print(f"\n👤 Current Personalization:")
print(f"   Sessions: {pers_stats['total_sessions']}")
print(f"   ML Weight: {pers_stats['ml_weight']:.0%}")

print("\n⚠️  The model was trained on synthetic data which doesn't match")
print("   real usage patterns. This causes high predictions from the start.")

response = input("\n❓ Do you want to reset the model and start fresh? (y/n): ")

if response.lower() == 'y':
    print("\n🔄 Resetting model and personalization...")
    
    # Reset model
    model_manager.reset_model()
    print("   ✅ Model reset")
    
    # Reset personalization  
    personalization.reset_profile()
    print("   ✅ Personalization reset")
    
    print("\n✅ Reset complete!")
    print("\n📝 What happens now:")
    print("   • ML will start at 0% weight (pure rule-based)")
    print("   • It will collect data from YOUR real usage")
    print("   • After 5 sessions, ML will begin at 30% weight")
    print("   • After 20 sessions, ML will reach 85% weight")
    print("   • The model will learn YOUR specific patterns")
    
    print("\n💡 This is actually better because:")
    print("   • Trains on YOUR actual behavior")
    print("   • More accurate for YOUR fatigue patterns")
    print("   • No bias from synthetic data")
    
else:
    print("\n❌ Reset cancelled")
    print("\n💡 Alternative fixes:")
    print("   1. Lower the ML weight initially")
    print("   2. Manually adjust personalization thresholds")
    print("   3. Wait for model to adapt with more real sessions")

print("\n" + "="*70)
