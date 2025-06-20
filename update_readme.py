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

def update_readme(username):
    """
    Updates the README.md file with a list of public repositories and top skills.
    """
    repos = get_public_repos(username)
    if repos is None:
        return

    # Sort repositories by last updated time, descending
    repos.sort(key=lambda x: x['updated_at'], reverse=True)

    # --- Generate skills list ---
    all_topics = [topic for repo in repos if repo.get('topics') for topic in repo['topics']]
    top_skills = [skill for skill, count in Counter(all_topics).most_common(10)]
    
    colors = ['blue', 'green', 'yellow', 'orange', 'red', 'purple', 'pink', 'brightgreen', 'success', 'important']

    skills_md = " ".join([
        f"![{skill}](https://img.shields.io/badge/{urllib.parse.quote(skill)}-{colors[i % len(colors)]}?style=for-the-badge&logo={urllib.parse.quote(skill.lower())}&logoColor=white)"
        for i, skill in enumerate(top_skills)
    ])

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

    # Read the existing README content
    try:
        with open("README.md", "r") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print("README.md not found.")
        return

    # Use placeholders to find and replace the content
    def replace_between(content, start, end, new_text):
        if start in content and end in content:
            start_index = content.find(start) + len(start)
            end_index = content.find(end)
            return content[:start_index] + "\n" + new_text + "\n" + content[end_index:]
        return content

    readme_content = replace_between(readme_content, "<!-- SKILLS_LIST -->", "<!-- SKILLS_LIST_END -->", skills_md)
    readme_content = replace_between(readme_content, "<!-- PROJECTS_LIST -->", "<!-- PROJECTS_LIST_END -->", projects_md)
    
    # Write the updated content back to the README file
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("README.md updated successfully with skills and project list.")

if __name__ == "__main__":
    github_username = "Krasnomakov"
    update_readme(github_username) 