#!/usr/bin/env python3
"""
Eğitilmiş modeli değerlendir ve sonuçları görselleştir
"""

import os
import sys

# SUMO_HOME ayarla
sumo_home = "/opt/homebrew/opt/sumo/share/sumo"
os.environ["SUMO_HOME"] = sumo_home
sys.path.insert(0, os.path.join(sumo_home, "tools"))

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import torch
import numpy as np
from src.environment.sumo_env import SumoEnvironment
from src.algorithms.dqn import DQNAgent

def evaluate_model(checkpoint_path, config_name="bursa", num_episodes=5):
    """Modeli değerlendir"""
    
    print("=" * 60)
    print(f"🎯 Model Değerlendirmesi: {checkpoint_path}")
    print("=" * 60)
    
    # Environment oluştur
    if config_name == "bursa":
        env = SumoEnvironment(
            sumo_cfg="data/scenarios/bursa/bursa.sumocfg",
            net_file="data/scenarios/bursa/new_clean.net.xml",
            route_file="data/scenarios/bursa/traffic_low_new.rou.xml",
            use_gui=False,
            num_seconds=500,
            delta_time=5,
        )
    else:
        env = SumoEnvironment(
            sumo_cfg="data/scenarios/single_intersection/single_intersection.sumocfg",
            net_file="data/scenarios/single_intersection/single_intersection.net.xml",
            route_file="data/scenarios/single_intersection/single_intersection.rou.xml",
            use_gui=False,
            num_seconds=500,
            delta_time=5,
        )
    
    print(f"✅ Environment: {env.num_tls} trafik ışığı")
    
    # Agent oluştur
    obs_shape = env.observation_space.shape
    state_dim = 1
    for dim in obs_shape:
        state_dim *= dim
    action_dim = env.action_space.n
    
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        device="cpu",
    )
    
    # Checkpoint yükle
    if os.path.exists(checkpoint_path):
        agent.load(checkpoint_path)
        print(f"✅ Checkpoint yüklendi: {checkpoint_path}")
    else:
        print(f"❌ Checkpoint bulunamadı: {checkpoint_path}")
        return
    
    # Değerlendirme
    agent.epsilon = 0.0  # Keşif yok, sadece exploitation
    
    rewards = []
    waiting_times = []
    
    for ep in range(num_episodes):
        state, info = env.reset()
        episode_reward = 0
        episode_waiting = 0
        steps = 0
        
        done = False
        while not done:
            action = agent.select_action(state.flatten(), training=False)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            episode_reward += reward
            episode_waiting += info.get("total_waiting_time", 0)
            steps += 1
            state = next_state
        
        rewards.append(episode_reward)
        waiting_times.append(episode_waiting / max(steps, 1))
        print(f"   Episode {ep+1}: Reward={episode_reward:.2f}, Avg Waiting={waiting_times[-1]:.2f}")
    
    env.close()
    
    # Sonuçlar
    print("\n" + "=" * 60)
    print("📊 Değerlendirme Sonuçları")
    print("=" * 60)
    print(f"   Ortalama Reward: {np.mean(rewards):.2f} ± {np.std(rewards):.2f}")
    print(f"   Ortalama Bekleme: {np.mean(waiting_times):.2f} ± {np.std(waiting_times):.2f}")
    print(f"   En İyi Reward: {max(rewards):.2f}")
    print(f"   En Kötü Reward: {min(rewards):.2f}")
    
    return rewards, waiting_times


def compare_with_baseline(config_name="bursa", num_episodes=3):
    """Random baseline ile karşılaştır"""
    
    print("\n" + "=" * 60)
    print("📊 Baseline Karşılaştırması (Random vs Eğitilmiş)")
    print("=" * 60)
    
    # Environment
    if config_name == "bursa":
        env = SumoEnvironment(
            sumo_cfg="data/scenarios/bursa/bursa.sumocfg",
            net_file="data/scenarios/bursa/new_clean.net.xml",
            route_file="data/scenarios/bursa/traffic_low_new.rou.xml",
            use_gui=False,
            num_seconds=500,
            delta_time=5,
        )
    else:
        return
    
    # Random baseline
    print("\n🎲 Random Baseline:")
    random_rewards = []
    for ep in range(num_episodes):
        state, info = env.reset()
        episode_reward = 0
        done = False
        while not done:
            action = env.action_space.sample()  # Random action
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            episode_reward += reward
            state = next_state
        random_rewards.append(episode_reward)
        print(f"   Episode {ep+1}: Reward={episode_reward:.2f}")
    
    env.close()
    
    print(f"\n   Random Ortalama: {np.mean(random_rewards):.2f}")
    
    return random_rewards


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, 
                        default="experiments/checkpoints/bursa/dqn_episode_500.pt")
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--config", type=str, default="bursa")
    parser.add_argument("--compare", action="store_true", help="Baseline ile karşılaştır")
    
    args = parser.parse_args()
    
    # Model değerlendirmesi
    rewards, waiting = evaluate_model(args.checkpoint, args.config, args.episodes)
    
    # Baseline karşılaştırması
    if args.compare:
        random_rewards = compare_with_baseline(args.config, num_episodes=3)
        
        print("\n" + "=" * 60)
        print("📈 Karşılaştırma Özeti")
        print("=" * 60)
        if rewards and random_rewards:
            improvement = ((np.mean(random_rewards) - np.mean(rewards)) / abs(np.mean(random_rewards))) * 100
            print(f"   Random: {np.mean(random_rewards):.2f}")
            print(f"   DQN: {np.mean(rewards):.2f}")
            if improvement > 0:
                print(f"   ✅ İyileşme: %{improvement:.1f}")
            else:
                print(f"   ⚠️  Henüz iyileşme yok, daha fazla eğitim gerekebilir")
