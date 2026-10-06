# Security Notice

## What happened

On 2026-10-06, the user received a GitHub Secret Scanning alert on the
repository `LeslieDian/pydanticAI-zhongyi`.

## Root cause

The alert was a **false positive**. During initial development of the
project, a commit (`09d3542`) included the literal string
`sk-cp-fakefake-fake-fake-fake-fake-fake-fake` in its commit message
as part of describing a pre-commit hook test (“attempting to commit
a file with `sk-cp-fakefake...`”).

GitHub Secret Scanning flags any string matching the `sk-` prefix
pattern, even when the actual content is clearly fake.

## What is real and what is fake

- **Fake**: `sk-cp-fakefake-fake-fake-fake-fake-fake-fake`
  - This appears only in the commit message of `09d3542`
  - It is a literal description string, not a credential
- **Real API key** (the user's actual MiniMax key): stored **only** in
  the local `.env` file, which is git-ignored and has never been
  pushed to GitHub.

## Verification

We have verified:

1. All 6 commits on the public `main` branch are clean (no `sk-` strings).
2. The `.env` file is NOT in the repository (`.gitignore` works).
3. The `.env.example` template contains only empty placeholders.
4. No issues, PRs, or commit comments contain real keys.

## Resolution

The misleading commit `09d3542` has been replaced with `eb37b30`
(via `git push --force-with-lease`) with a commit message that does
not contain the `sk-cp-` prefix pattern. The old commit object may
still exist in GitHub's object store (GitHub does not garbage-collect
unreachable commits immediately), but it is no longer reachable from
any branch or tag.

## What you should do

If you received a Secret Scanning alert email from GitHub:

1. **Do not panic** — it is a false positive based on the literal string `sk-cp-fakefake...`
2. The "secret" in question is `sk-cp-fakefake-fake-fake-fake-fake-fake-fake`, not a real credential
3. You can dismiss the alert in GitHub Settings → Code security → Secret scanning
4. As a precaution, **rotate your real MiniMax API key** in the MiniMax dashboard,
   and update `.env` with the new value

## Long-term safeguards

The repository now has:

- `.git/hooks/pre-commit`: rejects any staged file matching the API key pattern
- README security section: prominent warnings and instructions
- `.gitignore`: excludes `.env` and `.env.*` files

## Contact

If you have concerns, open a GitHub issue or contact the maintainer.
