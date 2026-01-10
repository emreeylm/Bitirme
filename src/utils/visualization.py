"""
Visualization utilities for training and evaluation results.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
import seaborn as sns

sns.set_style("whitegrid")


def plot_training_curves(
    rewards: List[float],
    losses: Optional[List[float]] = None,
    save_path: Optional[str] = None,
):
    """
    Plot training curves for rewards and losses.
    
    Args:
        rewards: List of episode rewards
        losses: Optional list of episode losses
        save_path: Path to save the plot
    """
    fig, axes = plt.subplots(1, 2 if losses else 1, figsize=(12, 4))
    
    if not isinstance(axes, np.ndarray):
        axes = [axes]
    
    # Plot rewards
    axes[0].plot(rewards, alpha=0.6, label="Episode Reward")
    if len(rewards) > 10:
        # Moving average
        window = min(50, len(rewards) // 10)
        moving_avg = np.convolve(
            rewards, np.ones(window) / window, mode="valid"
        )
        axes[0].plot(
            range(window - 1, len(rewards)),
            moving_avg,
            label=f"Moving Average ({window})",
            linewidth=2,
        )
    axes[0].set_xlabel("Episode")
    axes[0].set_ylabel("Reward")
    axes[0].set_title("Training Rewards")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot losses if provided
    if losses and len(axes) > 1:
        axes[1].plot(losses, alpha=0.6, label="Episode Loss")
        if len(losses) > 10:
            window = min(50, len(losses) // 10)
            moving_avg = np.convolve(
                losses, np.ones(window) / window, mode="valid"
            )
            axes[1].plot(
                range(window - 1, len(losses)),
                moving_avg,
                label=f"Moving Average ({window})",
                linewidth=2,
            )
        axes[1].set_xlabel("Episode")
        axes[1].set_ylabel("Loss")
        axes[1].set_title("Training Losses")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()
    
    plt.close()


def plot_traffic_metrics(
    metrics: Dict[str, List[float]],
    save_path: Optional[str] = None,
):
    """
    Plot traffic performance metrics.
    
    Args:
        metrics: Dictionary mapping metric name to list of values
        save_path: Path to save the plot
    """
    num_metrics = len(metrics)
    cols = min(3, num_metrics)
    rows = (num_metrics + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    
    if num_metrics == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if isinstance(axes, np.ndarray) else [axes]
    else:
        axes = axes.flatten()
    
    for idx, (metric_name, values) in enumerate(metrics.items()):
        ax = axes[idx] if num_metrics > 1 else axes[0]
        ax.plot(values, alpha=0.7)
        ax.set_xlabel("Time Step")
        ax.set_ylabel(metric_name)
        ax.set_title(f"{metric_name} Over Time")
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(num_metrics, len(axes)):
        axes[idx].axis("off")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()
    
    plt.close()


def plot_comparison(
    results: Dict[str, Dict[str, float]],
    save_path: Optional[str] = None,
):
    """
    Plot comparison of different algorithms/baselines.
    
    Args:
        results: Dictionary mapping algorithm name to metrics dictionary
        save_path: Path to save the plot
    """
    metrics = list(next(iter(results.values())).keys())
    algorithms = list(results.keys())
    
    num_metrics = len(metrics)
    cols = min(3, num_metrics)
    rows = (num_metrics + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    
    if num_metrics == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if isinstance(axes, np.ndarray) else [axes]
    else:
        axes = axes.flatten()
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx] if num_metrics > 1 else axes[0]
        values = [results[alg][metric] for alg in algorithms]
        bars = ax.bar(algorithms, values, alpha=0.7)
        ax.set_ylabel(metric)
        ax.set_title(f"{metric} Comparison")
        ax.grid(True, alpha=0.3, axis="y")
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.2f}",
                ha="center",
                va="bottom",
            )
    
    # Hide unused subplots
    for idx in range(num_metrics, len(axes)):
        axes[idx].axis("off")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()
    
    plt.close()
