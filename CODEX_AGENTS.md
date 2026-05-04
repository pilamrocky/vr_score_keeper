# VR Score Keeper Agent Notes

## Project Overview

VR Score Keeper is a Django web app for managing VR golf tournaments. It supports authenticated users, tournament creation, player registration, match creation, per-player scoring, winner tracking, profile editing, and a small admin surface.

The actual Django project lives in `vr_score_keeper/` inside this repository root.

## Layout

- `vr_score_keeper/manage.py`: Django management entry point.
- `vr_score_keeper/settings/settings/`: split settings modules.
  - `base.py`: common Django apps, middleware, templates, SQLite default, logging.
  - `dev.py`: development settings.
  - `prod.py`: production settings using `DATABASE_URL`, secure cookies, WhiteNoise.
- `vr_score_keeper/vr_tournaments/`: main app.
  - `models.py`: `Tournament`, `Player`, `Match`, `Score`.
  - `forms.py`: tournament/player/match/profile forms plus `MultiScoreForm`.
  - `views.py`: function-based views for tournament dashboard, CRUD-ish actions, scores, and profiles.
  - `templates/`: Bulma-based app templates.
  - `tests/`: basic Django unit tests for models/forms/views.
- `vr_score_keeper/templates/registration/`: auth templates.
- `vr_score_keeper/Dockerfile`, `docker-compose.yml`, `docker-compose.prod.yml`: container workflows.

## Local Workflow

The README expects Docker:

```bash
cd vr_score_keeper
docker-compose up --build
docker-compose exec web python manage.py test vr_tournaments
```

This checkout is normally developed from WSL. When Codex is launched from Windows/PowerShell, prefer invoking WSL explicitly instead of using Windows `python` or Windows `git`.

Use the repo-root WSL virtual environment, not the nested app-local `vr_score_keeper/env`:

```bash
wsl -d Ubuntu-22.04 -e bash -lc 'cd /home/rocky/repos/vr_score_keeper/vr_score_keeper && ../env/bin/python manage.py test vr_tournaments'
wsl -d Ubuntu-22.04 -e bash -lc 'cd /home/rocky/repos/vr_score_keeper/vr_score_keeper && ../env/bin/python manage.py check'
```

WSL Git should be used for status/diff:

```bash
wsl -d Ubuntu-22.04 -e bash -lc 'cd /home/rocky/repos/vr_score_keeper && git status --short --branch'
```

Avoid setting the shell command `workdir` to the `V:\...` path when invoking `wsl.exe`; WSL emits path-translation warnings. Use a neutral Windows working directory such as `C:\` and do the Linux `cd` inside `bash -lc`.

Test status as of the environment setup review: `../env/bin/python manage.py test vr_tournaments` passes 18 tests.

To run the app from a Windows-launched Codex session, start WSL as the long-lived server process. `Start-Process` works reliably with a single argument string:

```powershell
$arg='-d Ubuntu-22.04 -e bash -lc "cd /home/rocky/repos/vr_score_keeper/vr_score_keeper && exec ../env/bin/python manage.py runserver 0.0.0.0:8000 --noreload"'
$p=Start-Process wsl.exe -ArgumentList $arg -PassThru -WindowStyle Hidden
```

Verify it from WSL:

```bash
wsl -d Ubuntu-22.04 -e bash -lc 'curl -I http://127.0.0.1:8000/'
```

The app is login-protected, so `/` should return `302 Found` to `/accounts/login/?next=/` when not authenticated.

## Current Review Notes

- Existing modified files before this note was added: `vr_score_keeper/build_and_push.sh`, `vr_score_keeper/entrypoint.sh`, `vr_score_keeper/manage.py`. Treat them as user changes unless told otherwise.
- `db.sqlite3` and `backup/db.sqlite3` are currently tracked. Be careful not to overwrite real data.
- Current authorization model:
  - Any authenticated user can view `index`, `tournaments`, profile pages.
  - Superusers can manage players and player registration.
  - Users in the `powerUser` group, plus superusers, can view tournament details, create matches/scores, and delete matches.
- Score/winner rules are currently implicit in code: `index()` marks a tournament winner when a player total reaches at least 30.

## Follow-up Candidates

- Fix score resubmission so existing `Score` rows are updated instead of silently keeping old values.
- Decide whether `powerUser` should be able to create tournaments; the view permits it, but the template only shows the button to superusers.
- Replace direct `.objects.get()` calls in views with `get_object_or_404()` and validate posted player/tournament relationships.
- Review production Docker settings before relying on the image: ownership/entrypoint behavior and development Compose settings need attention.
- Add tests for score editing/resubmission, power-user permissions, tournament winner transitions, and missing-object behavior.
