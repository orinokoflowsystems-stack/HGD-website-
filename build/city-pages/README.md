# City pages generator

The 38 city pages (19 cities, English and Spanish) are generated. Do not edit
`sliding-glass-door-repair-*.html` or `es/reparacion-puertas-corredizas-*.html`
by hand: the next build overwrites them.

| File | What it holds |
| --- | --- |
| `templates/en.html`, `templates/es.html` | The page layout. Change these to redesign every city page at once. |
| `cities.json` | One entry per city: title, description, hero text, local notes, neighborhoods, FAQs (EN and ES). |
| `business.json` | The business details used in the structured data (schema.org), per language. |
| `gallery.json` | The "Recent work" photos. Files live in `assets/work/`. |
| `build.py` | Fills the templates. |

```
python3 build/city-pages/build.py           # rebuild all city pages
python3 build/city-pages/build.py --check   # list pages that are out of date
```

## Add a city

1. Copy an existing city in `cities.json` and rewrite **every** text field for the new
   city (hero, what we see, local notes, neighborhoods, FAQs). Pages that only swap the
   city name are what Google treats as doorway pages.
2. Run the build. The new city is added to the "Cities we serve" list on every page.
3. Add both URLs to `sitemap.xml` and link the city from `service-areas.html` and
   `es/areas-de-servicio.html`.

## Add job photos

1. Save the photo as `assets/work/<name>.webp` (1280 px on the long side) and
   `<name>-640.webp`, with location data (EXIF/GPS) removed.
2. Add it to `gallery.json` with English and Spanish captions and alt text.
3. Put the city slug in `cities` when you know where the job was: that photo then
   shows first on that city's page. `"anywhere": false` keeps a photo off the other
   cities. `focus` sets which part of the photo stays visible in the thumbnail.
