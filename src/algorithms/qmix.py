"""
QMIX: Value Factorization for Multi-Agent Reinforcement Learning

Implements QMIX algorithm for multi-agent traffic signal control
with monotonic value factorization.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Tuple, Optional
from collections import deque
import random


class QNetwork(nn.Module):
    """
    Q-network for individual agents in QMIX.
    
    Maps (state, action) to Q-value.
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dims: list = [64, 64],
    ):
        super(QNetwork, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.network(state)


class MixingNetwork(nn.Module):
    """
    Mixing network for QMIX.
    
    Combines individual Q-values into joint Q-value
    while ensuring monotonicity constraint.
    """
    
    def __init__(
        self,
        num_agents: int,
        state_dim: int,
        hidden_dim: int = 64,
    ):
        """
        Initialize mixing network.
        
        Args:
            num_agents: Number of agents
            state_dim: Dimension of global state
            hidden_dim: Hidden dimension
        """
        super(MixingNetwork, self).__init__()
        
        self.num_agents = num_agents
        self.state_dim = state_dim
        
        # Hypernetworks for mixing weights
        self.hyper_w1 = nn.Linear(state_dim, num_agents * hidden_dim)
        self.hyper_w2 = nn.Linear(state_dim, hidden_dim)
        
        # Bias networks
        self.hyper_b1 = nn.Linear(state_dim, hidden_dim)
        self.hyper_b2 = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
    
    def forward(
        self,
        q_values: torch.Tensor,
        global_state: torch.Tensor,
    ) -> torch.Tensor:
        """
        Mix individual Q-values into joint Q-value.
        
        Args:
            q_values: Individual Q-values [batch, num_agents]
            global_state: Global state [batch, state_dim]
        """
        batch_size = q_values.size(0)
        
        # Generate mixing weights from global state
        w1 = torch.abs(self.hyper_w1(global_state))
        w1 = w1.view(batch_size, self.num_agents, -1)
        
        w2 = torch.abs(self.hyper_w2(global_state))
        w2 = w2.view(batch_size, 1, -1)
        
        b1 = self.hyper_b1(global_state)
        b1 = b1.view(batch_size, 1, -1)
        
        b2 = self.hyper_b2(global_state)
        
        # Mix Q-values
        q_values = q_values.view(batch_size, 1, -1)
        hidden = torch.bmm(q_values, w1) + b1
        hidden = torch.relu(hidden)
        q_total = torch.bmm(hidden, w2.transpose(1, 2)) + b2
        
        return q_total.squeeze()
    
    def forward_abs(self, q_values: torch.Tensor, global_state: torch.Tensor) -> torch.Tensor:
        """Forward pass ensuring monotonicity (absolute weights)."""
        return self.forward(q_values, global_state)


class QMIXAgent:
    """
    Single agent in QMIX framework.
    """
    
    def __init__(
        self,
        agent_id: str,
        state_dim: int,
        action_dim: int,
        lr: float = 0.0005,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.05,
        epsilon_decay: float = 0.99,
        device: str = "cpu",
    ):
        """
        Initialize QMIX agent.
        
        Args:
            agent_id: Unique identifier
            state_dim: State dimension
            action_dim: Action dimension
            lr: Learning rate
            gamma: Discount factor
            epsilon_start: Initial exploration rate
            epsilon_end: Final exploration rate
            epsilon_decay: Epsilon decay rate
            device: Device to run on
        """
        self.agent_id = agent_id
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.device = torch.device(device)
        
        # Q-network
        self.q_network = QNetwork(state_dim, action_dim).to(self.device)
        self.target_q_network = QNetwork(state_dim, action_dim).to(self.device)
        self.target_q_network.load_state_dict(self.q_network.state_dict())
        
        # Optimizer (will be set in QMIX class)
        self.optimizer = None
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Current state
            training: Whether in training mode
        """
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            action = q_values.argmax().item()
        
        return action
    
    def update_epsilon(self):
        """Decay epsilon."""
        self.epsilon = max(
            self.epsilon_end,
            self.epsilon * self.epsilon_decay
        )


class QMIX:
    """
    QMIX algorithm for multi-agent traffic signal control.
    """
    
    def __init__(
        self,
        agent_ids: List[str],
        state_dims: Dict[str, int],
        action_dims: Dict[str, int],
        global_state_dim: int,
        lr: float = 0.0005,
        gamma: float = 0.99,
        tau: float = 0.005,
        device: str = "cpu",
    ):
        """
        Initialize QMIX.
        
        Args:
            agent_ids: List of agent IDs
            state_dims: Dictionary mapping agent ID to state dimension
            action_dims: Dictionary mapping agent ID to action dimension
            global_state_dim: Dimension of global state
            lr: Learning rate
            gamma: Discount factor
            tau: Soft update coefficient
            device: Device to run on
        """
        self.agent_ids = agent_ids
        self.num_agents = len(agent_ids)
        self.global_state_dim = global_state_dim
        self.gamma = gamma
        self.tau = tau
        self.device = torch.device(device)
        
        # Create agents
        self.agents = {}
        for agent_id in agent_ids:
            agent = QMIXAgent(
                agent_id,
                state_dims[agent_id],
                action_dims[agent_id],
                lr,
                gamma,
                device=device,
            )
            agent.optimizer = optim.RMSprop(
                agent.q_network.parameters(), lr=lr, alpha=0.99, eps=1e-5
            )
            self.agents[agent_id] = agent
        
        # Mixing network
        self.mixing_network = MixingNetwork(
            self.num_agents, global_state_dim
        ).to(self.device)
        self.target_mixing_network = MixingNetwork(
            self.num_agents, global_state_dim
        ).to(self.device)
        self.target_mixing_network.load_state_dict(
            self.mixing_network.state_dict()
        )
        
        # Mixing network optimizer
        self.mixing_optimizer = optim.RMSprop(
            self.mixing_network.parameters(), lr=lr, alpha=0.99, eps=1e-5
        )
    
    def select_actions(
        self,
        states: Dict[str, np.ndarray],
        training: bool = True,
    ) -> Dict[str, int]:
        """
        Select actions for all agents.
        
        Args:
            states: Dictionary mapping agent ID to state
            training: Whether in training mode
        """
        actions = {}
        for agent_id, state in states.items():
            actions[agent_id] = self.agents[agent_id].select_action(state, training)
        return actions
    
    def update(
        self,
        batch: List[Tuple],
    ):
        """
        Update QMIX networks.
        
        Args:
            batch: List of transitions (states, actions, rewards, next_states, dones, global_states)
        """
        # This is a simplified placeholder
        # Full implementation would process batches and update networks
        pass
    
    def soft_update(self):
        """Soft update target networks."""
        for agent_id, agent in self.agents.items():
            for target_param, param in zip(
                agent.target_q_network.parameters(),
                agent.q_network.parameters(),
            ):
                target_param.data.copy_(
                    self.tau * param.data + (1 - self.tau) * target_param.data
                )
        
        for target_param, param in zip(
            self.target_mixing_network.parameters(),
            self.mixing_network.parameters(),
        ):
            target_param.data.copy_(
                self.tau * param.data + (1 - self.tau) * target_param.data
            )
    
    def save(self, path: str):
        """Save all parameters."""
        checkpoint = {
            "mixing_network": self.mixing_network.state_dict(),
            "target_mixing_network": self.target_mixing_network.state_dict(),
        }
        for agent_id, agent in self.agents.items():
            checkpoint[f"{agent_id}_q_network"] = agent.q_network.state_dict()
            checkpoint[f"{agent_id}_target_q_network"] = agent.target_q_network.state_dict()
        torch.save(checkpoint, path)
    
    def load(self, path: str):
        """Load all parameters."""
        checkpoint = torch.load(path, map_location=self.device)
        self.mixing_network.load_state_dict(checkpoint["mixing_network"])
        self.target_mixing_network.load_state_dict(checkpoint["target_mixing_network"])
        for agent_id, agent in self.agents.items():
            agent.q_network.load_state_dict(checkpoint[f"{agent_id}_q_network"])
            agent.target_q_network.load_state_dict(
                checkpoint[f"{agent_id}_target_q_network"]
            )
