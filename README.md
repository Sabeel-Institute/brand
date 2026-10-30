# Sabeel Institute brand

The colours, logo, and design guidance for everything Sabeel Institute makes:
the website, the apps, flyers, and printed material, and the shared method for
getting the apps onto phones. The guidance is written as skills for AI agents
such as Claude, and reads just as well for people.

## Skills

| Skill | Use it for |
|---|---|
| [`sabeel-brand`](skills/sabeel-brand/SKILL.md) | The palette and the logo on any surface: the five colours and their proportions, readable text colours, the single light theme, and which logo version to use where |
| [`sabeel-flyers`](skills/sabeel-flyers/SKILL.md) | Program flyers: what every flyer says, layout, formats, QR codes, and how to write dates, times, and names |
| [`sabeel-app-stores`](skills/sabeel-app-stores/SKILL.md) | The apps on the App Store and Google Play: the decisions that keep review simple (no account creation in the phone apps, the reviewer's account, the institute's rules and a report form, adults only), how we answer each store, the shared Apple and Play accounts, and the submission checklists |

## Installing a skill

Ask your agent to install it, for example: “Install the sabeel-flyers skill from
https://github.com/Sabeel-Institute/brand.”

To install one yourself:

- **Claude Code:** copy the skill's folder, such as `skills/sabeel-flyers`, into
  `~/.claude/skills/` to use it in all your projects, or into a project's
  `.claude/skills/`.
- **Claude apps (claude.ai and the desktop app):** zip the skill's folder and
  upload the zip under **Customize → Skills**. Code execution must be turned on.

This repository has the latest version of each skill. To update one, install it
again.

## Logo files

The logo files are in
[`skills/sabeel-brand/logo/`](skills/sabeel-brand/logo/):

| File | What it is |
|---|---|
| `sabeel-logo.png` | The logo on a transparent background, for ivory and other light backgrounds |
| `sabeel-logo-ivory.png` | The ivory version, only for dark or raspberry backgrounds |
| `sabeel-icon.png` | The calligraphy on an ivory square, 1024 × 1024 px, for favicons, app icons, and profile pictures |
| `sabeel-mark-earlier.png` | The calligraphy before 2026-09-28, black: the mark of the apps' icons, beside each app's badge |

The apps' icons come from [`skills/sabeel-brand/tools/make-app-icons.py`](skills/sabeel-brand/tools/make-app-icons.py), which writes them into each app's repository (the `sabeel-brand` skill, "The apps' icons").

The Sabeel Institute name and logo belong to Sabeel Institute. Use them only
for Sabeel Institute's work.

## Changing the brand

New files from the designer and changes to the guidance go here first. Then
update the website and the apps to match.
