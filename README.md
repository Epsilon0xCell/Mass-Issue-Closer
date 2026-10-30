![banner](assets/banner.png)

# Mass-Issue-Closer

Mass GitHub issue closer, written after its author created too many issues.

This Python script closes every open issue in one GitHub repository. Open pull requests in the repository are skipped, not closed.

## Setup

Generate a classic GitHub personal access token with the `repo` scope (which includes `public_repo` for public repositories).

Install the one dependency:

```
pip install -r requirements.txt
```

That installs PyGithub. Installing it directly also works:

```
pip install PyGithub
```

## Usage

Run the script as:

```
python main.py INSERT_PAT_HERE [owner/repository]
```

- The token argument is required. Running with no arguments, or with `-h` or `--help`, prints the usage line instead of an error.
- The repository argument is optional. When it is omitted, the script uses the placeholder repository written in `main.py` (`CY83R-3X71NC710N/Example-Project`), so pass a real `owner/repository` value for real use.
- The script prints one line for each issue it closes and one line for each pull request it skips.

Warning: this closes issues in bulk and the action is not undone by the script. Double check the repository argument before running.

Note on the token: because the token is passed on the command line, it may be saved in your shell history. The script cannot clear its parent shell's history (an earlier version claimed to do this; that code did not work and has been removed), so clear your history yourself afterwards if that is a concern.

## Did the script stop without closing all issues?

Simply rerun it. This has happened due to API rate limits by GitHub, and issues that are already closed are not returned again, so a rerun continues with what is still open.
