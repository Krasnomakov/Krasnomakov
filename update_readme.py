import os
import requests

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

    # Generate the Markdown list of projects
    projects_md = ""
    for repo in repos:
        projects_md += f"- [{repo['name']}]({repo['html_url']}) - {repo.get('description', 'No description')}\n"

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