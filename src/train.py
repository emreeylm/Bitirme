"""
Training script for MARL traffic signal control agents.

Supports DQN (single-agent), MADDPG, and QMIX algorithms.
"""

import argparse
import os
import sys
import yaml
import numpy as np
from typing import Dict, Any

# SUMO_HOME ayarla
sumo_home = "/opt/homebrew/opt/sumo/share/sumo"
if "SUMO_HOME" not in os.environ:
    os.environ["SUMO_HOME"] = sumo_home

# SUMO tools'u Python path'e ekle
tools_path = os.path.join(sumo_home, "tools")
if os.path.exists(tools_path) and tools_path not in sys.path:
    sys.path.insert(0, tools_path)

try:
    import torch
except ImportError:
    print("⚠️  PyTorch bulunamadı. RL algoritmaları çalışmayacak.")
    print("   Yüklemek için: pip install torch")
    torch = None

# Proje root'unu path'e ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.environment.sumo_env import SumoEnvironment
from src.utils.metrics import calculate_metrics
if torch:
    from src.algorithms.dqn import DQNAgent
    from src.algorithms.maddpg import MADDPG
    from src.algorithms.qmix import QMIX
else:
    DQNAgent = None
    MADDPG = None
    QMIX = None


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def train_dqn(env: SumoEnvironment, config: Dict[str, Any]):
    """Train DQN agent for single intersection."""
    if DQNAgent is None:
        print("❌ PyTorch yüklü değil. DQN eğitimi yapılamaz.")
        print("   Yüklemek için: pip install torch")
        return None, [], []
    
    print("Training DQN agent...")
    
    # Initialize agent
    # Flatten state dimension for multi-agent scenarios
    obs_shape = env.observation_space.shape
    state_dim = 1
    for dim in obs_shape:
        state_dim *= dim
    action_dim = env.action_space.n
    
    print(f"   State dim: {state_dim}, Action dim: {action_dim}")
    print(f"   Observation shape: {obs_shape}")
    
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        lr=config.get("lr", 0.001),
        gamma=config.get("gamma", 0.99),
        epsilon_start=config.get("epsilon_start", 1.0),
        epsilon_end=config.get("epsilon_end", 0.01),
        epsilon_decay=config.get("epsilon_decay", 0.995),
        batch_size=config.get("batch_size", 64),
        buffer_size=config.get("buffer_size", 10000),
        device=config.get("device", "cpu"),
    )
    
    # Training loop
    num_episodes = config.get("num_episodes", 1000)
    max_steps = config.get("max_steps", 3600)
    
    rewards_history = []
    losses_history = []
    
    # Metrik geçmişi
    metrics_history = {
        "waiting_time": [],
        "queue_length": [],
        "stops": [],
        "delay": [],
        "throughput": [],
        "fuel_consumption": [],
        "co2_emission": [],
    }
    
    for episode in range(num_episodes):
        state, info = env.reset()
        episode_reward = 0
        episode_losses = []
        episode_metrics = {
            "waiting_time": [],
            "queue_length": [],
            "stops": [],
            "delay": [],
            "throughput": [],
        }
        
        for step in range(max_steps):
            # Select action
            action = agent.select_action(state.flatten(), training=True)
            
            # Take step
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Store transition
            agent.store_transition(
                state.flatten(),
                action,
                reward,
                next_state.flatten(),
                done,
            )
            
            # Train agent
            loss = agent.train()
            if loss is not None:
                episode_losses.append(loss)
            
            episode_reward += reward
            state = next_state
            
            # Metrikleri topla (her 50 adımda bir)
            if step % 50 == 0:
                try:
                    metrics = calculate_metrics(
                        env.traffic_lights,
                        include_emissions=True
                    )
                    episode_metrics["waiting_time"].append(metrics.get("avg_waiting_time", 0))
                    episode_metrics["queue_length"].append(metrics.get("avg_queue_length", 0))
                    episode_metrics["stops"].append(metrics.get("avg_stops", 0))
                    episode_metrics["delay"].append(metrics.get("avg_delay", 0))
                    episode_metrics["throughput"].append(metrics.get("throughput", 0))
                except:
                    pass
            
            if done:
                break
        
        # Episode sonu metrikleri
        try:
            final_metrics = calculate_metrics(
                env.traffic_lights,
                include_emissions=True
            )
            metrics_history["waiting_time"].append(np.mean(episode_metrics["waiting_time"]) if episode_metrics["waiting_time"] else 0)
            metrics_history["queue_length"].append(np.mean(episode_metrics["queue_length"]) if episode_metrics["queue_length"] else 0)
            metrics_history["stops"].append(np.mean(episode_metrics["stops"]) if episode_metrics["stops"] else 0)
            metrics_history["delay"].append(np.mean(episode_metrics["delay"]) if episode_metrics["delay"] else 0)
            metrics_history["throughput"].append(np.mean(episode_metrics["throughput"]) if episode_metrics["throughput"] else 0)
            metrics_history["fuel_consumption"].append(final_metrics.get("total_fuel_consumption", 0))
            metrics_history["co2_emission"].append(final_metrics.get("total_co2_emission", 0))
        except:
            # Metrik hesaplama başarısız olursa sıfır ekle
            for key in metrics_history:
                metrics_history[key].append(0)
        
        # Update epsilon
        agent.update_epsilon()
        
        # Logging
        avg_loss = np.mean(episode_losses) if episode_losses else 0.0
        rewards_history.append(episode_reward)
        losses_history.append(avg_loss)
        
        if (episode + 1) % 10 == 0:
            avg_waiting = metrics_history["waiting_time"][-1] if metrics_history["waiting_time"] else 0
            avg_queue = metrics_history["queue_length"][-1] if metrics_history["queue_length"] else 0
            avg_stops = metrics_history["stops"][-1] if metrics_history["stops"] else 0
            
            print(
                f"Episode {episode + 1}/{num_episodes} | "
                f"Reward: {episode_reward:.2f} | "
                f"Loss: {avg_loss:.4f} | "
                f"Epsilon: {agent.epsilon:.3f}"
            )
            print(
                f"  📊 Metrikler: "
                f"Bekleme={avg_waiting:.2f}s | "
                f"Kuyruk={avg_queue:.2f} | "
                f"Duruş={avg_stops:.3f}"
            )
        
        # Save checkpoint
        if (episode + 1) % config.get("save_freq", 100) == 0:
            checkpoint_path = os.path.join(
                config.get("checkpoint_dir", "experiments/checkpoints"),
                f"dqn_episode_{episode + 1}.pt"
            )
            os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
            agent.save(checkpoint_path)
    
    env.close()
    
    # Final özet
    print("\n" + "=" * 70)
    print("📊 Eğitim Tamamlandı - Final Metrikler")
    print("=" * 70)
    
    if metrics_history["waiting_time"]:
        print(f"\n⏱️  Ortalama Bekleme Süresi: {np.mean(metrics_history['waiting_time']):.2f} ± {np.std(metrics_history['waiting_time']):.2f} saniye")
        print(f"📏 Ortalama Kuyruk Uzunluğu: {np.mean(metrics_history['queue_length']):.2f} ± {np.std(metrics_history['queue_length']):.2f}")
        print(f"🛑 Ortalama Duruş Sayısı: {np.mean(metrics_history['stops']):.3f} ± {np.std(metrics_history['stops']):.3f}")
        print(f"⏳ Ortalama Gecikme: {np.mean(metrics_history['delay']):.2f} ± {np.std(metrics_history['delay']):.2f} saniye")
        print(f"🚗 Ortalama Akış (Throughput): {np.mean(metrics_history['throughput']):.2f} ± {np.std(metrics_history['throughput']):.2f} araç")
        
        if metrics_history["fuel_consumption"][-1] > 0:
            print(f"⛽ Toplam Yakıt Tüketimi: {metrics_history['fuel_consumption'][-1]:.2f} ml")
            print(f"🌍 Toplam CO2 Emisyonu: {metrics_history['co2_emission'][-1]:.2f} g")
        
        print(f"\n📈 En İyi Episode:")
        best_idx = np.argmax(rewards_history)
        print(f"   Episode {best_idx + 1}: Reward={rewards_history[best_idx]:.2f}")
        print(f"   Bekleme: {metrics_history['waiting_time'][best_idx]:.2f}s")
        print(f"   Kuyruk: {metrics_history['queue_length'][best_idx]:.2f}")
    
    print("=" * 70)
    
    return agent, rewards_history, losses_history, metrics_history


