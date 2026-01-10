#!/usr/bin/env python3
"""
Kod yapısı testi - Bağımlılıklar olmadan syntax ve yapı kontrolü
"""

import os
import sys
import ast
import importlib.util

print("=" * 70)
print("🔍 Kod Yapısı ve Syntax Kontrolü")
print("=" * 70)
print()

# SUMO_HOME ayarla
sumo_home = "/opt/homebrew/opt/sumo/share/sumo"
os.environ["SUMO_HOME"] = sumo_home
sys.path.insert(0, os.path.join(sumo_home, "tools"))

def check_syntax(file_path):
    """Dosyanın syntax'ını kontrol et"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_file_exists(file_path):
    """Dosyanın varlığını kontrol et"""
    return os.path.exists(file_path)

def check_imports_in_file(file_path):
    """Dosyadaki import'ları kontrol et (syntax için)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    except:
        return []

print("1️⃣  Python Dosyaları Syntax Kontrolü:")
print("-" * 70)

python_files = [
    "src/environment/sumo_env.py",
    "src/environment/traffic_agent.py",
    "src/algorithms/dqn.py",
    "src/algorithms/maddpg.py",
    "src/algorithms/qmix.py",
    "src/utils/visualization.py",
    "src/utils/metrics.py",
    "src/train.py",
]

all_syntax_ok = True
for file_path in python_files:
    exists = check_file_exists(file_path)
    if not exists:
        print(f"   ❌ {file_path}: Dosya bulunamadı")
        all_syntax_ok = False
        continue
    
    is_valid, error = check_syntax(file_path)
    if is_valid:
        imports = check_imports_in_file(file_path)
        print(f"   ✅ {file_path}")
        if imports:
            print(f"      📦 İmportlar: {', '.join(imports[:5])}{'...' if len(imports) > 5 else ''}")
    else:
        print(f"   ❌ {file_path}: Syntax hatası - {error}")
        all_syntax_ok = False

print()
print("2️⃣  TraCI Import Testi:")
print("-" * 70)
try:
    import traci
    print("   ✅ TraCI başarıyla import edildi")
    print(f"   📍 TraCI modülü: {traci.__file__}")
except ImportError as e:
    print(f"   ❌ TraCI import hatası: {e}")
except Exception as e:
    print(f"   ⚠️  TraCI kontrolü: {e}")

print()
print("3️⃣  Yapılandırma Dosyaları:")
print("-" * 70)
config_files = [
    "configs/default.yaml",
    "requirements.txt",
    "setup.py",
]

for config_file in config_files:
    if check_file_exists(config_file):
        size = os.path.getsize(config_file)
        print(f"   ✅ {config_file} ({size} bytes)")
    else:
        print(f"   ❌ {config_file} bulunamadı")

print()
print("4️⃣  Senaryo Dosyaları:")
print("-" * 70)
scenario_files = [
    "data/scenarios/single_intersection/single_intersection.net.xml",
    "data/scenarios/single_intersection/single_intersection.rou.xml",
    "data/scenarios/single_intersection/single_intersection.sumocfg",
]

for scenario_file in scenario_files:
    if check_file_exists(scenario_file):
        size = os.path.getsize(scenario_file)
        print(f"   ✅ {scenario_file} ({size} bytes)")
    else:
        print(f"   ❌ {scenario_file} bulunamadı")

print()
print("=" * 70)
if all_syntax_ok:
    print("✅ Tüm Python dosyaları syntax hatasızdır!")
    print()
    print("📝 Sonraki adımlar:")
    print("   1. Bağımlılıkları yükleyin: pip install -r requirements.txt")
    print("   2. Test çalıştırın: python3 test_imports.py")
    print("   3. Eğitimi başlatın: python3 src/train.py --algorithm dqn")
else:
    print("⚠️  Bazı dosyalarda sorunlar var. Lütfen kontrol edin.")
print("=" * 70)
