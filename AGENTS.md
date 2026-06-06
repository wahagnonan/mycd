## Goal
Build a scalable registration and search flow for encadreurs (tutors) in Côte d'Ivoire with dynamic villes/quartiers data, "Autre" custom entries, and a comprehensive test suite.

## Constraints & Preferences
- Phone must start with +225 prefix; input limits to 10 digits max.
- Villes and quartiers must come from API (`/api/villes/`), not hardcoded.
- "Autre" option in dropdowns must show a text input for custom entry.
- Password fields must have eye icon toggle (show/hide).
- Code must be scalable and evolutive.
- Unit tests must cover backend (Django) and frontend (Next.js) completely.

## Progress
### Done
- Fixed `backends.middleware` → `backends.backends.middleware` in settings.py.
- Restructured `backends/data/communes.json`: key `communes` → `quartiers`, 11 cities, 223 quartiers, `{"ville":"Autre","quartiers":[]}`.
- Created `backends/core/views.py` with `GET /api/villes/` endpoint (reads JSON, `AllowAny`).
- Added `backends.core` to `INSTALLED_APPS`, wired `path("api/", include("backends.core.urls"))`.
- Added `autre_matiere` CharField to `ProfilEncadreur` model + migration + serializer.
- Updated `mon-profil/page.tsx`: checkbox for "Autre" matiere shows text input; sends `autre_matiere`.
- Updated `register/page.tsx`: phone input with +225 prefix, password eye toggles, villes/quartiers from API, "Autre" ville with `villeAutre` text input, submit sends `villeFinale`.
- Updated `login/page.tsx`: password eye toggle.
- Updated `encadreurs/page.tsx`: cascading Ville + Quartier selects from API, "Autre" ville shows text input (`villeAutre`), `villeFinale` in search query; added `matiereAutre` state + text input when "Autre" matière selected in search filter.
- Updated `lib/api.ts`: `getVilles()` uses `apiFetch`, `register()` normalizes phone with +225, error parsing uses `Object.values(err).flat().find(Boolean)`, added `matiere_nom` parameter to `getEncadreurs`.
- Added `"Autre"` to `matieres.json` and seeded.
- Added `matiere_nom` filter to `EncadreurListView` (filters `autre_matiere__icontains`).
- Set `DEFAULT_PERMISSION_CLASSES: IsAuthenticated` → added `AllowAny` on ville endpoint.
- Django system check passes, TypeScript compiles clean.
- Git: committed "petites modifications" (16 files), pushed to `origin/archi` via SSH (key passphrase `github`).
- Created branch `test` for unit tests, switched to it.
- Installed backend test deps: `pytest`, `pytest-django`, `pytest-cov`, `model-bakery`, `pytest-env`.
- Created `conftest.py` at project root with env vars (`PAYDUNYA_*`, `DJANGO_DEBUG=False`), `SECURE_SSL_REDIRECT=False`, shared fixtures (`api_client`, `parent_user`, `encadreur_user`, `encadreur_profile`, `matieres`, `encadreur_with_matieres`).
- **102 backend tests** — all passing (accounts, encadreurs, core, avis apps).
- Installed frontend test deps: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`, `msw`.
- Created `vitest.config.ts` with jsdom env, `tests/setup.ts`.
- Wrote **20 frontend tests** — all passing (`lib/api.ts` and `contexts/AuthContext.tsx`).
- Added `"test": "vitest run"` and `"test:watch": "vitest"` scripts to `frontends/package.json`.

### In Progress
- (none)

### Blocked
- (none)

## Key Decisions
- Villes data served from static JSON via Django API rather than DB model.
- "Autre" handling: separate state (`villeAutre`, `matiereAutre`) rather than mutating dropdown value.
- `apiFetch` used for `getVilles()` for consistent headers; endpoint marked `AllowAny`.
- `matiere_nom` query param filters `autre_matiere__icontains` for custom matière search.
- Test infrastructure: root `conftest.py` with `django.setup()` via `pytest-django`, lazy imports to avoid circular/early-load issues, `db` fixture on `api_client` to allow view database access.
- `settings.SECURE_SSL_REDIRECT = False` in conftest.py to prevent 301 redirects during tests.

## Next Steps
- Optionally run with `pytest-cov` for coverage report.
- Possibly update encadreurs suggestions (`SUGGESTIONS` array).

## Critical Context
- Phone validator on User model: `^\+225\d{10}$`.
- `SECURE_SSL_REDIRECT = True` in production settings causes 301 redirect in tests if not overridden.
- Django 6 `authenticate()` returns `None` for inactive users (via `user_can_authenticate`), so `Compte désactivé` branch is unreachable.
- Project root `/home/soro/mycd/` must be on `sys.path` (not `backends/`) for correct module resolution: `backends.backends.settings`.
- Outer `backends/__init__.py` must exist to avoid namespace-package conflicts.

## Relevant Files
- `/home/soro/mycd/backends/backends/settings.py`: MIDDLEWARE, INSTALLED_APPS, REST_FRAMEWORK config, SECURE_SSL_REDIRECT
- `/home/soro/mycd/backends/backends/urls.py`: includes all app URLs
- `/home/soro/mycd/backends/backends/middleware.py`: SecurityLoggingMiddleware
- `/home/soro/mycd/backends/core/views.py`, `urls.py`: `/api/villes/` endpoint
- `/home/soro/mycd/backends/data/communes.json`: 42 villes, 223 quartiers
- `/home/soro/mycd/backends/data/matieres.json`: 21 matières (including "Autre")
- `/home/soro/mycd/backends/encadreurs/models.py`: `ProfilEncadreur.autre_matiere`
- `/home/soro/mycd/backends/encadreurs/serializers.py`: `autre_matiere`, `matiere_ids` write-only
- `/home/soro/mycd/backends/encadreurs/views.py`: `matiere_nom` filter on `EncadreurListView`
- `/home/soro/mycd/backends/accounts/models.py`: phone validator, UserManager
- `/home/soro/mycd/backends/accounts/serializers.py`: RegisterSerializer
- `/home/soro/mycd/backends/accounts/views.py`: RegisterView, LoginView, MeView
- `/home/soro/mycd/backends/avis/models.py`: Avis, clean, notification on save
- `/home/soro/mycd/backends/avis/signals.py`: recalculates `note_moyenne`/`nombre_avis`
- `/home/soro/mycd/backends/avis/views.py`: AvisCreateView, AvisByEncadreurView, AvisDetailView
- `/home/soro/mycd/frontends/lib/api.ts`: `getVilles()`, `register()`, `login()`, `logout()`, `getEncadreurs()` with `matiere_nom`, `apiFetch` with token expiry check + auto-refresh
- `/home/soro/mycd/frontends/contexts/AuthContext.tsx`: AuthProvider with `useEffect` init from token, `redirectIfAuthenticated`, login/register/logout handlers
- `/home/soro/mycd/frontends/app/(auth)/register/page.tsx`: registration form
- `/home/soro/mycd/frontends/app/(auth)/login/page.tsx`: login form with eye toggle
- `/home/soro/mycd/frontends/app/encadreurs/page.tsx`: search/filter with ville+matiere "Autre" text inputs
- `/home/soro/mycd/frontends/app/mon-profil/page.tsx`: profile edit with "Autre" matiere input
- `/home/soro/mycd/conftest.py`: test config, env vars, shared fixtures
- `/home/soro/mycd/backends/accounts/tests/`: 9 test files (models, serializers, views)
- `/home/soro/mycd/backends/encadreurs/tests/`: 3 test files (models, serializers, views)
- `/home/soro/mycd/backends/core/tests/`: 1 test file (views)
- `/home/soro/mycd/backends/avis/tests/`: 2 test files (models, views)
- `/home/soro/mycd/frontends/tests/lib/api.test.ts`: API client tests (15 tests)
- `/home/soro/mycd/frontends/tests/contexts/AuthContext.test.tsx`: Auth provider tests (5 tests)
- `/home/soro/mycd/frontends/vitest.config.ts`: vitest configuration
- `/home/soro/mycd/backends/pytest.ini`: pytest configuration
- `/home/soro/mycd/backends/requirements.txt`: includes `pytest`, `pytest-django`, `pytest-cov`, `model-bakery`
