"""
Multi-Agent Deep Deterministic Policy Gradient (MADDPG)

Implements MADDPG algorithm for multi-agent traffic signal control
with centralized training and decentralized execution.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Tuple, Optional
from collections import deque
import random


class Actor(nn.Module):
    """
    Actor network for MADDPG.
    
    Maps state to action (deterministic policy).
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: list = [128, 128],
    ):
        super(Actor, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, action_dim))
        layers.append(nn.Tanh())  # Actions normalized to [-1, 1]
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.network(state)


class Critic(nn.Module):
    """
    Critic network for MADDPG.
    
    Maps (all agents' states, all agents' actions) to Q-value.
    Used for centralized training.
    """
    
    def __init__(
        self,
        state_dims: List[int],
        action_dims: List[int],
        num_agents: int,
        hidden_dims: list = [128, 128],
    ):
        super(Critic, self).__init__()
        
        # Total input dimension: sum of all states + sum of all actions
        total_state_dim = sum(state_dims)
        total_action_dim = sum(action_dims)
        input_dim = total_state_dim + total_action_dim
        
        layers = []
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, 1))
        
        self.network = nn.Sequential(*layers)
    
    def forward(
        self,
        states: List[torch.Tensor],
        actions: List[torch.Tensor],
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            states: List of state tensors for each agent
            actions: List of action tensors for each agent
        """
        # Concatenate all states and actions
        state_cat = torch.cat(states, dim=1)
        action_cat = torch.cat(actions, dim=1)
        input_tensor = torch.cat([state_cat, action_cat], dim=1)
        
        return self.network(input_tensor)


class MADDPGAgent:
    """
    Single agent in MADDPG framework.
    
    Each agent has its own actor and critic networks.
    """
    
    def __init__(
        self,
        agent_id: str,
        state_dim: int,
        action_dim: int,
        lr_actor: float = 0.001,
        lr_critic: float = 0.001,
        gamma: float = 0.99,
        tau: float = 0.01,
        device: str = "cpu",
    ):
        """
        Initialize MADDPG agent.
        
        Args:
            agent_id: Unique identifier for agent
            state_dim: Dimension of agent's state space
            action_dim: Dimension of agent's action space
            lr_actor: Learning rate for actor
            lr_critic: Learning rate for critic
            gamma: Discount factor
            tau: Soft update coefficient for target networks
            device: Device to run on
        """
        self.agent_id = agent_id
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.tau = tau
        self.device = torch.device(device)
        
        # Actor networks
        self.actor = Actor(state_dim, action_dim).to(self.device)
        self.actor_target = Actor(state_dim, action_dim).to(self.device)
        self.actor_target.load_state_dict(self.actor.state_dict())
        
        # Critic network (will be initialized in MADDPG class)
        self.critic = None
        self.critic_target = None
        
        # Optimizers
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr_actor)
        self.critic_optimizer = None  # Will be set in MADDPG class
    
    def select_action(self, state: np.ndarray, noise: float = 0.0) -> np.ndarray:
        """
        Select action using actor network.
        
        Args:
            state: Current state
            noise: Noise scale for exploration
            
        Returns:
            action: Selected action
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            action = self.actor(state_tensor).cpu().numpy()[0]
            
            # Add noise for exploration
            if noise > 0:
                action += np.random.normal(0, noise, size=action.shape)
                action = np.clip(action, -1, 1)
        
        return action
    
    def soft_update(self):
        """Soft update target networks."""
        for target_param, param in zip(
            self.actor_target.parameters(), self.actor.parameters()
        ):
            target_param.data.copy_(
                self.tau * param.data + (1 - self.tau) * target_param.data
            )


class MADDPG:
    """
    Multi-Agent DDPG algorithm.
    
    Coordinates training of multiple agents with centralized critics.
    """
    
    def __init__(
        self,
        agent_ids: List[str],
        state_dims: Dict[str, int],
        action_dims: Dict[str, int],
        lr_actor: float = 0.001,
        lr_critic: float = 0.001,
        gamma: float = 0.99,
        tau: float = 0.01,
        device: str = "cpu",
    ):
        """
        Initialize MADDPG.
        
        Args:
            agent_ids: List of agent IDs
            state_dims: Dictionary mapping agent ID to state dimension
            action_dims: Dictionary mapping agent ID to action dimension
            lr_actor: Learning rate for actors
            lr_critic: Learning rate for critics
            gamma: Discount factor
            tau: Soft update coefficient
            device: Device to run on
        """
        self.agent_ids = agent_ids
        self.num_agents = len(agent_ids)
        self.gamma = gamma
        self.device = torch.device(device)
        
        # Create agents
        self.agents = {}
        for agent_id in agent_ids:
            self.agents[agent_id] = MADDPGAgent(
                agent_id,
                state_dims[agent_id],
                action_dims[agent_id],
                lr_actor,
                lr_critic,
                gamma,
                tau,
                device,
            )
        
        # Create centralized critics
        state_dim_list = [state_dims[aid] for aid in agent_ids]
        action_dim_list = [action_dims[aid] for aid in agent_ids]
        
        for agent_id in agent_ids:
            agent = self.agents[agent_id]
            agent.critic = Critic(
                state_dim_list, action_dim_list, self.num_agents
            ).to(self.device)
            agent.critic_target = Critic(
                state_dim_list, action_dim_list, self.num_agents
            ).to(self.device)
            agent.critic_target.load_state_dict(agent.critic.state_dict())
            agent.critic_optimizer = optim.Adam(
                agent.critic.parameters(), lr=lr_critic
            )
    
    def select_actions(
        self,
        states: Dict[str, np.ndarray],
        noise: float = 0.0,
    ) -> Dict[str, np.ndarray]:
        """
        Select actions for all agents.
        
        Args:
            states: Dictionary mapping agent ID to state
            noise: Noise scale for exploration
            
        Returns:
            actions: Dictionary mapping agent ID to action
        """
        actions = {}
        for agent_id, state in states.items():
            actions[agent_id] = self.agents[agent_id].select_action(state, noise)
        return actions
    
    def update(
        self,
        transitions: List[Tuple],
    ):
        """
        Update all agents using MADDPG algorithm.
        
        Args:
            transitions: List of (states, actions, rewards, next_states, dones)
                where each element is a dictionary mapping agent ID to value
        """
        # This is a simplified version - full implementation would
        # sample batches from replay buffer and update networks
        # For now, this is a placeholder structure
        pass
    
    def save(self, path: str):
        """Save all agent parameters."""
        checkpoint = {}
        for agent_id, agent in self.agents.items():
            checkpoint[agent_id] = {
                "actor": agent.actor.state_dict(),
                "actor_target": agent.actor_target.state_dict(),
                "critic": agent.critic.state_dict(),
                "critic_target": agent.critic_target.state_dict(),
            }
        torch.save(checkpoint, path)
    
    def load(self, path: str):
        """Load all agent parameters."""
        checkpoint = torch.load(path, map_location=self.device)
        for agent_id, agent in self.agents.items():
            if agent_id in checkpoint:
                agent.actor.load_state_dict(checkpoint[agent_id]["actor"])
                agent.actor_target.load_state_dict(checkpoint[agent_id]["actor_target"])
                agent.critic.load_state_dict(checkpoint[agent_id]["critic"])
                agent.critic_target.load_state_dict(
                    checkpoint[agent_id]["critic_target"]
                )
