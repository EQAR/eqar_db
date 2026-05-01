# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack overview

EQAR's internal contact/registration database. Four cooperating services wired together by `docker-compose.yaml`:

- **backend** (`api/`) — Django 3.1 + DRF, served by gunicorn. The Django project is `eqar_db` with apps `uni_db`, `contacts`, `members`, `agencies`, `stats`, `ldap_view`.
- **db** — MariaDB 10. The schema is bootstrapped from `initdb.d/*.sql` on first start; Django migrations run with `--fake-initial` because tables already exist.
- **frontend** (`frontend/`) — UniDB, a generic vanilla-JS / jQuery client (git submodule, branch `django-backend`). Pure static files served by nginx. No build step.
- **ldap** (`slapd/`) — OpenLDAP using the `back-sql` backend over ODBC against the same MariaDB. NB: This is only for exposing the contact database read-only via LDAP, e.g. for use in email clients. Authentication for Django also uses LDAP, but through an external LDAP server.

`nginx.conf` (the `frontend` container) serves the static UniDB files at `/`, exposes Django at `/api`, `/admin`, `/stats`, `/phonebook.xml`, and proxy-caches `/stats` for 30 min.

## Commands

```bash
# bring up the full stack (override file enables local-dev: settings_local.py mount, exposed db port, dev-link network)
docker compose up --build

# Django management — always go through the backend container
docker compose exec backend python manage.py <cmd>
docker compose exec backend python manage.py migrate --fake-initial
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py deqarsync          # pull updates from DEQAR API into local agencies
docker compose exec backend python manage.py importdecisions <csv>

# running Django outside Docker (against the dockerised db on :3306):
cd api && source set-local-env.sh && python manage.py runserver
```

There is **no test suite and no linter configured** — `tests.py` files are stubs. Don't claim "tests pass"; verify behaviour by hitting the API or the UniDB UI.

`docker-compose.override.yml` is committed (unusually) and is what enables local development: it mounts `settings_local.py` into the backend, exposes the DB port, and joins a `dev-link` external network so a host-side dev frontend can talk to `eqar-db-backend`.

## Architecture: how UniDB generates the API

The whole point of `uni_db/` is **metaprogramming over Django models**. A single registry drives the API and the frontend's table list:

- `api/uni_db/views_meta.py` defines `class UniDB` with a `Tables = [...]` list of viewsets. `UniDB.table_path()` registers them on a `DefaultRouter`; `UniDB.table_list()` introspects each viewset's serializer and returns a JSON description (columns, labels, primary key, allowed actions, search/global-search flags) at `GET /api/v3/system/tables/`. The frontend reads that one endpoint and renders an entire CRUD UI dynamically — there is no per-table frontend code.
- `UniModelViewSet` (`uni_db/views.py`) auto-generates four serializer variants per model — list / search / download / detail-read / nested / detail-write — by subclassing `ListSerializer` / `DetailSerializer` and copying `Meta` from declared `list_fields`, `extra_kwargs`, `limit_choices_to`, etc. Adding a viewset to `UniDB.Tables` is normally enough to expose a new model end-to-end.
- `ReadWriteSerializerMixin` (`uni_db/mixins.py`) routes GET vs POST/PUT to different serializers; `DetailSerializer.validate()` calls the model's `clean()` so validation lives on the model.
- `SearchFacetPagination` (`uni_db/filters.py`) augments paginated responses with per-field facet counts derived from the active `FilterSet`. `FilterBackend` adds `EnumField` support to `DjangoFilterBackend`.
- `RawQuery` model + `QueryViewset` let users save arbitrary `SELECT` SQL and run it through the API at `/api/v3/query/<uuid>/` with pagination, ordering, and `%s` substitution for search. Non-SELECT statements are rejected; `/* … %s … */` comments are stripped when no search term is supplied.

When adding a new model:
1. Define the Django model. Use `EnumField` (`uni_db/fields.py`) for MySQL `ENUM` columns and set `db_column=` to match the legacy schema in `initdb.d/0001_eqar.sql`.
2. Create a `UniModelViewSet` in the relevant app's `views.py`. Set `list_fields`, `search_fields`, `filterset_fields`, `relations_count` (for the detail `_related` block), and optionally `limit_choices_to`, `unidb_options` (`readonly`, `hidden`, `create`, `update`, `delete`, `includeGlobalSearch`).
3. Register it in `UniDB.Tables` in `api/uni_db/views_meta.py`. The frontend will pick it up automatically.

## Per-app notes

- **agencies/** — Core registration domain. `Applications.save()` auto-derives `previous` (most recent prior application for the same agency) and, for Focused/Targeted reviews, copies `panel_/rapp_/rc_` fields from the previous application when the matching `inherit_*` flag is set. It also writes through to `ApplicationStandard` rows. `Applications.clean()` enforces stage-progression rules (e.g. stage ≥ 4 requires per-ESG compliance fields). `EsgVersion.active=True` selects the live ESG list — there is exactly one active version at a time. The `deqarsync` management command uses `deqarclient` to push local agency contact/address changes back to DEQAR.
- **contacts/** — `Contact.save()` auto-builds `person`/`nameEmail` and normalises `phone`/`mobile` via `phonenumbers` (default region `BE`). `Organisation.get_readonly_fields()` locks fields once linked to a DEQAR-registered agency.
- **stats/** — Public, cached statistics endpoints under `/stats/v1/`. `StatsView` is a generic base; subclasses set a `queryset`, `x_range`, `field_labels`, and implement `filter_queryset_by_x()` + `stats()`. Custom renderers in `stats/renderers.py` produce CSV and Infogram-shaped JSON in addition to JSON.
- **ldap_view/** — Models map onto the slapd `back-sql` mapping tables (`ldap_oc_mappings`, `ldap_attr_mappings`, `ldap_entry_objclasses`, `ldap_referrals`) so admins can edit how DB rows expose as LDAP entries.
- **eqar_db/** — `settings.py` chains `settings_base.py` + optional `settings_local.py` via `django-split-settings`. `BearerAuthentication` is just `TokenAuthentication` with the `Bearer` keyword. Default DRF permission is `IsSuperUser`; viewsets typically loosen this to `IsAuthenticated & (IsSuperUser | AllowReadOnly)`.

## Conventions and gotchas

- **`db_column` everywhere** — most models inherit a legacy hand-written schema, so column names rarely match Python attribute names. When adding fields, pick whichever is appropriate; when reading models, don't assume the DB column name.
- **`--fake-initial` is required** — the initial migrations are derived from the legacy schema and would otherwise re-create existing tables. The Dockerfile CMD already does this. Never run `migrate` without it on a fresh DB.
- **LDAP is the source of truth for users.** `AUTHENTICATION_BACKENDS` lists `ModelBackend` first (for a local superuser fallback) and `LDAPBackend` second. Group memberships in LDAP set `is_staff` / `is_superuser` via `AUTH_LDAP_USER_FLAGS_BY_GROUP`.
- **Frontend is a submodule** — `frontend/` points to `git@github.com:ctueck/UniDB.git` branch `django-backend`. Don't commit changes inside `frontend/` without coordinating in that repo.
- **`.env` and `settings_local.py` in the repo are dev-only** placeholders with throwaway secrets. Real deployments inject `DJANGO_SECRET_KEY`, `DJANGO_DB_PASS`, `DJANGO_HOSTNAME`, `DEQAR_BASE`, `DEQAR_TOKEN` via the environment.
- **Architecture pin on slapd image** — `slapd/Dockerfile` forces `linux/amd64` because `odbc-mariadb` has no arm64 build. On Apple Silicon expect emulation.
