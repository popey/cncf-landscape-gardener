import yaml
import requests
import time
import os
import re

def check_repo_url(repo_url):
    """
    Validates and normalizes a repository URL.

    Args:
        repo_url (str): The repository URL to validate.

    Returns:
        str: A normalized URL if valid, None otherwise.
    """

    if not repo_url:
        return None

    # Remove trailing slashes
    repo_url = repo_url.rstrip('/')

    # Handle GitHub URLs
    if "github.com" in repo_url:
        if re.search(r'github.com/[^/]+/[^/]+$', repo_url):
            return repo_url
        else:
            return None  # Not a valid GitHub repo URL

    # Handle GitLab URLs
    elif "gitlab.com" in repo_url:
        return None  # Indicate GitLab is unsupported for now

    else:
        return None  # Unsupported code forge

def check_github_repo(repo_url):
    """
    Checks if a GitHub repository exists, is public, and is not archived.

    Args:
        repo_url (str): The URL of the GitHub repository.

    Returns:
        str: A string describing any issues, or None if no issues.
    """
    # Extract the owner and repo name from the URL
    parts = repo_url.split('/')
    owner = parts[-2]
    repo = parts[-1]

    # GitHub API endpoint to get repository information
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {}
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    time.sleep(0.5)  # Sleep to avoid hitting rate limits
    print(f"Checking {repo_url}...")

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Check Content-Type
        content_type = response.headers.get('Content-Type')
        if content_type and 'application/json' in content_type:
            repo_info = response.json()

            if repo_info.get('private'):
                return f"{repo_url} is private"
            if repo_info.get('archived'):
                return f"{repo_url} is archived"
            return None
        else:
            # Handle non-JSON responses (e.g., HTML error pages)
            if response.status_code == 404:
                return f"{repo_url} does not exist (HTTP 404)"
            elif response.status_code == 403:
                return f"Error 403: Forbidden - Skipping {repo_url}"
            else:
                return f"Unexpected response from {repo_url}: {response.status_code} - {response.text[:100]}"  # Include status and first part of text


    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"Rate limit hit. Retrying after 60 seconds for {repo_url}")
            time.sleep(60)  # Wait and retry
            return check_github_repo(repo_url)  # Recursive call to retry
        else:
            return f"HTTP error checking {repo_url}: {e}"
    except Exception as e:
        return f"Error checking {repo_url}: {e}"

def process_landscape_yaml(filename):
    """
    Processes the landscape.yaml file to extract repo URLs and check them.

    Args:
        filename (str): The path to the landscape.yaml file.
    """

    invalid_repos = []

    with open(filename, 'r') as f:
        data = yaml.safe_load(f)

    for category in data['landscape']:
        for subcategory in category['subcategories']:
            for item in subcategory['items']:
                repo_url = item.get('repo_url')
                valid_url = check_repo_url(repo_url)
                if valid_url:
                    if "github.com" in valid_url:
                      error = check_github_repo(valid_url)
                      if error:
                          #Include project status in the output
                          status_message = f"{error}"
                          project_status = item.get('project')  # Get project status
                          if project_status:
                            status_message += f" (CNCF Project Status: {project_status})"
                          invalid_repos.append(status_message)
                    elif "gitlab.com" in valid_url:
                        invalid_repos.append(f"Skipping: {repo_url} - Unsupported code forge")


    if invalid_repos:
        print("The following repositories have issues:")
        for error in invalid_repos:
            print(f"  - {error}")
    else:
        print("No invalid repositories found.")

# Main execution
if __name__ == "__main__":
    filename = 'landscape.yml'  # Replace with the actual filename if different
    process_landscape_yaml(filename)