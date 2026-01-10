#!/usr/bin/env python3
"""
SUMO network dosyası oluşturucu - Basit 4 yönlü kavşak
"""

import os
import subprocess

# Basit bir node dosyası oluştur
nodes_content = """<?xml version="1.0" encoding="UTF-8"?>
<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="n0" x="0.0" y="50.0" type="priority"/>
    <node id="n1" x="100.0" y="50.0" type="traffic_light"/>
    <node id="n2" x="200.0" y="50.0" type="priority"/>
    <node id="n3" x="100.0" y="0.0" type="priority"/>
    <node id="n4" x="100.0" y="100.0" type="priority"/>
</nodes>
"""

# Edge dosyası oluştur
edges_content = """<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="n0n1" from="n0" to="n1" priority="1" numLanes="1" speed="13.89"/>
    <edge id="n1n2" from="n1" to="n2" priority="1" numLanes="1" speed="13.89"/>
    <edge id="n2n1" from="n2" to="n1" priority="1" numLanes="1" speed="13.89"/>
    <edge id="n1n0" from="n1" to="n0" priority="1" numLanes="1" speed="13.89"/>
    <edge id="n3n1" from="n3" to="n1" priority="1" numLanes="1" speed="13.89"/>
    <edge id="n1n4" from="n1" to="n4" priority="1" numLanes="1" speed="13.89"/>
    <edge id="n4n1" from="n4" to="n1" priority="1" numLanes="1" speed="13.89"/>
    <edge id="n1n3" from="n1" to="n3" priority="1" numLanes="1" speed="13.89"/>
</edges>
"""

# Dosyaları yaz
with open("nodes.nod.xml", "w") as f:
    f.write(nodes_content)

with open("edges.edg.xml", "w") as f:
    f.write(edges_content)

print("✅ Node ve Edge dosyaları oluşturuldu")

# netconvert ile network oluştur
sumo_home = "/opt/homebrew/opt/sumo"
netconvert = f"{sumo_home}/bin/netconvert"

cmd = [
    netconvert,
    "--node-files", "nodes.nod.xml",
    "--edge-files", "edges.edg.xml",
    "--output-file", "single_intersection.net.xml",
    "--no-turnarounds",
    "--no-internal-links",
]

print("🔄 Network dosyası oluşturuluyor...")
try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print("✅ Network dosyası başarıyla oluşturuldu!")
    print(f"   Dosya: single_intersection.net.xml")
except subprocess.CalledProcessError as e:
    print(f"❌ Hata: {e}")
    print(f"   stdout: {e.stdout}")
    print(f"   stderr: {e.stderr}")
    print("\n⚠️  Manuel network dosyası kullanılacak")
