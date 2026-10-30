from github import Github
import sys

# This check runs before anything touches the network, on purpose. The
# first version had no check: running with no arguments crashed on
# sys.argv[1], and running with --help sent the word "--help" to GitHub
# as the token and got a 401 back. Wave 1 reproduced both. Help is a
# local question, so I answer it locally.
# The exit codes split for a reason. Asking for help on purpose exits 0.
# A missing token exits 2, because that run was a mistake.
if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print("Usage: python main.py INSERT_PAT_HERE [owner/repository]")
    print("The repository argument is optional and defaults to the placeholder below.")
    sys.exit(0 if len(sys.argv) >= 2 else 2)

# The token arrives as a plain command line argument. That is simple,
# and it is also the weak point of this script: arguments can show in
# shell history and in a process listing. I warn about the history in
# the last line of the script. I do not prompt for the token or read it
# from a file, because I wrote this as a quick one job tool and I accept
# that trade for that use.
token = sys.argv[1]

# The default below is a placeholder, not a real repository. I left it
# as the default so the old command line still parses the same way, but
# a run with no second argument points at a repo nobody means. This is
# the argument to read twice before running.
# Anything past the second argument is ignored. A typo in a third
# argument changes nothing and warns about nothing.
repo_name = sys.argv[2] if len(sys.argv) > 2 else 'CY83R-3X71NC710N/Example-Project'

# There is no dry run mode and no confirmation prompt in this script.
# With a valid token, the first thing it does is start closing. That is
# the whole design, and it is why the repository argument above matters
# more than any other line here.
# I do not catch errors from these two calls. A bad token or a bad repo
# name should stop the run with the real API error, before any close
# happens, not be papered over with a friendlier guess.
g = Github(token)
repo = g.get_repo(repo_name)

# I ask only for open issues. Closed ones are never returned, which is
# what makes a rerun after a rate limit stop safe: the rerun picks up
# what is still open instead of going over finished work again.
issues = repo.get_issues(state='open')

for issue in issues:
    # get_issues returns open pull requests mixed in with the issues,
    # because on GitHub a pull request is tracked like an issue. Closing
    # one here would shut down a review nobody asked me to touch, so I
    # check pull_request on every item and skip it out loud. Wave 1
    # verified the skip with a mocked PyGithub run.
    if issue.pull_request is not None:
        print(f"Skipped pull request #{issue.number}: {issue.title}")
        continue
    # I close first and print after. If edit() raises, the run stops and
    # no "Closed" line prints for that issue, so the output only ever
    # lists closes that already happened. Everything after the failed
    # issue stays open for the rerun.
    issue.edit(state='closed')
    print(f"Closed issue #{issue.number}: {issue.title}")

# This warning is all I can honestly do about the token in the shell
# history. An earlier version of this script tried to clear the history
# and the screen from inside the process and printed that it had done
# so. It could not work: history belongs to the parent shell, and a
# child process cannot clear it. Wave 1 removed that code and its claim
# together, and this line is what replaced them.
print("Done. Note: the token was passed on the command line, so it may be saved in your shell history. Clear that history yourself if that is a concern; a script cannot clear its parent shell's history.")
