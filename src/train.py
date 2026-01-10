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
    
    for episode in range(num_episodes):
        state, info = env.reset()
        episode_reward = 0
        episode_losses = []
        
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
            
            if done:
                break
        
        # Update epsilon
        agent.update_epsilon()
        
        # Logging
        avg_loss = np.mean(episode_losses) if episode_losses else 0.0
        rewards_history.append(episode_reward)
        losses_history.append(avg_loss)
        
        if (episode + 1) % 10 == 0:
            print(
                f"Episode {episode + 1}/{num_episodes} | "
                f"Reward: {episode_reward:.2f} | "
                f"Loss: {avg_loss:.4f} | "
                f"Epsilon: {agent.epsilon:.3f}"
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
    return agent, rewards_history, losses_history


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
        agent, rewards, losses = train_dqn(env, config)
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
