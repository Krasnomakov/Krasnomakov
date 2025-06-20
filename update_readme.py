import os
import requests
import urllib.parse

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
    Updates the README.md file with a list of public repositories.
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
        
        # Build the new README content
        new_readme = (
            readme_content[:start_index]
            + "\n"
            + projects_md
            + "\n"
            + readme_content[end_index:]
        )

        # Write the updated content back to the README file
        with open("README.md", "w") as f:
            f.write(new_readme)
        print("README.md updated successfully with the project list.")
    else:
        print("Placeholders not found in README.md. Could not update the project list.")

if __name__ == "__main__":
    github_username = "Krasnomakov"
    update_readme(github_username) 