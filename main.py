import argparse
import re
import sys

# The PyGithub import sits inside run(), not at the top of the file.
# The first version imported it before the argument check, so
# `python main.py --help` on a machine without PyGithub installed
# crashed with ModuleNotFoundError instead of printing usage. Help is
# a local question, so I answer it locally, before any import that
# can fail and before anything touches the network.

DEFAULT_REPO = "CY83R-3X71NC710N/Example-Project"
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Close every open issue in one GitHub repository. "
        "Open pull requests are skipped, not closed."
    )
    parser.add_argument("pat", help="GitHub personal access token with the repo scope")
    parser.add_argument(
        "repository",
        nargs="?",
        default=DEFAULT_REPO,
        help="owner/repository (default: the placeholder %(default)s)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list what would be closed without closing anything",
    )
    return parser.parse_args(argv)


def close_issues(repo, dry_run=False, out=sys.stdout):
    """Close every open issue in repo, skipping pull requests.

    Returns (closed, skipped). In dry run mode nothing is edited and
    the would-be closes count as closed for reporting only.
    I ask only for open issues. Closed ones are never returned, which
    is what makes a rerun after a rate limit stop safe: the rerun
    picks up what is still open instead of going over finished work.
    """
    closed = 0
    skipped = 0
    for issue in repo.get_issues(state="open"):
        # get_issues returns open pull requests mixed in with the
        # issues, because on GitHub a pull request is tracked like an
        # issue. Closing one here would shut down a review nobody
        # asked me to touch, so I check pull_request on every item
        # and skip it out loud.
        if issue.pull_request is not None:
            print(f"Skipped pull request #{issue.number}: {issue.title}", file=out)
            skipped += 1
            continue
        if dry_run:
            print(f"Would close issue #{issue.number}: {issue.title}", file=out)
        else:
            # I close first and print after. If edit() raises, no
            # "Closed" line prints for that issue, so the output only
            # ever lists closes that already happened.
            issue.edit(state="closed")
            print(f"Closed issue #{issue.number}: {issue.title}", file=out)
        closed += 1
    return closed, skipped


def run(pat, repository, dry_run=False):
    # Imported here, after --help and validation have had their
    # chance to answer without the dependency or the network.
    from github import Github

    # The credential arrives as a plain command line argument. That
    # is simple, and it is also the weak point of this script:
    # arguments can show in shell history and in a process listing. I
    # warn about the history in the last line of main. I do not prompt
    # for it or read it from a file, because I wrote this as a quick
    # one job tool and I accept that trade for that use.
    client = Github(pat)
    repo = client.get_repo(repository)
    return close_issues(repo, dry_run=dry_run)


def main(argv=None):
    args = parse_args(argv)
    if not REPO_RE.match(args.repository):
        print(
            f"Error: {args.repository!r} does not look like owner/repository.",
            file=sys.stderr,
        )
        return 2
    # A bad credential or a bad repo name stops the run with the real
    # API error text and exit 1, before any close happens, instead of
    # a raw traceback. KeyboardInterrupt is not caught here on
    # purpose: a person stopping a bulk close should see it stop.
    try:
        closed, skipped = run(args.pat, args.repository, dry_run=args.dry_run)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    mode = "Would close" if args.dry_run else "Closed"
    print(f"Done. {mode} {closed} issue(s), skipped {skipped} pull request(s).")
    # This warning is all I can honestly do about the credential in
    # the shell history. An earlier version of this script tried to
    # clear the history and the screen from inside the process and
    # printed that it had done so. It could not work: history belongs
    # to the parent shell, and a child process cannot clear it.
    print(
        "Note: the token was passed on the command line, so it may be saved in your "
        "shell history. Clear that history yourself if that is a concern; a script "
        "cannot clear its parent shell's history."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
