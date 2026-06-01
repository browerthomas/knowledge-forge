# knowledge-forge

A personal Claude skills marketplace. Currently ships one skill: **learning-sprint**.

> **learning-sprint** — takes any topic from zero to retained understanding using six chained techniques: a 20-hour 80/20 plan, a one-page cheat sheet, progressive quizzing, a 5-level difficulty ladder, web-validated resources, and the Feynman re-teach loop. The first time it runs in a conversation it shows an orientation card and lets you pick a run mode.

---

## Publishing this (you, once)

1. Create a **public** GitHub repo — `browerthomas/knowledge-forge`.
2. Push the entire contents of this folder to the repo root (so `.claude-plugin/marketplace.json` sits at the top level).
3. Done. Anyone can now install it with the commands below. To ship updates, bump the `version` fields and push — installers refresh with `/plugin marketplace update`.

```
your-repo-root/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── learning-sprint/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── learning-sprint/
│               └── SKILL.md
└── README.md
```

---

## Installing it (your friend)

The marketplace name is `knowledge-forge` and the plugin name is `learning-sprint`, so the install target is `learning-sprint@knowledge-forge`.

### Claude Code (terminal)

```bash
claude plugin marketplace add browerthomas/knowledge-forge
claude plugin install learning-sprint@knowledge-forge
```

Or from inside a Claude Code session, interactively:

```
/plugin marketplace add browerthomas/knowledge-forge
/plugin install learning-sprint@knowledge-forge
```

Restart the session after installing. Then just say "teach me X" or "run a learning sprint on X."

### Claude Desktop app

1. Open the **Customize** panel in the left sidebar → **Skills**.
2. Click **+** next to *Personal plugins*.
3. Paste the GitHub repo path (`browerthomas/knowledge-forge`) and click **Sync**.
4. Click **Install** on `learning-sprint`.
5. Start a new conversation — the skill is live.

### Claude.ai (web) — zip upload fallback

The web app installs skills as an uploaded folder rather than from a repo URL. Use the bundled `learning-sprint.zip`:

1. Settings → **Capabilities / Skills** → **Upload skill**.
2. Select `learning-sprint.zip`.

Skills require a paid Claude plan. If the upload option isn't present, the account/plan doesn't have custom skills enabled.

---

## Notes

- Requires a recent Claude Code (plugin/marketplace support; v2.0.13+ is a safe floor, newer is better).
- Private repos work too — installers just need git credentials configured for the host (e.g. `gh auth login`).
- The skill itself is plain markdown (`SKILL.md`) with a YAML frontmatter `description` that controls when Claude auto-invokes it.
