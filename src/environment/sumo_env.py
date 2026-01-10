"""
SUMO-TraCI Environment for Traffic Signal Control

This module provides a Gym-like interface for SUMO traffic simulation,
enabling reinforcement learning agents to interact with traffic scenarios.
"""

import os
import sys
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from gymnasium import Env, spaces
import traci
from traci import constants


class SumoEnvironment(Env):
    """
    SUMO-based traffic simulation environment for RL agents.
    
    This environment wraps SUMO's TraCI interface to provide a standard
    Gymnasium environment for training traffic signal control agents.
    """
    
    def __init__(
        self,
        sumo_cfg: str,
        net_file: str,
        route_file: str,
        use_gui: bool = False,
        num_seconds: int = 3600,
        yellow_time: int = 3,
        min_green_time: int = 10,
        max_green_time: int = 60,
        delta_time: int = 5,
    ):
        """
        Initialize SUMO environment.
        
        Args:
            sumo_cfg: Path to SUMO configuration file (.sumocfg)
            net_file: Path to SUMO network file (.net.xml)
            route_file: Path to SUMO route file (.rou.xml)
            use_gui: Whether to use SUMO GUI
            num_seconds: Simulation duration in seconds
            yellow_time: Yellow phase duration in seconds
            min_green_time: Minimum green phase duration
            max_green_time: Maximum green phase duration
            delta_time: Time step for agent actions
        """
        super().__init__()
        
        self.sumo_cfg = sumo_cfg
        self.net_file = net_file
        self.route_file = route_file
        self.use_gui = use_gui
        self.num_seconds = num_seconds
        self.yellow_time = yellow_time
        self.min_green_time = min_green_time
        self.max_green_time = max_green_time
        self.delta_time = delta_time
        
        # SUMO binary path
        if "SUMO_HOME" in os.environ:
            tools = os.path.join(os.environ["SUMO_HOME"], "tools")
            sys.path.append(tools)
        else:
            raise ValueError("SUMO_HOME environment variable not set!")
        
        # Get traffic lights by briefly starting SUMO
        self.traffic_lights = self._init_traffic_lights()
        self.num_tls = len(self.traffic_lights)
        
        # Define observation and action spaces
        # Observation: queue lengths, waiting times, phase info for each lane
        # Action: phase selection (discrete)
        self.observation_space = self._get_observation_space()
        self.action_space = self._get_action_space()
        
        # State variables
        self.current_step = 0
        self.last_action = None
        self.last_phase_time = 0
        
    def _init_traffic_lights(self) -> List[str]:
        """Get list of all traffic light IDs by briefly starting SUMO."""
        try:
            # Start SUMO briefly to get traffic light info
            sumo_binary = "sumo-gui" if self.use_gui else "sumo"
            
            # Save current directory and change to config directory
            original_dir = os.getcwd()
            config_dir = os.path.dirname(os.path.abspath(self.sumo_cfg))
            config_name = os.path.basename(self.sumo_cfg)
            os.chdir(config_dir)
            
            traci.start([
                sumo_binary,
                "-c", config_name,
                "--no-step-log",
                "--no-warnings",
            ])
            
            tl_ids = list(traci.trafficlight.getIDList())
            traci.close()
            os.chdir(original_dir)
            
            return tl_ids
        except Exception as e:
            print(f"Warning: Could not get traffic lights: {e}")
            return []
    
    def _get_observation_space(self) -> spaces.Box:
        """
        Define observation space.
        
        For each traffic light, we observe:
        - Queue lengths per lane (normalized)
        - Waiting times per lane (normalized)
        - Current phase
        - Time since last phase change
        - Number of vehicles per lane
        """
        # Example: 4 phases, 4 incoming lanes per TL
        # [queue_lengths (4), waiting_times (4), phase (1), phase_time (1), vehicle_count (4)]
        obs_dim = 4 + 4 + 1 + 1 + 4  # 14 dimensions per TL
        return spaces.Box(
            low=0.0,
            high=1.0,
            shape=(self.num_tls, obs_dim),
            dtype=np.float32
        )
    
    def _get_action_space(self) -> spaces.Discrete:
        """
        Define action space.
        
        Actions: Select next phase (0 to num_phases-1)
        """
        # Assuming 4 phases per traffic light
        return spaces.Discrete(4)
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict]:
        """
        Reset the environment to initial state.
        
        Returns:
            observation: Initial observation
            info: Additional information
        """
        super().reset(seed=seed)
        
        # Close existing SUMO connection if any
        try:
            traci.close()
        except:
            pass
        
        # Start SUMO
        sumo_binary = "sumo-gui" if self.use_gui else "sumo"
        traci.start([
            sumo_binary,
            "-c", self.sumo_cfg,
            "--no-step-log",
            "--no-warnings",
            "--quit-on-end",
        ])
        
        # Get traffic lights
        self.traffic_lights = list(traci.trafficlight.getIDList())
        self.num_tls = len(self.traffic_lights)
        
        # Reset state variables
        self.current_step = 0
        self.last_action = None
        self.last_phase_time = 0
        
        # Get initial observation
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Execute one step in the environment.
        
        Args:
            action: Action to take (phase selection)
            
        Returns:
            observation: Next observation
            reward: Reward for this step
            terminated: Whether episode ended
            truncated: Whether episode was truncated
            info: Additional information
        """
        # Apply action (change traffic light phase)
        self._apply_action(action)
        
        # Simulate for delta_time seconds
        for _ in range(self.delta_time):
            traci.simulationStep()
            self.current_step += 1
        
        # Get observation and reward
        observation = self._get_observation()
        reward = self._calculate_reward()
        terminated = self.current_step >= self.num_seconds
        truncated = False
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def _apply_action(self, action: int):
        """Apply action to traffic lights."""
        # For multi-agent: action is a dict mapping TL ID to phase
        # For single-agent: action is phase index
        if isinstance(action, dict):
            for tl_id, phase in action.items():
                if tl_id in self.traffic_lights:
                    self._set_phase(tl_id, phase)
        else:
            # Single agent: apply to first traffic light
            if self.traffic_lights:
                self._set_phase(self.traffic_lights[0], action)
    
    def _set_phase(self, tl_id: str, phase: int):
        """Set traffic light phase."""
        # Get current phase
        current_phase = traci.trafficlight.getPhase(tl_id)
        
        # If phase changed, ensure yellow phase transition
        if current_phase != phase:
            # Set yellow phase first (if needed)
            if current_phase % 2 == 0:  # Currently green
                yellow_phase = current_phase + 1
                traci.trafficlight.setPhase(tl_id, yellow_phase)
                # Wait for yellow time (handled in step)
            
            # Set new phase
            traci.trafficlight.setPhase(tl_id, phase)
            self.last_phase_time = 0
        else:
            self.last_phase_time += self.delta_time
    
    def _get_observation(self) -> np.ndarray:
        """
        Get current observation from environment.
        
        Returns:
            observation: Array of observations for each traffic light
        """
        observations = []
        
        for tl_id in self.traffic_lights:
            obs = self._get_tl_observation(tl_id)
            observations.append(obs)
        
        return np.array(observations, dtype=np.float32)
    
    def _get_tl_observation(self, tl_id: str) -> np.ndarray:
        """
        Get observation for a single traffic light.
        
        Returns:
            observation: Normalized observation vector
        """
        # Get controlled lanes
        controlled_lanes = traci.trafficlight.getControlledLanes(tl_id)
        
        # Initialize observation components
        queue_lengths = []
        waiting_times = []
        vehicle_counts = []
        
        for lane in controlled_lanes:
            # Queue length (vehicles with speed < 0.1 m/s)
            vehicles = traci.lane.getLastStepVehicleIDs(lane)
            queue = sum(1 for v in vehicles if traci.vehicle.getSpeed(v) < 0.1)
            queue_lengths.append(min(queue / 20.0, 1.0))  # Normalize to [0, 1]
            
            # Waiting time (accumulated waiting time)
            waiting_time = traci.lane.getWaitingTime(lane)
            waiting_times.append(min(waiting_time / 100.0, 1.0))  # Normalize
            
            # Vehicle count
            vehicle_count = traci.lane.getLastStepVehicleNumber(lane)
            vehicle_counts.append(min(vehicle_count / 30.0, 1.0))  # Normalize
        
        # Pad or truncate to fixed size (4 lanes)
        while len(queue_lengths) < 4:
            queue_lengths.append(0.0)
            waiting_times.append(0.0)
            vehicle_counts.append(0.0)
        
        queue_lengths = queue_lengths[:4]
        waiting_times = waiting_times[:4]
        vehicle_counts = vehicle_counts[:4]
        
        # Current phase (one-hot encoded, normalized)
        current_phase = traci.trafficlight.getPhase(tl_id)
        phase_normalized = current_phase / 4.0  # Assuming 4 phases
        
        # Time since last phase change (normalized)
        phase_time_normalized = min(self.last_phase_time / 60.0, 1.0)
        
        # Concatenate all features
        observation = np.array(
            queue_lengths + waiting_times + [phase_normalized] + 
            [phase_time_normalized] + vehicle_counts,
            dtype=np.float32
        )
        
        return observation
    
    def _calculate_reward(self) -> float:
        """
        Calculate reward based on traffic metrics.
        
        Reward function combines:
        - Negative waiting time (minimize)
        - Negative queue length (minimize)
        - Negative number of stops (minimize)
        - Positive throughput (maximize)
        """
        total_waiting_time = 0.0
        total_queue_length = 0.0
        total_stops = 0
        total_vehicles = 0
        
        for tl_id in self.traffic_lights:
            controlled_lanes = traci.trafficlight.getControlledLanes(tl_id)
            
            for lane in controlled_lanes:
                waiting_time = traci.lane.getWaitingTime(lane)
                queue_length = traci.lane.getLastStepHaltingNumber(lane)
                vehicle_count = traci.lane.getLastStepVehicleNumber(lane)
                
                total_waiting_time += waiting_time
                total_queue_length += queue_length
                total_stops += queue_length  # Halting vehicles count as stops
                total_vehicles += vehicle_count
        
        # Normalize by number of traffic lights to make reward scale consistent
        num_tls = max(len(self.traffic_lights), 1)
        
        # Normalized penalties (per traffic light)
        avg_waiting = total_waiting_time / num_tls
        avg_queue = total_queue_length / num_tls
        avg_stops = total_stops / num_tls
        
        # Throughput reward (vehicles passed through)
        throughput_reward = total_vehicles * 0.01
        
        # Reward = throughput - penalties (normalized)
        reward = throughput_reward - (
            0.01 * avg_waiting +
            0.01 * avg_queue +
            0.005 * avg_stops
        )
        
        return reward
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional information about current state."""
        info = {
            "step": self.current_step,
            "traffic_lights": self.traffic_lights,
        }
        
        # Add traffic metrics
        total_waiting = sum(
            traci.lane.getWaitingTime(lane)
            for tl_id in self.traffic_lights
            for lane in traci.trafficlight.getControlledLanes(tl_id)
        )
        info["total_waiting_time"] = total_waiting
        
        return info
    
    def close(self):
        """Close SUMO connection."""
        try:
            traci.close()
        except:
            pass
    
    def render(self, mode: str = "human"):
        """Render the environment (SUMO GUI handles this)."""
        pass
