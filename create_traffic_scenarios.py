#!/usr/bin/env python3
"""
Tek kavşak için düşük, orta ve yüksek trafik senaryoları oluştur
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_route_file(filename, vehicles_per_hour, num_routes=4):
    """Route dosyası oluştur"""
    
    routes = ET.Element("routes")
    routes.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    routes.set("xsi:noNamespaceSchemaLocation", "http://sumo.dlr.de/xsd/routes_file.xsd")
    
    # Vehicle type
    vtype = ET.SubElement(routes, "vType")
    vtype.set("id", "type1")
    vtype.set("accel", "2.6")
    vtype.set("decel", "4.5")
    vtype.set("sigma", "0.5")
    vtype.set("length", "5")
    vtype.set("minGap", "2.5")
    vtype.set("maxSpeed", "13.89")
    vtype.set("guiShape", "passenger")
    
    # Routes (4 yön için)
    route_edges = [
        ["n0n1", "n1n3"],  # Batıdan doğuya
        ["n2n1", "n1n4"],  # Kuzeyden güneye
        ["n3n1", "n1n0"],  # Doğudan batıya
        ["n4n1", "n1n2"],  # Güneyden kuzeye
    ]
    
    for i, edges in enumerate(route_edges[:num_routes]):
        route = ET.SubElement(routes, "route")
        route.set("id", f"r{i}")
        route.set("edges", " ".join(edges))
        
        # Flow (araç akışı)
        flow = ET.SubElement(routes, "flow")
        flow.set("id", f"flow{i}")
        flow.set("type", "type1")
        flow.set("route", f"r{i}")
        flow.set("begin", "0")
        flow.set("end", "900")
        flow.set("vehsPerHour", str(vehicles_per_hour))
    
    # XML'i güzel formatla yaz
    rough_string = ET.tostring(routes, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty = reparsed.toprettyxml(indent="    ")
    
    # İlk satırı kaldır (<?xml version="1.0" ?> zaten var)
    lines = pretty.split('\n')
    if lines[0].startswith('<?xml'):
        lines = lines[1:]
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ {filename} oluşturuldu ({vehicles_per_hour} araç/saat)")

if __name__ == "__main__":
    scenario_dir = "data/scenarios/single_intersection_new"
    os.makedirs(scenario_dir, exist_ok=True)
    
    # Düşük trafik: 200 araç/saat
    create_route_file(
        os.path.join(scenario_dir, "traffic_low.rou.xml"),
        vehicles_per_hour=200
    )
    
    # Orta trafik: 500 araç/saat
    create_route_file(
        os.path.join(scenario_dir, "traffic_medium.rou.xml"),
        vehicles_per_hour=500
    )
    
    # Yüksek trafik: 1000 araç/saat
    create_route_file(
        os.path.join(scenario_dir, "traffic_high.rou.xml"),
        vehicles_per_hour=1000
    )
    
    print("\n✅ Tüm trafik senaryoları oluşturuldu!")
    print(f"   Düşük:  200 araç/saat")
    print(f"   Orta:   500 araç/saat")
    print(f"   Yüksek: 1000 araç/saat")
