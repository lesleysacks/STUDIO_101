# STUDIO101 JSON configuration

Routine layout, theme, navigation, page copy, and service catalog changes live in `config/content/`. Django still owns routing, permissions, forms, and the database. JSON never selects a template path and is never executed.

## Audit and baseline

The project is Django 5.2 on Python 3.12. Local development uses SQLite through `config.settings.local`. Production settings expect PostgreSQL environment variables and are unchanged. Installed packages are Django, Pillow, psycopg2-binary, django-environ, and WhiteNoise. There is no frontend framework.

Before this work the public site was a set of Django apps (`core`, `services`, `portfolio`, `studio`, `streams`, `bookings`) with hard-coded templates for navigation, footer, home, about, services, portfolio, studio, FAQ, and contact. Editable records already existed for site settings, hero slides, FAQs, services, projects, studio spaces, equipment, live streams, and booking requests. `manage.py check` was clean and the existing 27 tests passed. Gaps were the lack of a configuration layer, a booking form script that blocked the real POST, no lint configuration, and no automated coverage of theme or content structure.

Those models and the original templates remain. A broken or unpublished page definition falls back to the original template.

## Architecture

| Layer | Location | Responsibility |
| --- | --- | --- |
| JSON configuration | `config/content/` | Validated content, theme tokens, navigation, page sections, service catalog |
| Loading and validation | `apps/siteconfig/services/` | Parse, schema-check, cache, and resolve references |
| Rendering | `templates/siteconfig/` | Registered components only |
| Relational data | Existing apps | Admin-authored records. A database row wins over a JSON catalog entry with the same slug |
| Static files | `static/` | CSS, JavaScript, and images referenced as `ASSETS/...` |
| Tests | `apps/siteconfig/tests/` | Validation, rendering, cache, security, and import behaviour |

`apps/siteconfig` is the only new application. Views stay thin: they ask `render_configured_page` for a slug and pass the old template as a fallback.

### Precedence

1. Component schema defaults.
2. `site.json` `component_defaults` for that component type.
3. The page section `settings` object. A section replaces a whole key such as `primary_cta`; it does not deep-merge nested objects.
4. Database records replace JSON catalog entries that share a slug. Hero slides replace the JSON hero heading when an active slide exists. Contact email, phone, and address always come from `SiteSettings`.

`use_json_pages: false`, or `"published": false` on a page, renders the original template instead.

## Directory

```text
config/content/
  schemas/                  JSON Schemas, including schemas/components/
  site.json                 Global switches and component defaults
  theme.json                Brand tokens
  navigation.json           Header and footer links
  pages/                    One file per composed page
  services/                 Service catalog used for display and import
apps/siteconfig/            Loader, registry, commands, diagnostics
templates/siteconfig/       Shared page renderer and components
```

## What each file controls

| File | Controls |
| --- | --- |
| `site.json` | `use_json_pages`, content version, and default settings for components such as service grids and calls to action |
| `theme.json` | Colours, content width, section spacing, radii, and the heading/body font choice |
| `navigation.json` | Header links, the Book Now treatment, footer columns, blurb, and legal line |
| `pages/home.json` | Home section order: hero, live stream, facility highlights, featured services, portfolio, call to action |
| `pages/about.json` | Story, facility grid, call to action |
| `pages/services.json` | Service grid and the three published rate tiers |
| `pages/portfolio.json` | Showcase hero, gallery, call to action |
| `pages/studio.json` | Studio overview and facility cards |
| `pages/contact.json` | Contact copy and the enquiry form |
| `pages/faq.json` | FAQ hero and question list |
| `services/*.json` | Photography, podcast, music video, studio hire, and short film catalog entries |
| `schemas/*.json` | Allowed fields, types, and enumerations |

Portfolio items are still database records. Add `config/content/portfolio/<slug>.json` when a JSON catalog entry is useful; the portfolio schema is already in place. The gallery shows published projects, then the `fallback_items` in the page file when the database is empty.

## Validation

```bash
python manage.py validate_site_config
python manage.py validate_site_config --strict
```

`--strict` turns warnings, including a missing image, into a failure. Either way the command exits nonzero when the configuration is not safe to publish. Errors include the file, the JSON path, and the reason, for example `pages/about.json: $.title: This field is required.`

