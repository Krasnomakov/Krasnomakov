import os
import requests
import urllib.parse
from collections import Counter

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
    Generates a Mermaid graph of skills from repository topics.
    """
    all_topics = []
    project_topics = []
    for repo in repos:
        if repo['topics']:
            all_topics.extend(repo['topics'])
            project_topics.append(repo['topics'])

    if not all_topics:
        return ""

    topic_counts = Counter(all_topics)
    
    # Group topics by count
    counts_to_topics = {}
    for topic, count in topic_counts.items():
        if count not in counts_to_topics:
            counts_to_topics[count] = []
        counts_to_topics[count].append(topic)

    # Sort counts in descending order
    sorted_counts = sorted(counts_to_topics.keys(), reverse=True)
    
    mermaid_str = "```mermaid\ngraph TD\n"

    def sanitize(topic):
        """Sanitizes topic names for Mermaid IDs."""
        return urllib.parse.quote(topic).replace('-', '_').replace(' ', '_')

    # Define nodes and ranks using subgraphs
    all_sanitized_nodes = {}
    rank_num = 1
    for count in sorted_counts:
        topics_in_rank = counts_to_topics[count]
        
        plural = 's' if count > 1 else ''
        mermaid_str += f'    subgraph "Rank {rank_num} - Used in {count} project{plural}"\n'
        node_definitions = []
        for topic in topics_in_rank:
            sanitized_topic = sanitize(topic)
            all_sanitized_nodes[topic] = sanitized_topic
            node_definitions.append(f'{sanitized_topic}["{topic}"]')

        mermaid_str += "        " + "; ".join(node_definitions) + "\n"
        mermaid_str += "    end\n"
        rank_num += 1

    # Define links based on co-occurrence in projects
    links = set()
    for topics in project_topics:
        if len(topics) > 1:
            for i in range(len(topics)):
                for j in range(i + 1, len(topics)):
                    t1, t2 = sorted([topics[i], topics[j]])
                    st1 = all_sanitized_nodes.get(t1)
                    st2 = all_sanitized_nodes.get(t2)
                    if st1 and st2:
                        links.add(f"    {st1} --- {st2}")
    
    if links:
        mermaid_str += "\n" + "\n".join(sorted(list(links)))
    
    mermaid_str += "\n```"
    
    return mermaid_str

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
    skills_graph_md = generate_skills_graph(repos)

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
        readme_content = (
            readme_content[:start_index]
            + "\n"
            + skills_graph_md
            + "\n"
            + readme_content[end_index:]
        )

    # Write the updated content back to the README file
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("README.md updated successfully with the project list and skills graph.")

if __name__ == "__main__":
    github_username = "Krasnomakov"
    update_readme(github_username) 