def train_maddpg(env: SumoEnvironment, config: Dict[str, Any]):
    """Train MADDPG agents for multi-intersection scenario."""
    print("Training MADDPG agents...")
    # Implementation similar to train_dqn but for multi-agent
    # This is a placeholder structure
    pass


def train_qmix(env: SumoEnvironment, config: Dict[str, Any]):
    """Train QMIX agents for multi-intersection scenario."""
    print("Training QMIX agents...")
    # Implementation similar to train_dqn but for multi-agent
    # This is a placeholder structure
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Train MARL agents for traffic signal control"
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        choices=["dqn", "maddpg", "qmix"],
        required=True,
        help="RL algorithm to use",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="single_intersection",
        help="Traffic scenario to use",
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with scenario-specific config if available
    scenario_config_path = f"configs/{args.scenario}.yaml"
    if os.path.exists(scenario_config_path):
        scenario_config = load_config(scenario_config_path)
        config.update(scenario_config)
    
    # Create environment
    env = SumoEnvironment(
        sumo_cfg=config["sumo_cfg"],
        net_file=config["net_file"],
        route_file=config["route_file"],
        use_gui=config.get("use_gui", False),
        num_seconds=config.get("num_seconds", 3600),
        yellow_time=config.get("yellow_time", 3),
        min_green_time=config.get("min_green_time", 10),
        max_green_time=config.get("max_green_time", 60),
        delta_time=config.get("delta_time", 5),
    )
    
    # Train based on algorithm
    if args.algorithm == "dqn":
        if DQNAgent is None:
            print("❌ PyTorch yüklü değil. DQN eğitimi yapılamaz.")
            sys.exit(1)
        agent, rewards, losses, metrics = train_dqn(env, config)
        
        # Metrikleri kaydet
        import json
        results_dir = config.get("log_dir", "experiments/logs")
        os.makedirs(results_dir, exist_ok=True)
        
        results = {
            "rewards": [float(r) for r in rewards],
            "losses": [float(l) for l in losses],
            "metrics": {k: [float(v) for v in vals] for k, vals in metrics.items()}
        }
        
        results_file = os.path.join(results_dir, "training_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Sonuçlar kaydedildi: {results_file}")
    elif args.algorithm == "maddpg":
        if MADDPG is None:
            print("❌ PyTorch yüklü değil. MADDPG eğitimi yapılamaz.")
            sys.exit(1)
        train_maddpg(env, config)
    elif args.algorithm == "qmix":
        if QMIX is None:
            print("❌ PyTorch yüklü değil. QMIX eğitimi yapılamaz.")
            sys.exit(1)
        train_qmix(env, config)
    
    print("Training completed!")


if __name__ == "__main__":
    main()
