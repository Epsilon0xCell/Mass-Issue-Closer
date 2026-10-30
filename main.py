from github import Github
import sys

# usage: python main.py INSERT_PAT_HERE [owner/repository]
if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print("Usage: python main.py INSERT_PAT_HERE [owner/repository]")
    print("The repository argument is optional and defaults to the placeholder below.")
    sys.exit(0 if len(sys.argv) >= 2 else 2)

# get the personal access token from the command-line arguments
token = sys.argv[1]

# get the repository from the command-line arguments if one was given
repo_name = sys.argv[2] if len(sys.argv) > 2 else 'CY83R-3X71NC710N/Example-Project'

# authenticate to GitHub API using personal access token
g = Github(token)

# get repository
repo = g.get_repo(repo_name)

# get all issues in the repository
issues = repo.get_issues(state='open')

# iterate over the issues and close each one
for issue in issues:
    # get_issues also returns pull requests, which are not issues to close here
    if issue.pull_request is not None:
        print(f"Skipped pull request #{issue.number}: {issue.title}")
        continue
    issue.edit(state='closed')
    print(f"Closed issue #{issue.number}: {issue.title}")

print("Done. Note: the token was passed on the command line, so it may be saved in your shell history. Clear that history yourself if that is a concern; a script cannot clear its parent shell's history.")
