import os
import requests
import urllib.parse
from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def get_public_repos(username):
    """
    Fetches the public repositories of a GitHub user.
    """
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            repos.extend(data)
            page += 1
        else:
            print(f"Failed to fetch repositories: {response.status_code}")
            return None
    return repos

def generate_skills_graph(repos):
    """
    Generates an image of a skills graph from repository topics.
    """
    all_topics = []
    project_topics = []
    for repo in repos:
        if repo['topics']:
            all_topics.extend(repo['topics'])
            project_topics.append(repo['topics'])

    if not all_topics:
        return None

    topic_counts = Counter(all_topics)
    
    G = nx.Graph()

    # Add nodes
    for topic in topic_counts:
        G.add_node(topic)

    # Add edges based on co-occurrence
    for topics in project_topics:
        if len(topics) > 1:
            for i in range(len(topics)):
                for j in range(i + 1, len(topics)):
                    t1, t2 = topics[i], topics[j]
                    if G.has_edge(t1, t2):
                        G[t1][t2]['weight'] += 0.1
                    else:
                        G.add_edge(t1, t2, weight=1)

    if not G.nodes():
        return None
        
    # Hierarchical layout
    pos = {}
    counts_to_topics = {}
    for topic, count in topic_counts.items():
        if count not in counts_to_topics:
            counts_to_topics[count] = []
        counts_to_topics[count].append(topic)
    
    sorted_unique_counts = sorted(counts_to_topics.keys(), reverse=True)
    y_levels = {count: i for i, count in enumerate(sorted_unique_counts)}
    
    for count, topics in counts_to_topics.items():
        y = y_levels[count]
        xs = np.linspace(-len(topics)/2, len(topics)/2, len(topics))
        for i, topic in enumerate(sorted(topics)):
            pos[topic] = (xs[i] * 1.5, y * 2)

    node_sizes = [topic_counts[n] * 200 for n in G.nodes()]
    edge_widths = [G[u][v]['weight'] for u, v in G.edges()]

    plt.figure(figsize=(24, 24), dpi=150)
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.2, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=9, font_family='sans-serif', font_weight='bold')
    
    plt.title('Skills Graph', size=30)
    plt.axis('off')
    plt.tight_layout()
    
    graph_path = "skills_graph.png"
    plt.savefig(graph_path, format='png', bbox_inches='tight')
    plt.close()
    
    return graph_path

def update_readme(username):
    """
    Updates the README.md file with a list of public repositories and a skills graph.
    """
    repos = get_public_repos(username)
    if repos is None:
        return

    # Sort repositories by last updated time, descending
    repos.sort(key=lambda x: x['updated_at'], reverse=True)

    # Generate the Markdown table of projects
    projects_md = "| Project | Description | Skills |\n"
    projects_md += "|---|---|---|\n"
    for repo in repos:
        # Prepare skills badges
        skills_badges = ""
        if repo['topics']:
            skills_badges = " ".join([
                f"![{topic}](https://img.shields.io/badge/{urllib.parse.quote(topic)}-white?style=for-the-badge&logo={urllib.parse.quote(topic.lower())}&logoColor=black)"
                for topic in repo['topics']
            ])
        
        description = repo.get('description', 'No description')
        if description is None:
            description = 'No description'
            
        projects_md += f"| [{repo['name']}]({repo['html_url']}) | {description} | {skills_badges} |\n"

    # Generate skills graph
    graph_path = generate_skills_graph(repos)

    # Read the existing README content
    try:
        with open("README.md", "r") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print("README.md not found.")
        return

    # Use placeholders to find and replace the projects list
    start_placeholder = "<!-- PROJECTS_LIST -->"
    end_placeholder = "<!-- PROJECTS_LIST_END -->"

    if start_placeholder in readme_content and end_placeholder in readme_content:
        # Find the content between placeholders
        start_index = readme_content.find(start_placeholder) + len(start_placeholder)
        end_index = readme_content.find(end_placeholder)
        
        # Build the new README content for projects
        readme_content = (
            readme_content[:start_index]
            + "\n"
            + projects_md
            + readme_content[end_index:]
        )

    # Use placeholders to find and replace the skills graph
    start_graph_placeholder = "<!-- SKILLS_GRAPH -->"
    end_graph_placeholder = "<!-- SKILLS_GRAPH_END -->"

    if start_graph_placeholder in readme_content and end_graph_placeholder in readme_content:
        start_index = readme_content.find(start_graph_placeholder) + len(start_graph_placeholder)
        end_index = readme_content.find(end_graph_placeholder)
        
        # Build the new README content for skills graph
        if graph_path:
            skills_graph_md = f"\n![Skills Graph]({graph_path})\n"
        else:
            skills_graph_md = "\n_Could not generate skills graph._\n"
        
        readme_content = (
            readme_content[:start_index]
            + skills_graph_md
            + readme_content[end_index:]
        )

    # Write the updated content back to the README file
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("README.md updated successfully with the project list and skills graph.")

if __name__ == "__main__":
    github_username = "Krasnomakov"
    update_readme(github_username) 