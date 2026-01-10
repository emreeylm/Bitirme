#!/usr/bin/env python3
"""
Import testleri - Kod yapısının doğru olup olmadığını kontrol eder.
"""

import sys
import os

# SUMO_HOME ayarla
sumo_home = "/opt/homebrew/opt/sumo/share/sumo"
os.environ["SUMO_HOME"] = sumo_home
sys.path.insert(0, os.path.join(sumo_home, "tools"))

print("🔍 Import testleri başlatılıyor...\n")

# Test 1: TraCI
try:
    import traci
    print("✅ traci import başarılı")
except ImportError as e:
    print(f"❌ traci import hatası: {e}")
    sys.exit(1)

# Test 2: Proje modülleri
try:
    from src.environment.sumo_env import SumoEnvironment
    print("✅ SumoEnvironment import başarılı")
except ImportError as e:
    print(f"❌ SumoEnvironment import hatası: {e}")

try:
    from src.environment.traffic_agent import AgentState, AgentAction, RewardFunction
    print("✅ TrafficAgent modülleri import başarılı")
except ImportError as e:
    print(f"❌ TrafficAgent import hatası: {e}")

try:
    from src.algorithms.dqn import DQNAgent
    print("✅ DQNAgent import başarılı")
except ImportError as e:
    print(f"❌ DQNAgent import hatası: {e}")

try:
    from src.algorithms.maddpg import MADDPG
    print("✅ MADDPG import başarılı")
except ImportError as e:
    print(f"❌ MADDPG import hatası: {e}")

try:
    from src.algorithms.qmix import QMIX
    print("✅ QMIX import başarılı")
except ImportError as e:
    print(f"❌ QMIX import hatası: {e}")

try:
    from src.utils.visualization import plot_training_curves
    print("✅ Visualization utils import başarılı")
except ImportError as e:
    print(f"❌ Visualization import hatası: {e}")

try:
    from src.utils.metrics import calculate_metrics
    print("✅ Metrics utils import başarılı")
except ImportError as e:
    print(f"❌ Metrics import hatası: {e}")

# Test 3: PyTorch
try:
    import torch
    print(f"✅ PyTorch import başarılı (version: {torch.__version__})")
except ImportError:
    print("⚠️  PyTorch bulunamadı - 'pip install torch' ile yükleyin")

# Test 4: Diğer bağımlılıklar
try:
    import numpy as np
    print(f"✅ NumPy import başarılı (version: {np.__version__})")
except ImportError:
    print("⚠️  NumPy bulunamadı")

try:
    import yaml
    print("✅ PyYAML import başarılı")
except ImportError:
    print("⚠️  PyYAML bulunamadı")

print("\n🎉 Import testleri tamamlandı!")
print("\n📝 Not: SUMO simülasyonu için network erişimi gereklidir.")
print("   Gerçek test için: python3 test_run.py (network izni ile)")
