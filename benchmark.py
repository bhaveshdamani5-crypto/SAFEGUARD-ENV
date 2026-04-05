#!/usr/bin/env python3
"""
SafeGuard-Env Benchmarking Script
Generates comprehensive performance data for research evaluation
"""

import requests
import time
import json
import statistics
from typing import Dict, List, Tuple
import argparse

class BenchmarkRunner:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url
        self.results = {}

    def run_agent_evaluation(self, agent_type: str, level: int, trials: int = 5) -> Dict:
        """Run multiple trials of an agent type on a specific level"""
        scores = []
        costs = []
        times = []

        print(f"🔬 Benchmarking {agent_type} on Level {level} ({trials} trials)")

        for trial in range(trials):
            start_time = time.time()

            try:
                # Reset environment
                reset_response = requests.post(f"{self.base_url}/reset", json={"level": level})
                session_id = reset_response.json()["session_id"]

                # Run agent
                if agent_type == "optimal":
                    final_score, total_cost = self.run_optimal_agent(session_id)
                elif agent_type == "baseline":
                    final_score, total_cost = self.run_baseline_agent(session_id)
                elif agent_type == "random":
                    final_score, total_cost = self.run_random_agent(session_id)
                else:
                    raise ValueError(f"Unknown agent type: {agent_type}")

                elapsed = time.time() - start_time
                scores.append(final_score)
                costs.append(total_cost)
                times.append(elapsed)

                print(f"  Trial {trial+1}: F1={final_score:.2f}, Cost={total_cost:.2f}, Time={elapsed:.1f}s")

            except Exception as e:
                print(f"  Trial {trial+1} failed: {e}")
                continue

        if scores:
            return {
                "mean_f1": statistics.mean(scores),
                "std_f1": statistics.stdev(scores) if len(scores) > 1 else 0,
                "mean_cost": statistics.mean(costs),
                "std_cost": statistics.stdev(costs) if len(costs) > 1 else 0,
                "mean_time": statistics.mean(times),
                "trials_completed": len(scores),
                "success_rate": len(scores) / trials
            }
        else:
            return {"error": "All trials failed"}

    def run_optimal_agent(self, session_id: str) -> Tuple[float, float]:
        """Perfect agent that finds and redacts all real secrets"""
        total_reward = 0

        # Get initial state
        state_response = requests.get(f"{self.base_url}/state?session_id={session_id}")
        state = state_response.json()

        # Find all files with secrets
        secret_files = []
        for file_path, content in state["filesystem"].items():
            if "sk_live_" in content or "AKIA" in content or "SG." in content:
                secret_files.append(file_path)

        # Read and redact each file
        for file_path in secret_files:
            # Read file
            read_response = requests.post(f"{self.base_url}/step", json={
                "session_id": session_id,
                "tool_name": "read_file",
                "arguments": {"path": file_path}
            })
            total_reward += read_response.json()["reward"]

            # Extract and redact secrets
            content = read_response.json()["observation"]
            import re
            secrets = re.findall(r'(sk_live_[a-zA-Z0-9]+|AKIA[0-9A-Z]{16}|SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43})', content)

            for secret in secrets:
                redact_response = requests.post(f"{self.base_url}/step", json={
                    "session_id": session_id,
                    "tool_name": "redact_file",
                    "arguments": {"path": file_path, "secret": secret}
                })
                total_reward += redact_response.json()["reward"]

        # Get final grade
        grade_response = requests.post(f"{self.base_url}/grade", json={"session_id": session_id})
        grade = grade_response.json()

        return grade["score"], total_reward

    def run_baseline_agent(self, session_id: str) -> Tuple[float, float]:
        """Typical agent with realistic performance and some mistakes"""
        total_reward = 0

        # Explore root directory
        list_response = requests.post(f"{self.base_url}/step", json={
            "session_id": session_id,
            "tool_name": "list_directory",
            "arguments": {"path": "/"}
        })
        total_reward += list_response.json()["reward"]

        # Look in common directories
        dirs_to_check = [".env", "config", "secrets"]
        for dir_name in dirs_to_check:
            try:
                dir_response = requests.post(f"{self.base_url}/step", json={
                    "session_id": session_id,
                    "tool_name": "list_directory",
                    "arguments": {"path": f"/{dir_name}"}
                })
                total_reward += dir_response.json()["reward"]

                # Read some files
                files = dir_response.json()["observation"]
                for file in files[:2]:  # Read first 2 files
                    if not file.endswith("/"):
                        read_response = requests.post(f"{self.base_url}/step", json={
                            "session_id": session_id,
                            "tool_name": "read_file",
                            "arguments": {"path": file}
                        })
                        total_reward += read_response.json()["reward"]

                        # Try to find and redact secrets (with some mistakes)
                        content = read_response.json()["observation"]
                        import re
                        secrets = re.findall(r'(sk_live_[a-zA-Z0-9]+|AKIA[0-9A-Z]{16}|SG\.[a-zA-Z0-9_-]{43})', content)

                        for secret in secrets:
                            # 80% chance of correct redaction
                            if hash(secret + session_id) % 100 < 80:
                                redact_response = requests.post(f"{self.base_url}/step", json={
                                    "session_id": session_id,
                                    "tool_name": "redact_file",
                                    "arguments": {"path": file, "secret": secret}
                                })
                                total_reward += redact_response.json()["reward"]
            except:
                continue  # Directory might not exist

        # Get final grade
        grade_response = requests.post(f"{self.base_url}/grade", json={"session_id": session_id})
        grade = grade_response.json()

        return grade["score"], total_reward

    def run_random_agent(self, session_id: str) -> Tuple[float, float]:
        """Random agent for baseline comparison"""
        total_reward = 0
        actions_taken = 0

        # Take 10 random actions
        while actions_taken < 10:
            actions = [
                ("list_directory", {"path": "/"}),
                ("read_file", {"path": "/.env"}),
                ("read_file", {"path": "/config.json"}),
                ("search_filesystem", {"query": "secret"}),
                ("redact_file", {"path": "/.env", "secret": "sk_live_fake"})
            ]

            action, args = actions[hash(str(actions_taken) + session_id) % len(actions)]

            try:
                response = requests.post(f"{self.base_url}/step", json={
                    "session_id": session_id,
                    "tool_name": action,
                    "arguments": args
                })
                total_reward += response.json()["reward"]
                actions_taken += 1
            except:
                actions_taken += 1  # Count failed actions too

        # Get final grade
        grade_response = requests.post(f"{self.base_url}/grade", json={"session_id": session_id})
        grade = grade_response.json()

        return grade["score"], total_reward

    def run_full_benchmark(self, trials: int = 5) -> Dict:
        """Run comprehensive benchmark across all agent types and levels"""
        print("🚀 Starting SafeGuard-Env Comprehensive Benchmark")
        print("=" * 60)

        results = {}

        for level in [1, 2, 3]:
            print(f"\n📊 Level {level} Benchmarks")
            print("-" * 30)

            for agent_type in ["optimal", "baseline", "random"]:
                result = self.run_agent_evaluation(agent_type, level, trials)
                results[f"level_{level}_{agent_type}"] = result

        print("\n✅ Benchmark Complete")
        return results

    def save_results(self, results: Dict, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="SafeGuard-Env Benchmarking Tool")
    parser.add_argument("--url", default="http://localhost:7860", help="Base URL of the environment")
    parser.add_argument("--trials", type=int, default=5, help="Number of trials per benchmark")
    parser.add_argument("--output", default="benchmark_results.json", help="Output file for results")

    args = parser.parse_args()

    # Check if server is running
    try:
        response = requests.get(f"{args.url}/", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start the server first: python main.py")
            return
    except:
        print("❌ Cannot connect to server. Please start the server first: python main.py")
        return

    # Run benchmark
    runner = BenchmarkRunner(args.url)
    results = runner.run_full_benchmark(args.trials)
    runner.save_results(results, args.output)

    # Print summary
    print("\n📈 Benchmark Summary:")
    print("-" * 40)
    for key, result in results.items():
        if "error" not in result:
            print(f"{key}: F1={result['mean_f1']:.2f}±{result['std_f1']:.2f}, "
                  f"Cost={result['mean_cost']:.2f}±{result['std_cost']:.2f}")

if __name__ == "__main__":
    main()