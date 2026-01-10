#!/usr/bin/env python3
"""
Baseline metrikleri topla - DQN eğitimi olmadan
Random policy veya sabit zamanlı kontrol ile
"""

import os
import sys
import numpy as np
from typing import Dict, List

# SUMO_HOME ayarla
sumo_home = "/opt/homebrew/opt/sumo/share/sumo"
os.environ["SUMO_HOME"] = sumo_home
sys.path.insert(0, os.path.join(sumo_home, "tools"))

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import traci
from src.utils.metrics import calculate_metrics


def run_baseline_simulation(
    sumo_cfg: str,
    net_file: str,
    route_file: str,
    policy: str = "random",
    num_episodes: int = 10,
    num_seconds: int = 900,
    delta_time: int = 5,
) -> Dict[str, List[float]]:
    """
    Baseline simülasyon çalıştır ve metrikleri topla.
    
    Args:
        sumo_cfg: SUMO config dosyası
        net_file: Network dosyası
        route_file: Route dosyası
        policy: "random" veya "fixed" (sabit zamanlı)
        num_episodes: Episode sayısı
        num_seconds: Episode süresi
        delta_time: Adım aralığı
        
    Returns:
        Dictionary of metrics lists
    """
    
    print(f"🚦 Baseline Simülasyon: {policy.upper()} Policy")
    print("=" * 60)
    
    metrics_history = {
        "waiting_time": [],
        "queue_length": [],
        "stops": [],
        "delay": [],
        "throughput": [],
        "fuel_consumption": [],
        "co2_emission": [],
    }
    
    config_dir = os.path.dirname(os.path.abspath(sumo_cfg))
    config_name = os.path.basename(sumo_cfg)
    original_dir = os.getcwd()
    
    sumo_binary = "/opt/homebrew/opt/sumo/bin/sumo"
    
    for episode in range(num_episodes):
        try:
            os.chdir(config_dir)
            
            traci.start([
                sumo_binary,
                "-c", config_name,
                "--no-step-log",
                "--no-warnings",
            ])
            
            traffic_lights = list(traci.trafficlight.getIDList())
            
            episode_metrics = {
                "waiting_time": [],
                "queue_length": [],
                "stops": [],
                "delay": [],
                "throughput": [],
            }
            
            current_step = 0
            phase_timer = {tl_id: 0 for tl_id in traffic_lights}
            current_phase = {tl_id: 0 for tl_id in traffic_lights}
            
            while current_step < num_seconds:
                # Policy uygula
                if policy == "random":
                    # Random policy: Rastgele faz seç
                    for tl_id in traffic_lights:
                        if phase_timer[tl_id] >= 30:  # 30 saniyede bir değiştir
                            new_phase = np.random.randint(0, 4)
                            traci.trafficlight.setPhase(tl_id, new_phase)
                            current_phase[tl_id] = new_phase
                            phase_timer[tl_id] = 0
                        else:
                            phase_timer[tl_id] += delta_time
                
                elif policy == "fixed":
                    # Fixed-time policy: Sabit döngü (42s yeşil, 3s sarı)
                    for tl_id in traffic_lights:
                        if phase_timer[tl_id] >= 45:  # 42s yeşil + 3s sarı
                            current_phase[tl_id] = (current_phase[tl_id] + 1) % 4
                            traci.trafficlight.setPhase(tl_id, current_phase[tl_id])
                            phase_timer[tl_id] = 0
                        else:
                            phase_timer[tl_id] += delta_time
                
                # Simüle et
                for _ in range(delta_time):
                    traci.simulationStep()
                    current_step += 1
                
                # Metrikleri topla (her 10 adımda bir)
                if current_step % 50 == 0:
                    metrics = calculate_metrics(traffic_lights, include_emissions=True)
                    episode_metrics["waiting_time"].append(metrics.get("avg_waiting_time", 0))
                    episode_metrics["queue_length"].append(metrics.get("avg_queue_length", 0))
                    episode_metrics["stops"].append(metrics.get("avg_stops", 0))
                    episode_metrics["delay"].append(metrics.get("avg_delay", 0))
                    episode_metrics["throughput"].append(metrics.get("throughput", 0))
            
            # Episode sonu metrikleri
            final_metrics = calculate_metrics(traffic_lights, include_emissions=True)
            
            metrics_history["waiting_time"].append(np.mean(episode_metrics["waiting_time"]))
            metrics_history["queue_length"].append(np.mean(episode_metrics["queue_length"]))
            metrics_history["stops"].append(np.mean(episode_metrics["stops"]))
            metrics_history["delay"].append(np.mean(episode_metrics["delay"]))
            metrics_history["throughput"].append(np.mean(episode_metrics["throughput"]))
            metrics_history["fuel_consumption"].append(final_metrics.get("total_fuel_consumption", 0))
            metrics_history["co2_emission"].append(final_metrics.get("total_co2_emission", 0))
            
            traci.close()
            os.chdir(original_dir)
            
            print(f"   Episode {episode+1}/{num_episodes}: "
                  f"Waiting={metrics_history['waiting_time'][-1]:.2f}s, "
                  f"Queue={metrics_history['queue_length'][-1]:.2f}")
            
        except Exception as e:
            print(f"   ❌ Episode {episode+1} hatası: {e}")
            try:
                traci.close()
                os.chdir(original_dir)
            except:
                pass
    
    return metrics_history


