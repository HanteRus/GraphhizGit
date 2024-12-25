import os
import subprocess
import json
import argparse

def get_git_commit_dependencies(repo_path, target_file):
    os.chdir(repo_path)
    result = subprocess.run(["git", "log", "--pretty=format:%H", "--", target_file], capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {result.stderr}")

    commits = result.stdout.splitlines()
    dependencies = {i + 1: commit for i, commit in enumerate(reversed(commits))}
    return dependencies

def generate_graphviz_code(dependencies):
    dot = ["digraph G {"]

    previous_node = None
    for order, commit in dependencies.items():
        current_node = f'"{order}: {commit}"'
        dot.append(f"    {current_node} [shape=box, style=filled, color=lightblue]")

        if previous_node:
            dot.append(f"    {previous_node} -> {current_node}")

        previous_node = current_node

    dot.append("}")
    return "\n".join(dot)

def save_graph_to_file(graph_code, output_path):
    with open(output_path, 'w') as file:
        file.write(graph_code)

def load_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

def main():
    parser = argparse.ArgumentParser(description="Visualize Git repository dependencies using Graphviz.")
    parser.add_argument("--config", required=True, help="Path to the configuration JSON file")

    args = parser.parse_args()

    try:
        config = load_config(args.config)
        graphviz_path = config["graphviz_path"]
        repo_path = config["repo_path"]
        output_path = config["output_path"]
        target_file = config["target_file"]

        dependencies = get_git_commit_dependencies(repo_path, target_file)
        graph_code = generate_graphviz_code(dependencies)
        save_graph_to_file(graph_code, output_path)

        print("Graphviz code saved to", output_path)
        print("Run the following command to visualize:")
        print(f"{graphviz_path} -Tpng {output_path} -o output.png")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()

#main.py --config config.json
#python main.py --config config.json