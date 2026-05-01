# EQAR DB

EQAR's internal contact and registration database. The stack is brought up with `docker compose up --build` and consists of a Django/DRF backend (`api/`), the UniDB vanilla-JS frontend (git submodule under `frontend/`), MariaDB, and an OpenLDAP service exposing the contact data over LDAP.

## `/stats/v1/` endpoints

Public, cached statistics endpoints (proxy-cached for 30 min by nginx). These are used for live charts shown on the EQAR website.

### Format

Each path accepts a `.<format>` suffix, use them as follows for different charting tools:

| Tool used         | Format suffix |
|-------------------|---------------|
| Datawrapper       | .csv          |
| Infogram/Prezi    | .infogram     |
| LibreOffice/Excel | .csv          |

There is also a default JSON (`.json`) format. It is currently not used by any charting tool, but only by the website for showing tables/content based on the API (e.g. list of current applications).

### Common date-range filter

Every endpoint marked **filterable** below accepts:

| Param        | Value                          | Notes |
|--------------|--------------------------------|-------|
| `date_from`  | ISO date `YYYY-MM-DD`          | Inclusive lower bound (`__gte`). |
| `date_to`    | ISO date `YYYY-MM-DD`          | Inclusive upper bound (`__lte`). |
| `date_field` | application date column        | Selects which date the window applies to, see list below. |

The possible values for `date_field` are:

| Field             | Date when |
|-------------------|-----------|
| `submitDate`      | Application was submitted to EQAR |
| `eligibilityDate` | Eligibility was confirmed by EQAR |
| `sitevisitDate`   | Site visit to the agency took place |
| `reportDate`      | Report was issued/finalised |
| `reportSubmitted` | Report was received by EQAR |
| `decisionDate`    | Final EQAR decision was taken |

Each endpoint has its own default field, see table below.

For year-axis endpoints, the year buckets are trimmed to the filter window: years outside `[date_from.year, date_to.year]` are dropped, years inside it with no matching data still appear as zero-count rows. Bad input returns `400`.

### Endpoints

All paths are to be prefixed by `/stats/v1/`.

The production instance runs at `https://db.app.eqar.eu/`.

Date filter parameters need to be added as: `?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD&date_field=ABC` (order does not matter and each parameter is optional)

A full example URL looks as follow:

<https://db.app.eqar.eu/stats/v1/esg/compliance-changed/by-year.csv/?date_from=2025-01-01&date_to=2026-12-31&date_field=applicationDate>

| Path | Returns | Filterable | Default `date_field` | Other params |
|------|---------|:---:|---|---|
| `esg/simple.<format>/` | Compliance / Partial / Non-compliance counts per active ESG standard | yes | `decisionDate` | — |
| `esg/extended.<format>/` | `esg/simple` broken down by application type, result, and year | yes | `decisionDate` | — |
| `esg/timeline-by-standard.<format>/` | Compliance levels per ESG standard, by year | yes | `decisionDate` | — |
| `esg/compliance-changed/by-year.<format>/` | Panel-vs-RC conclusion changes, by year (from 2016) | yes | `decisionDate` | — |
| `esg/compliance-changed/by-standard.<format>/` | Same, by ESG standard | yes | `decisionDate` | — |
| `esg/compliance-changed/by-panel.<format>/` | Same, per panel member (≥4 reviews) | yes | `decisionDate` | — |
| `esg/compliance-changed/by-rapporteur.<format>/` | Same, per RC rapporteur | yes | `decisionDate` | — |
| `applications/by-year.<format>/` | Decisions on applications and registered agencies, by year | yes | `decisionDate` | — |
| `applications/totals.<format>/` | Application counts per result, split Initial / Renewal | yes | `decisionDate` | — |
| `applications/duration/latest.<format>/` | Average days between application milestones, latest N applications | yes | `reportSubmitted` | `limit` (default `10`) |
| `applications/duration/by-year.<format>/` | Same, aggregated by year | yes | `reportSubmitted` | — |
| `applications/clarification-requests/by-year.<format>/` | Clarification-request counts, by year | yes | `decisionDate` | — |
| `applications/clarification-requests/by-standard.<format>/` | Clarification-request counts, by ESG standard | yes | `decisionDate` | — |

The following endpoints are for use on the EQAR website. They require authentication and cannot be used in external charting tools.

| Path | Returns | Parameters |
|------|---------|------------|
| `applications/open/` | List of currently open applications | DRF filterset: `type`, `stage`, `agency`, `secretary` |
| `applications/withdrawn/` | List of withdrawn applications | (none, full list) |
| `applications/precedents/` | Per-standard precedents with keywords / decisions | DRF filterset on `application__*`, `standard`, `rc`, `panel`; search on title/keywords |

### Examples

```bash
# Decisions per year, 2018–2021 only
curl 'https://.../stats/v1/applications/by-year/?date_from=2018-01-01&date_to=2021-12-31'

# Compliance per ESG standard, scoped by application submission date
curl 'https://.../stats/v1/esg/simple/?date_field=submitDate&date_from=2020-01-01&date_to=2022-12-31'

# Latest 5 application durations whose reports were submitted from 2023 onwards
curl 'https://.../stats/v1/applications/duration/latest/?limit=5&date_from=2023-01-01'
```
