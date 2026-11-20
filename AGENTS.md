# AGENTS.md — rules for every developer and AI coding tool

This repository is governed by the Software Factory
(<https://github.com/aliyuumaru-beep/software-factory-governance>, SPEC-GOV-ENF-001).
These rules apply to humans, Claude Code, Cursor, Copilot, Codex and any other tool.

1. Install the gateway once per machine:
   `git clone https://github.com/aliyuumaru-beep/software-factory-governance && bash software-factory-governance/enforcement/install.sh`
2. Read `CLAUDE.md` and the files listed under `briefing_docs` in `.governance.json` before changing anything.
3. Never commit to `main`. Work on a feature branch.
4. No spec, no code: the work item (WP-/DEC-/SPEC-…) must exist in the repo docs. `gov start <WORK-ITEM>`.
5. Never change a live database without a fresh backup and the sponsor's go-ahead.
6. Update the governance docs (`required_doc_updates` in `.governance.json`) with the change.
7. Run `gov review` — G1 Architecture, G2 Quality, G3 Security review the change as independent agents.
8. Open a PR citing the work item. GitHub runs the same G1/G2/G3 reviews; `governance / gate` must pass
   for anyone, including admins, to merge.