Django's system check reports the same errors as `siteconfig.E001`.

Other commands:

```bash
python manage.py import_site_content --kind services
python manage.py import_site_content --kind services --apply
python manage.py import_site_content --kind services --apply --update
python manage.py export_site_content --kind services --output /tmp/services.json
```

Import prints a plan and writes nothing until `--apply`. `--update` is required before an existing slug changes. Import never deletes a database row, and it does not replace an image that is already stored. Export refuses to overwrite an existing `--output` file and writes through a temporary file followed by an atomic replace.

Staff can open `/site-config/diagnostics/` to read the current validation result. The view is GET-only and does not edit files.

## Customizing without application code

Change the theme accent:

```json
{ "colors": { "accent": "#d4af37" } }
```

`theme.json` must keep the rest of the required colour and layout fields. Valid colours are `#RRGGBB`. Widths are a number plus `px`, `rem`, or `em`. Fonts are one of `cinzel`, `syne`, `inter`, `jakarta`, or `system`. The loader maps those tokens onto the CSS variables the stylesheets already use and injects them as `#site-theme`. Arbitrary CSS is rejected.

Reorder the home page by moving objects inside `pages/home.json` `sections`. Set `"enabled": false` to hide a section without deleting it. A section `type` must be one of the registered components: `hero`, `rich_text`, `text_image`, `feature_grid`, `service_grid`, `portfolio_gallery`, `video_embed`, `pricing`, `faq`, `cta`, `contact_enquiry`, `booking_enquiry`, `studio_facilities`, `live_stream`, `image_banner`.

Add a navigation item in `navigation.json`:

```json
{ "id": "contact", "label": "Contact", "href": "/contact/", "style": "link" }
```

`href` must be a site path or an `http`/`https` URL. `javascript:` URLs, protocol-relative URLs, and paths containing `..` fail validation.

A service file uses a stable `slug` that matches its filename. Set `published` and `is_featured` to control the grids. The public detail page reads the database first. When no row exists, the JSON entry is rendered. Run the import command when the catalog should become editable in the admin.

## Caching and failure behaviour

`get_bundle()` caches the validated bundle and rebuilds it when any JSON file under the root changes size or modification time. If a later read fails and a valid bundle was already loaded for that same root, the last valid bundle stays in use and the error is logged. The first request with no valid bundle raises, and page views fall back to the legacy templates. Broken production configuration is not replaced with invented page copy.

Do not commit secrets. API keys and database credentials stay in environment variables.

## Security

- Component templates are chosen from the registry, not from a path in JSON.
- Text is escaped by Django templates. Theme CSS is built only from validated tokens and is the only `|safe` insertion.
- Video URLs in JSON must be `https` on YouTube, Vimeo, Facebook, or Twitch. Admin live-stream embeds must be `https` and cannot target localhost.
- Media references must stay under `static/ASSETS/` and cannot contain `..`.
- Booking and contact forms keep CSRF, server-side validation, and a honeypot field. A filled honeypot is rejected and nothing is saved.
- Diagnostics require a staff account.

## Deploy, rollback, and recovery

1. Edit the JSON on a branch.
2. Run `python manage.py validate_site_config --strict` and `python manage.py test`.
3. Deploy the revision the way the site is already deployed. No new migration is required for this layer.
4. Restart the application process so a long-lived process drops its cache. A development server reloads on its own.

To roll back, deploy the previous revision. Existing database rows are left in place. If an import with `--apply --update` changed rows you need to restore, use a database backup or the previous export file. Export before a large import.

If a file is invalid after deploy, the process keeps serving the last valid bundle loaded in that process and logs `siteconfig` errors. Fix the file or roll back the revision. There is no automatic rewrite of JSON.

## Limitations

- New component types still need a registry entry, a schema, a template, and a resolver.
- Portfolio filtering with `?category=` still uses the original portfolio template. The default portfolio page is JSON-driven.
- Live stream and booking pages stay on their specialized templates.
- JSON services appear on the public site and in the sitemap before they are imported, but the admin does not edit the JSON files directly.
- The configuration cache is per process. Multiple processes each keep their own last-valid bundle until restart.
