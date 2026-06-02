# knowledge-forge

A personal teacher that lives in Claude and takes you from zero to passing a
certification (AWS, Azure, GCP, CompTIA, CISSP, PMP, CKA, and more).

Ships one skill: **learning-sprint**. You chat with it like a tutor in a study group.
It researches the real exam, teaches you in digestible chapters, draws diagrams when
they help, quizzes you, runs timed mock exams, tracks your progress across exams, and
tells you — honestly — when you're ready to sit the test.

---

## Install

Pick the app you use. Both take about a minute.

### Claude Code (terminal)

Run these two commands:

```bash
claude plugin marketplace add browerthomas/knowledge-forge
claude plugin install learning-sprint@knowledge-forge
```

Restart Claude Code. Done.

### Claude Cowork (Mac app)

Copy the skill into Cowork's skills folder:

```bash
git clone https://github.com/browerthomas/knowledge-forge.git
cp -R knowledge-forge/plugins/learning-sprint/skills/learning-sprint ~/.claude/skills/learning-sprint
```

Restart Cowork. Done. (To let it research the live exam, turn on **Web Search**: your
workspace Owner enables it, then click **+ → Web search** in a chat.)

---

## How to use it

Just talk to it. For example:

- **"Study for my AWS Machine Learning Engineer – Associate exam."**
- **"Teach me Kubernetes networking."**
- **"Quiz me on TLS."**

It will ask what you already know and when your exam is, then start teaching. As you
go, you can say things like:

- **"Show me that"** / **"put it on the board"** — it draws a diagram.
- **"Give me the next chapter as a PDF."**
- **"Make me a practice exam."** / **"Am I ready?"**

Your progress is saved automatically, so you can come back any time and say
**"resume my sprint"** — even across several certs at once.

---

## Good to know

- **Free study materials it can make for you:** flashcards (Anki), a printable study
  guide, and timed practice exams. These use `python3` (already on most machines).
  Flashcards always export as a file you import into Anki; install `genanki`
  (`pip install genanki`) for one-click decks. Study guides/exams open in your browser
  to print or save as PDF.
- **It won't make things up.** Before teaching, it researches the current exam against
  real sources and flags anything it can't verify.
- **Your study data stays on your computer** (in `~/learning-sprints/`). Nothing is
  uploaded.

---

## Updating

When a new version ships:

- **Claude Code:** `claude plugin marketplace update knowledge-forge`
- **Cowork:** `git pull` in the cloned folder, then copy the skill folder again.

---

<details>
<summary>For maintainers (publishing changes)</summary>

This repo is a Claude Code plugin marketplace. Layout:

```
.claude-plugin/marketplace.json
plugins/learning-sprint/
  .claude-plugin/plugin.json
  skills/learning-sprint/SKILL.md   ← the skill
  skills/learning-sprint/references/  ← how-to docs the skill reads
  skills/learning-sprint/scripts/     ← python generators (chapters, exams, Anki, tracking)
README.md
```

To ship an update: edit the skill, bump `version` in **both** `marketplace.json` and
`plugin.json`, and push. Installers refresh with the update commands above.
</details>
