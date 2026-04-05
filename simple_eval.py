#!/usr/bin/env python3
"""
Simple evaluation script for SafeGuard-Env
Demonstrates basic RL environment functionality without complex setup
"""

import requests
import json
import time

def evaluate_level(level: int, max_steps: int = 10):
    """Simple evaluation of a single level"""
    print(f"\n{'='*50}")
    print(f"EVALUATING LEVEL {level}")
    print(f"{'='*50}")

    # Reset environment
    try:
        reset_response = requests.post(f"http://localhost:7860/reset?level={level}", timeout=5)
        reset_response.raise_for_status()
        obs = reset_response.json()
        session_id = obs.get("session_id", "default")

        print(f"Task: {obs['task_description']}")
        print(f"Initial state: {obs['tool_output']}")

        total_reward = 0
        steps_taken = 0

        # Simple hardcoded strategy for demonstration
        actions = [
            {"tool_name": "list_directory", "arguments": {"path": "/"}},
            {"tool_name": "read_file", "arguments": {"path": "/.env"}},
            {"tool_name": "redact_file", "arguments": {"path": "/.env", "secret": "sk_live_51Mabcde12345", "replacement": "***"}},
            {"tool_name": "submit", "arguments": {}}
        ]

        for i, action in enumerate(actions[:max_steps]):
            if steps_taken >= max_steps:
                break

            action_payload = {
                "session_id": session_id,
                "tool_name": action["tool_name"],
                "arguments": action["arguments"]
            }

            try:
                step_response = requests.post("http://localhost:7860/step",
                    json=action_payload, timeout=5)
                step_response.raise_for_status()
                result = step_response.json()

                reward = result["reward"]
                done = result["done"]
                tool_output = result["observation"]["tool_output"]

                total_reward += reward
                steps_taken += 1

                print(f"Step {i+1}: {action['tool_name']} -> Reward: {reward:.2f}")
                print(f"  Output: {tool_output[:100]}{'...' if len(tool_output) > 100 else ''}")

                if done:
                    # Get final grade
                    grade_response = requests.post(f"http://localhost:7860/grade?session_id={session_id}", timeout=5)
                    if grade_response.status_code == 200:
                        grade = grade_response.json()
                        print("Final Grade:")
                        print(f"  Precision: {grade['precision']:.2f}")
                        print(f"  Recall: {grade['recall']:.2f}")
                        print(f"  F1 Score: {grade['score']:.2f}")
                        print(f"  Total Reward: {total_reward:.2f}")
                    break

            except requests.exceptions.RequestException as e:
                print(f"Error in step {i+1}: {e}")
                break

        return total_reward

    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to environment: {e}")
        print("Make sure the server is running with: python main.py")
        return 0

def main():
    """Main evaluation function"""
    print("SafeGuard-Env Simple Evaluation")
    print("================================")

    # Check if server is running
    try:
        response = requests.get("http://localhost:7860/", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Start with: python main.py")
            return
    except:
        print("❌ Cannot connect to server. Start with: python main.py")
        return

    print("✅ Server is running")

    # Evaluate each level
    results = {}
    for level in [1, 2]:
        try:
            score = evaluate_level(level)
            results[level] = score
        except Exception as e:
            print(f"❌ Error evaluating level {level}: {e}")
            results[level] = 0

    # Summary
    print(f"\n{'='*50}")
    print("EVALUATION SUMMARY")
    print(f"{'='*50}")

    total_score = sum(results.values())
    print(f"Total evaluation score: {total_score:.2f}")

    if total_score > 1.0:
        print("✅ Environment working correctly!")
    else:
        print("⚠️  Environment may need tuning")

    print("\nNext steps:")
    print("1. Try level 3 for procedural generation")
    print("2. Run full evaluation: ./run_demo.sh")
    print("3. Check API docs: http://localhost:7860/docs")

if __name__ == "__main__":
    main()