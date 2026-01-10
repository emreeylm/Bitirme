"""
Metrics calculation utilities for traffic simulation evaluation.
"""

import numpy as np
from typing import Dict, List, Optional
import traci


def calculate_metrics(
    traffic_lights: List[str],
    include_emissions: bool = True,
) -> Dict[str, float]:
    """
    Calculate traffic performance metrics from SUMO simulation.
    
    Args:
        traffic_lights: List of traffic light IDs
        include_emissions: Whether to include emission metrics
        
    Returns:
        Dictionary of metric names to values
    """
    metrics = {}
    
    # Initialize accumulators
    total_waiting_time = 0.0
    total_queue_length = 0.0
    total_stops = 0
    total_delay = 0.0
    total_vehicles = 0
    
    for tl_id in traffic_lights:
        controlled_lanes = traci.trafficlight.getControlledLanes(tl_id)
        
        for lane in controlled_lanes:
            # Waiting time
            waiting_time = traci.lane.getWaitingTime(lane)
            total_waiting_time += waiting_time
            
            # Queue length (halting vehicles)
            queue_length = traci.lane.getLastStepHaltingNumber(lane)
            total_queue_length += queue_length
            
            # Stops
            stops = traci.lane.getLastStepHaltingNumber(lane)
            total_stops += stops
            
            # Vehicle count
            vehicle_count = traci.lane.getLastStepVehicleNumber(lane)
            total_vehicles += vehicle_count
            
            # Delay (simplified)
            mean_speed = traci.lane.getLastStepMeanSpeed(lane)
            if mean_speed > 0:
                # Delay = time to travel at desired speed - actual time
                # Simplified calculation
                delay = max(0, (traci.lane.getLength(lane) / mean_speed) - 
                           (traci.lane.getLength(lane) / traci.lane.getMaxSpeed(lane)))
                total_delay += delay * vehicle_count
    
    # Average metrics
    if total_vehicles > 0:
        metrics["avg_waiting_time"] = total_waiting_time / total_vehicles
        metrics["avg_queue_length"] = total_queue_length / len(traffic_lights)
        metrics["avg_stops"] = total_stops / total_vehicles
        metrics["avg_delay"] = total_delay / total_vehicles
    else:
        metrics["avg_waiting_time"] = 0.0
        metrics["avg_queue_length"] = 0.0
        metrics["avg_stops"] = 0.0
        metrics["avg_delay"] = 0.0
    
    # Throughput
    metrics["throughput"] = total_vehicles
    
    # Emission metrics (if available)
    if include_emissions:
        try:
            total_fuel = 0.0
            total_co2 = 0.0
            
            vehicle_ids = traci.vehicle.getIDList()
            for veh_id in vehicle_ids:
                try:
                    fuel = traci.vehicle.getFuelConsumption(veh_id)
                    co2 = traci.vehicle.getCO2Emission(veh_id)
                    total_fuel += fuel
                    total_co2 += co2
                except:
                    pass
            
            metrics["total_fuel_consumption"] = total_fuel
            metrics["total_co2_emission"] = total_co2
            
            if len(vehicle_ids) > 0:
                metrics["avg_fuel_per_vehicle"] = total_fuel / len(vehicle_ids)
                metrics["avg_co2_per_vehicle"] = total_co2 / len(vehicle_ids)
            else:
                metrics["avg_fuel_per_vehicle"] = 0.0
                metrics["avg_co2_per_vehicle"] = 0.0
        except:
            metrics["total_fuel_consumption"] = 0.0
            metrics["total_co2_emission"] = 0.0
            metrics["avg_fuel_per_vehicle"] = 0.0
            metrics["avg_co2_per_vehicle"] = 0.0
    
    return metrics


def compare_baselines(
    rl_metrics: Dict[str, float],
    baseline_metrics: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    """
    Compare RL agent metrics with baseline methods.
    
    Args:
        rl_metrics: Metrics from RL agent
        baseline_metrics: Dictionary mapping baseline name to metrics
        
    Returns:
        Dictionary with improvement percentages
    """
    improvements = {}
    
    for baseline_name, baseline_vals in baseline_metrics.items():
        improvements[baseline_name] = {}
        
        for metric_name, rl_value in rl_metrics.items():
            if metric_name in baseline_vals:
                baseline_value = baseline_vals[metric_name]
                
                # Calculate improvement percentage
                # For metrics where lower is better (waiting time, delay, etc.)
                if baseline_value > 0:
                    if "waiting" in metric_name or "delay" in metric_name or \
                       "queue" in metric_name or "stop" in metric_name or \
                       "fuel" in metric_name or "co2" in metric_name:
                        improvement = (
                            (baseline_value - rl_value) / baseline_value * 100
                        )
                    else:  # For metrics where higher is better (throughput)
                        improvement = (
                            (rl_value - baseline_value) / baseline_value * 100
                        )
                else:
                    improvement = 0.0
                
                improvements[baseline_name][metric_name] = improvement
    
    return improvements
