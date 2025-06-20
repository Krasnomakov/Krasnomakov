import os
import requests
import urllib.parse
import collections
import json

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

def generate_skills_chart(repos, top_n=15):
    """Generates a URL for a horizontal bar chart of top skills."""
    all_topics = [topic for repo in repos if repo.get('topics') for topic in repo['topics']]
    if not all_topics:
        return ""

    counter = collections.Counter(all_topics)
    top_skills = counter.most_common(top_n)

    labels = [skill for skill, count in reversed(top_skills)]
    data = [count for skill, count in reversed(top_skills)]

    chart_config = {
        'type': 'horizontalBar',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Projects',
                'data': data,
                'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        },
        'options': {
            'legend': {'display': False},
            'title': {
                'display': True,
                'text': 'Top Skills Across Projects',
                'fontSize': 18,
                'fontColor': '#333'
            },
            'scales': {
                'xAxes': [{
                    'ticks': {
                        'beginAtZero': True,
                        'stepSize': 1
                    }
                }],
                'yAxes': [{
                    'ticks': {
                        'fontSize': 12
                    }
                }]
            }
        }
    }
    
    encoded_config = urllib.parse.quote(json.dumps(chart_config))
    chart_url = f"https://quickchart.io/chart?c={encoded_config}&backgroundColor=white"
    
    return f"![Top Skills]({chart_url})"

def update_readme(username):
    """
    Updates the README.md file with a list of public repositories and a skills chart.
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

    # Generate skills chart
    skills_chart_md = generate_skills_chart(repos)

    # Read the existing README content
    try:
        with open("README.md", "r") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print("README.md not found.")
        return

    # Update projects list
    start_placeholder = "<!-- PROJECTS_LIST -->"
    end_placeholder = "<!-- PROJECTS_LIST_END -->"
    if start_placeholder in readme_content and end_placeholder in readme_content:
        start_index = readme_content.find(start_placeholder) + len(start_placeholder)
        end_index = readme_content.find(end_placeholder)
        
        readme_content = (
            readme_content[:start_index]
            + "\n"
            + projects_md
            + readme_content[end_index:]
        )
    else:
        print("Placeholders for projects list not found in README.md.")

    # Update skills chart
    chart_start_placeholder = "<!-- SKILLS_CHART -->"
    chart_end_placeholder = "<!-- SKILLS_CHART_END -->"
    if chart_start_placeholder in readme_content and chart_end_placeholder in readme_content:
        start_index = readme_content.find(chart_start_placeholder) + len(chart_start_placeholder)
        end_index = readme_content.find(chart_end_placeholder)

        readme_content = (
            readme_content[:start_index]
            + "\n"
            + skills_chart_md
            + "\n"
            + readme_content[end_index:]
        )
    else:
        print("Placeholders for skills chart not found in README.md.")

    # Write the updated content back to the README file
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("README.md updated successfully.")

if __name__ == "__main__":
    github_username = "Krasnomakov"
    update_readme(github_username) 