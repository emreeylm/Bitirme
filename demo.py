#!/usr/bin/env python3
"""
Basit demo - Projenin çalıştığını gösterir
"""

import sys
import os

# SUMO_HOME ayarla
sumo_home = "/opt/homebrew/opt/sumo/share/sumo"
os.environ["SUMO_HOME"] = sumo_home
sys.path.insert(0, os.path.join(sumo_home, "tools"))

print("=" * 60)
print("🚦 MARL Trafik Kontrol Projesi - Demo")
print("=" * 60)
print()

# 1. TraCI kontrolü
print("1️⃣  TraCI Kontrolü:")
try:
    import traci
    print("   ✅ TraCI başarıyla import edildi")
except ImportError as e:
    print(f"   ❌ TraCI import hatası: {e}")
    sys.exit(1)

# 2. Proje yapısı kontrolü
print("\n2️⃣  Proje Yapısı Kontrolü:")
files_to_check = [
    ("src/environment/sumo_env.py", "SUMO Environment"),
    ("src/algorithms/dqn.py", "DQN Algorithm"),
    ("src/algorithms/maddpg.py", "MADDPG Algorithm"),
    ("src/algorithms/qmix.py", "QMIX Algorithm"),
    ("configs/default.yaml", "Configuration"),
    ("data/scenarios/single_intersection/single_intersection.sumocfg", "SUMO Scenario"),
]

all_ok = True
for file_path, description in files_to_check:
    if os.path.exists(file_path):
        print(f"   ✅ {description}: {file_path}")
    else:
        print(f"   ❌ {description}: {file_path} bulunamadı")
        all_ok = False

# 3. Senaryo dosyaları
print("\n3️⃣  Senaryo Dosyaları:")
scenario_files = [
    "single_intersection.net.xml",
    "single_intersection.rou.xml",
    "single_intersection.sumocfg",
]
scenario_dir = "data/scenarios/single_intersection"

for filename in scenario_files:
    filepath = os.path.join(scenario_dir, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"   ✅ {filename} ({size} bytes)")
    else:
        print(f"   ❌ {filename} bulunamadı")
        all_ok = False

# 4. Bağımlılık kontrolü (opsiyonel)
print("\n4️⃣  Python Bağımlılıkları (Opsiyonel):")
dependencies = {
    "numpy": "NumPy",
    "torch": "PyTorch",
    "gymnasium": "Gymnasium",
    "matplotlib": "Matplotlib",
    "yaml": "PyYAML",
}

for module, name in dependencies.items():
    try:
        mod = __import__(module)
        version = getattr(mod, "__version__", "bilinmiyor")
        print(f"   ✅ {name}: {version}")
    except ImportError:
        print(f"   ⚠️  {name}: Yüklü değil (pip install {module})")

# 5. Özet
print("\n" + "=" * 60)
if all_ok:
    print("✅ Proje yapısı hazır!")
    print("\n📝 Sonraki adımlar:")
    print("   1. Bağımlılıkları yükleyin: pip install -r requirements.txt")
    print("   2. Test çalıştırın: python3 test_imports.py")
    print("   3. Eğitimi başlatın: python3 src/train.py --algorithm dqn")
else:
    print("⚠️  Bazı dosyalar eksik. Lütfen kontrol edin.")
print("=" * 60)
