#!/usr/bin/env python3
"""
Basit test scripti - SUMO ortamını ve temel fonksiyonları test eder.
"""

import os
import sys

# SUMO_HOME ayarla
sumo_home = "/opt/homebrew/opt/sumo/share/sumo"
if "SUMO_HOME" not in os.environ:
    os.environ["SUMO_HOME"] = sumo_home

# SUMO tools'u Python path'e ekle
tools_path = os.path.join(sumo_home, "tools")
if os.path.exists(tools_path):
    sys.path.insert(0, tools_path)
    print(f"✅ SUMO tools path eklendi: {tools_path}")

try:
    import traci
    print("✅ TraCI import başarılı!")
except ImportError as e:
    print(f"❌ TraCI import hatası: {e}")
    print(f"SUMO_HOME: {os.environ.get('SUMO_HOME', 'AYARLANMAMIŞ')}")
    sys.exit(1)

# SUMO binary kontrolü
sumo_binary = "/opt/homebrew/opt/sumo/bin/sumo"
if not os.path.exists(sumo_binary):
    sumo_binary = "sumo"  # PATH'te olabilir

print(f"✅ SUMO binary: {sumo_binary}")

# Senaryo dosyalarını kontrol et
scenario_dir = "data/scenarios/single_intersection"
net_file = os.path.join(scenario_dir, "single_intersection.net.xml")
rou_file = os.path.join(scenario_dir, "single_intersection.rou.xml")
cfg_file = os.path.join(scenario_dir, "single_intersection.sumocfg")

print(f"\n📁 Senaryo dosyaları:")
print(f"  Network: {net_file} - {'✅' if os.path.exists(net_file) else '❌'}")
print(f"  Routes: {rou_file} - {'✅' if os.path.exists(rou_file) else '❌'}")
print(f"  Config: {cfg_file} - {'✅' if os.path.exists(cfg_file) else '❌'}")

if not all(os.path.exists(f) for f in [net_file, rou_file, cfg_file]):
    print("\n❌ Senaryo dosyaları eksik!")
    sys.exit(1)

# SUMO'yu başlat
print("\n🚀 SUMO'yu başlatıyorum...")
try:
    # Config dosyasının bulunduğu dizine geç
    original_dir = os.getcwd()
    os.chdir(scenario_dir)
    
    # TraCI'yi başlat - port otomatik seçilecek
    traci.start([
        sumo_binary,
        "-c", "single_intersection.sumocfg",
        "--no-step-log",
        "--no-warnings",
    ], port=8813)
    print("✅ SUMO başarıyla başlatıldı!")
    
    # Trafik ışıklarını kontrol et
    tl_ids = traci.trafficlight.getIDList()
    print(f"\n🚦 Trafik ışıkları: {tl_ids}")
    
    if tl_ids:
        tl_id = tl_ids[0]
        print(f"\n📊 Trafik ışığı '{tl_id}' bilgileri:")
        print(f"  Mevcut faz: {traci.trafficlight.getPhase(tl_id)}")
        print(f"  Kontrol edilen şeritler: {traci.trafficlight.getControlledLanes(tl_id)}")
        
        # Birkaç adım simüle et
        print("\n🔄 10 adım simüle ediyorum...")
        for step in range(10):
            traci.simulationStep()
            phase = traci.trafficlight.getPhase(tl_id)
            vehicle_count = len(traci.vehicle.getIDList())
            if step % 2 == 0:
                print(f"  Adım {step}: Faz={phase}, Araç sayısı={vehicle_count}")
    
    traci.close()
    os.chdir(original_dir)
    print("\n✅ Test başarıyla tamamlandı!")
    
except Exception as e:
    print(f"\n❌ Hata: {e}")
    import traceback
    traceback.print_exc()
    try:
        traci.close()
    except:
        pass
    sys.exit(1)

print("\n🎉 Tüm testler başarılı! Proje çalışmaya hazır.")
