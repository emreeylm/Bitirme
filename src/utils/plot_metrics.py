"""
Eğitim metriklerini görselleştir
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import os


def load_training_results(results_file: str) -> Dict:
    """Eğitim sonuçlarını yükle"""
    with open(results_file, 'r') as f:
        return json.load(f)


def plot_training_metrics(results_file: str, save_path: str = None):
    """Eğitim metriklerini çiz"""
    
    results = load_training_results(results_file)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    # 1. Rewards
    axes[0].plot(results["rewards"], alpha=0.6, label="Episode Reward")
    if len(results["rewards"]) > 10:
        window = min(50, len(results["rewards"]) // 10)
        moving_avg = np.convolve(
            results["rewards"], np.ones(window) / window, mode="valid"
        )
        axes[0].plot(
            range(window - 1, len(results["rewards"])),
            moving_avg,
            label=f"Moving Avg ({window})",
            linewidth=2,
        )
    axes[0].set_xlabel("Episode")
    axes[0].set_ylabel("Reward")
    axes[0].set_title("Training Rewards")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 2. Waiting Time
    if results["metrics"]["waiting_time"]:
        axes[1].plot(results["metrics"]["waiting_time"], alpha=0.6, color='orange')
        axes[1].set_xlabel("Episode")
        axes[1].set_ylabel("Ortalama Bekleme Süresi (s)")
        axes[1].set_title("Bekleme Süresi")
        axes[1].grid(True, alpha=0.3)
    
    # 3. Queue Length
    if results["metrics"]["queue_length"]:
        axes[2].plot(results["metrics"]["queue_length"], alpha=0.6, color='red')
        axes[2].set_xlabel("Episode")
        axes[2].set_ylabel("Kuyruk Uzunluğu")
        axes[2].set_title("Kuyruk Uzunluğu")
        axes[2].grid(True, alpha=0.3)
    
    # 4. Stops
    if results["metrics"]["stops"]:
        axes[3].plot(results["metrics"]["stops"], alpha=0.6, color='purple')
        axes[3].set_xlabel("Episode")
        axes[3].set_ylabel("Duruş Sayısı")
        axes[3].set_title("Duruş Sayısı")
        axes[3].grid(True, alpha=0.3)
    
    # 5. Throughput
    if results["metrics"]["throughput"]:
        axes[4].plot(results["metrics"]["throughput"], alpha=0.6, color='green')
        axes[4].set_xlabel("Episode")
        axes[4].set_ylabel("Akış (Araç)")
        axes[4].set_title("Throughput")
        axes[4].grid(True, alpha=0.3)
    
    # 6. Delay
    if results["metrics"]["delay"]:
        axes[5].plot(results["metrics"]["delay"], alpha=0.6, color='brown')
        axes[5].set_xlabel("Episode")
        axes[5].set_ylabel("Gecikme (s)")
        axes[5].set_title("Gecikme")
        axes[5].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"✅ Grafik kaydedildi: {save_path}")
    else:
        plt.show()
    
    plt.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=str, required=True,
                        help="Training results JSON file")
    parser.add_argument("--output", type=str, default=None,
                        help="Output image path")
    
    args = parser.parse_args()
    
    plot_training_metrics(args.results, args.output)
