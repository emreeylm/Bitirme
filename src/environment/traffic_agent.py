"""
Traffic Agent Definition

This module defines the agent interface for traffic signal control,
including state, action, and reward specifications.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class AgentState:
    """
    State representation for a traffic signal agent.
    
    Attributes:
        queue_lengths: Queue length per incoming lane (normalized)
        waiting_times: Accumulated waiting time per lane (normalized)
        vehicle_counts: Number of vehicles per lane (normalized)
        current_phase: Current traffic light phase (one-hot or index)
        phase_duration: Time since last phase change (normalized)
        neighbor_states: States from neighboring intersections (optional)
    """
    queue_lengths: np.ndarray
    waiting_times: np.ndarray
    vehicle_counts: np.ndarray
    current_phase: int
    phase_duration: float
    neighbor_states: Optional[List[np.ndarray]] = None
    
    def to_vector(self) -> np.ndarray:
        """Convert state to feature vector."""
        features = [
            self.queue_lengths,
            self.waiting_times,
            self.vehicle_counts,
            np.array([self.current_phase / 4.0]),  # Normalized phase
            np.array([self.phase_duration]),
        ]
        
        if self.neighbor_states:
            # Concatenate neighbor states (flattened)
            neighbor_features = np.concatenate(self.neighbor_states)
            features.append(neighbor_features)
        
        return np.concatenate(features).astype(np.float32)


@dataclass
class AgentAction:
    """
    Action representation for a traffic signal agent.
    
    Attributes:
        phase: Phase index to switch to (0 to num_phases-1)
        duration: Optional duration for the phase (if using variable timing)
    """
    phase: int
    duration: Optional[int] = None
    
    def __post_init__(self):
        """Validate action."""
        if self.phase < 0 or self.phase >= 4:  # Assuming 4 phases
            raise ValueError(f"Invalid phase: {self.phase}")


class RewardFunction:
    """
    Reward function for traffic signal control.
    
    Combines multiple traffic metrics into a single reward signal.
    """
    
    def __init__(
        self,
        waiting_time_weight: float = 0.1,
        queue_length_weight: float = 0.1,
        stop_count_weight: float = 0.05,
        delay_weight: float = 0.1,
        throughput_weight: float = 0.05,
    ):
        """
        Initialize reward function with weights.
        
        Args:
            waiting_time_weight: Weight for waiting time penalty
            queue_length_weight: Weight for queue length penalty
            stop_count_weight: Weight for stop count penalty
            delay_weight: Weight for delay penalty
            throughput_weight: Weight for throughput reward (positive)
        """
        self.waiting_time_weight = waiting_time_weight
        self.queue_length_weight = queue_length_weight
        self.stop_count_weight = stop_count_weight
        self.delay_weight = delay_weight
        self.throughput_weight = throughput_weight
    
    def calculate(
        self,
        waiting_times: np.ndarray,
        queue_lengths: np.ndarray,
        stop_counts: np.ndarray,
        delays: np.ndarray,
        throughput: float,
    ) -> float:
        """
        Calculate reward from traffic metrics.
        
        Args:
            waiting_times: Waiting times per lane
            queue_lengths: Queue lengths per lane
            stop_counts: Number of stops per lane
            delays: Delays per lane
            throughput: Number of vehicles passed through
            
        Returns:
            reward: Scalar reward value
        """
        # Penalties (negative)
        waiting_penalty = self.waiting_time_weight * np.sum(waiting_times)
        queue_penalty = self.queue_length_weight * np.sum(queue_lengths)
        stop_penalty = self.stop_count_weight * np.sum(stop_counts)
        delay_penalty = self.delay_weight * np.sum(delays)
        
        # Reward (positive)
        throughput_reward = self.throughput_weight * throughput
        
        # Total reward
        reward = throughput_reward - (
            waiting_penalty + queue_penalty + stop_penalty + delay_penalty
        )
        
        return reward


class MultiAgentState:
    """
    State representation for multi-agent scenarios.
    
    Combines states from multiple agents (intersections).
    """
    
    def __init__(self, agent_states: Dict[str, AgentState]):
        """
        Initialize multi-agent state.
        
        Args:
            agent_states: Dictionary mapping agent ID to AgentState
        """
        self.agent_states = agent_states
    
    def get_agent_state(self, agent_id: str) -> AgentState:
        """Get state for a specific agent."""
        return self.agent_states[agent_id]
    
    def get_neighbor_states(
        self,
        agent_id: str,
        neighbor_ids: List[str]
    ) -> List[np.ndarray]:
        """Get states from neighboring agents."""
        neighbor_states = []
        for neighbor_id in neighbor_ids:
            if neighbor_id in self.agent_states:
                neighbor_state = self.agent_states[neighbor_id]
                neighbor_states.append(neighbor_state.to_vector())
        return neighbor_states