def print_summary(metrics: Dict[str, List[float]], policy: str):
    """Metrik özetini yazdır"""
    
    print("\n" + "=" * 60)
    print(f"📊 {policy.upper()} Policy Özeti")
    print("=" * 60)
    
    for metric_name, values in metrics.items():
        if values:
            mean_val = np.mean(values)
            std_val = np.std(values)
            min_val = np.min(values)
            max_val = np.max(values)
            
            print(f"\n{metric_name.replace('_', ' ').title()}:")
            print(f"   Ortalama: {mean_val:.2f} ± {std_val:.2f}")
            print(f"   Min: {min_val:.2f}")
            print(f"   Max: {max_val:.2f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Baseline metrikleri topla")
    parser.add_argument("--config", type=str, default="single_low",
                        choices=["single_low", "single_medium", "single_high"],
                        help="Senaryo")
    parser.add_argument("--policy", type=str, default="random",
                        choices=["random", "fixed"],
                        help="Policy tipi")
    parser.add_argument("--episodes", type=int, default=10,
                        help="Episode sayısı")
    
    args = parser.parse_args()
    
    # Senaryo dosyaları
    scenario_dir = "data/scenarios/single_intersection_new"
    
    configs = {
        "single_low": {
            "sumo_cfg": f"{scenario_dir}/map_low.sumocfg",
            "net_file": f"{scenario_dir}/single_tls.net.xml",
            "route_file": f"{scenario_dir}/traffic_low.rou.xml",
        },
        "single_medium": {
            "sumo_cfg": f"{scenario_dir}/map_medium.sumocfg",
            "net_file": f"{scenario_dir}/single_tls.net.xml",
            "route_file": f"{scenario_dir}/traffic_medium.rou.xml",
        },
        "single_high": {
            "sumo_cfg": f"{scenario_dir}/map_high.sumocfg",
            "net_file": f"{scenario_dir}/single_tls.net.xml",
            "route_file": f"{scenario_dir}/traffic_high.rou.xml",
        },
    }
    
    config = configs[args.config]
    
    print(f"📁 Senaryo: {args.config}")
    print(f"🎯 Policy: {args.policy}")
    print(f"📊 Episode sayısı: {args.episodes}")
    print()
    
    # Simülasyon çalıştır
    metrics = run_baseline_simulation(
        sumo_cfg=config["sumo_cfg"],
        net_file=config["net_file"],
        route_file=config["route_file"],
        policy=args.policy,
        num_episodes=args.episodes,
        num_seconds=900,
        delta_time=5,
    )
    
    # Özet yazdır
    print_summary(metrics, args.policy)
    
    # Sonuçları kaydet
    import json
    output_file = f"experiments/results/baseline_{args.config}_{args.policy}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({k: [float(v) for v in vals] for k, vals in metrics.items()}, f, indent=2)
    
    print(f"\n✅ Sonuçlar kaydedildi: {output_file}")
