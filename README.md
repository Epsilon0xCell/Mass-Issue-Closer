![Intro: the end of the line, the conveyor empty and still under its row of red stamp presses, one last cream ticket waiting on the side belt beside the tall stack of stamped tickets](intro-banner.png)


# Mass-Issue-Closer

<p align="center"><img src="logo.png" alt="Mass-Issue-Closer logo: a black conveyor belt seen from above, a heavy red stamp press descending onto one blank cream ticket, steel blue factory frame around the belt" width="200"></p>

![Banner: a long steel blue factory conveyor carrying a queue of cream tickets toward a row of red stamp presses, the stamped tickets stacking into a neat pile at the end while one differently shaped piece is diverted onto a side belt](banner.png)

![Scene](scene.svg)

Mass GitHub issue closer, written after its author created too many issues.

This Python script closes every open issue in one GitHub repository. Open pull requests in the repository are skipped, not closed.


![Separator](sep-heavy.svg)

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

- The token argument is required. Running with no arguments prints
  the usage message and exits 2. `-h` or `--help` prints the full
  usage and exits 0, and it works even on a machine where PyGithub is
  not installed yet, because the import happens after argument
  parsing.
- Add `--dry-run` to list the issues that would be closed, and the
  pull requests that would be skipped, without closing anything. For
  a bulk action with no undo in this script, that is the mode to run
  first.
- A repository argument that is not shaped like `owner/repository`
  exits 2 before any network call. A bad token or unknown repository
  prints the API error and exits 1, before any close happens.
- The repository argument is optional. When it is omitted, the script uses the placeholder repository written in `main.py` (`CY83R-3X71NC710N/Example-Project`), so pass a real `owner/repository` value for real use.
- The script prints one line for each issue it closes and one line for each pull request it skips.

> **Line caution, stamped on the first ticket:** bulk closing is not bulk reversible, and pull requests are deliberately skipped, never closed. Read the ticket before the stamp falls: confirm the repository twice, and run `--dry-run` first.

Warning: this closes issues in bulk and the action is not undone by the script. Double check the repository argument before running, and run with `--dry-run` first.

Tests: `python3 -m unittest` runs the closing logic against fake
issues and a fake PyGithub module (no network, no real token),
covering the pull request skip, dry run, and the exit codes.

Note on the token: because the token is passed on the command line, it may be saved in your shell history. The script cannot clear its parent shell's history (an earlier version claimed to do this; that code did not work and has been removed), so clear your history yourself afterwards if that is a concern.

## Did the script stop without closing all issues?

Simply rerun it. This has happened due to API rate limits by GitHub, and issues that are already closed are not returned again, so a rerun continues with what is still open.
