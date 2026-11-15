#!/usr/bin/env python3
"""Generate every city page (English and Spanish) from one template per language
and one data file.

    python3 build/city-pages/build.py          # write the pages
    python3 build/city-pages/build.py --check  # only report pages that would change

To add a city: add an entry to cities.json (copy an existing one and rewrite every
text field for the new city: local content is what keeps these pages from being
thin duplicates), then run the build. The new city also appears automatically in
the "Cities we serve" list of every other page.

To change the design of all city pages at once: edit templates/en.html and
templates/es.html (or assets/site.css) and run the build.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = 'https://hgdslidingdoor-repair.com'

LANG = {
    'en': {
        'path': 'sliding-glass-door-repair-{slug}.html',
        'url': SITE + '/sliding-glass-door-repair-{slug}',
        'href': 'sliding-glass-door-repair-{slug}',
        'other_href': 'es/reparacion-puertas-corredizas-{slug}',
        'crumbs': [('Home', SITE + '/'), ('Service areas', SITE + '/service-areas')],
        'gallery': {
            'h2': 'Recent work',
            'intro': 'Real jobs from our technician’s phone, around Central Florida. No stock photos.',
        },
    },
    'es': {
        'path': 'es/reparacion-puertas-corredizas-{slug}.html',
        'url': SITE + '/es/reparacion-puertas-corredizas-{slug}',
        'href': 'reparacion-puertas-corredizas-{slug}',
        'other_href': '../sliding-glass-door-repair-{slug}',
        'crumbs': [('Inicio', SITE + '/es/'), ('Áreas de servicio', SITE + '/es/areas-de-servicio')],
        'gallery': {
            'h2': 'Trabajos recientes',
            'intro': 'Trabajos reales, fotos del teléfono de nuestro técnico en Central Florida. Nada de fotos de stock.',
        },
    },
}

BUSINESS = json.load(open(os.path.join(HERE, "business.json"), encoding="utf-8"))  # per language


def load():
    data = json.load(open(os.path.join(HERE, 'cities.json'), encoding='utf-8'))
    gallery = json.load(open(os.path.join(HERE, 'gallery.json'), encoding='utf-8'))
    return data['cities'], gallery


def plain(fragment):
    """Visible HTML -> the plain text used inside JSON-LD."""
    return html.unescape(re.sub(r'<[^>]+>', '', fragment))


def ld(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False)


def schema(city, lang, page):
    cfg = LANG[lang]
    url = cfg['url'].format(slug=city['slug'])
    biz = dict(BUSINESS[lang])
    items = list(biz.items())
    # keep key order identical to the published pages: areaServed goes after knowsLanguage
    out = {}
    for k, v in items:
        out[k] = v
        if k == 'knowsLanguage':
            out['areaServed'] = city['area_served']
    faq = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': plain(f['q']),
         'acceptedAnswer': {'@type': 'Answer', 'text': f.get('a_schema') or plain(f['a'])}} for f in page['faqs']]}
    crumbs = [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u}
              for i, (n, u) in enumerate(cfg['crumbs'])]
    crumbs.append({'@type': 'ListItem', 'position': len(crumbs) + 1, 'name': plain(page['crumb']), 'item': url})
    bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': crumbs}
    return ld(out) + ld(faq) + ld(bc)


def services(page):
    return ('<section><div class="wrap two">\n'
            '<div><h2>%s</h2><ul class="dots">%s</ul></div>\n'
            '<div><h2>%s</h2><ul class="ticks">%s</ul></div>\n'
            '</div></section>') % (
        page['see_h2'], ''.join('<li>%s</li>' % x for x in page['see']),
        page['fix_h2'], ''.join('<li>%s</li>' % x for x in page['fix']))


def local_area(page):
    la = page.get('local_area')
    if not la:
        return ''
    return ('<section id="local-area"><div class="wrap two"><div><h2>%s</h2>%s</div>'
            '<div><h2>%s</h2><ul class="dots">%s</ul></div></div></section>\n') % (
        la['h2'], ''.join('<p>%s</p>' % p for p in la['paragraphs']),
        la['areas_h2'], ''.join('<li>%s</li>' % a for a in la['areas']))


def gallery_html(city, lang, gallery):
    """Photo strip. Photos tagged with this city come first; the rest fill up to 6."""
    photos = gallery['photos']
    mine = [p for p in photos if city['slug'] in p.get('cities', [])]
    rest = [p for p in photos if p not in mine and p.get('anywhere', True)]
    pick = (mine + rest)[:gallery.get('per_page', 6)]
    if not pick:
        return ''
    g = LANG[lang]['gallery']
    prefix = '../' if lang == 'es' else ''
    figs = []
    for p in pick:
        src = prefix + 'assets/work/' + p['file']
        figs.append(
            '<figure><a href="{full}" target="_blank" rel="noopener">'
            '<img src="{src}" srcset="{src} 640w, {full} 1280w" sizes="(max-width:700px) 50vw, 33vw" '
            'width="{w}" height="{h}" loading="lazy" decoding="async"{style} alt="{alt}"></a>'
            '<figcaption>{cap}</figcaption></figure>'.format(
                src=src.replace('.webp', '-640.webp'), full=src, w=p['w'], h=p['h'],
                style=' style="object-position:%s"' % p['focus'] if p.get('focus') else '',
                alt=html.escape(p['alt'][lang], quote=True), cap=p['caption'][lang]))
    return ('<section id="recent-work"><div class="wrap"><h2>%s</h2><p class="work-intro">%s</p>'
            '<div class="work">%s</div></div></section>\n') % (g['h2'], g['intro'], ''.join(figs))


def city_links(cities, me, lang):
    href = LANG[lang]['href']
    return ''.join('<li><a href="%s">%s <small>%s</small></a></li>' % (
        href.format(slug=c['slug']), c[lang].get('link_name', c['name']), c['area_label'][lang])
        for c in cities if c['slug'] != me['slug'])


def render(cities, city, lang, gallery, with_gallery=True):
    cfg = LANG[lang]
    page = city[lang]
    tpl = open(os.path.join(HERE, 'templates', lang + '.html'), encoding='utf-8').read()
    fill = {
        'SCHEMA': schema(city, lang, page),
        'TITLE': page['title'],
        'DESCRIPTION': page['description'],
        'URL_EN': LANG['en']['url'].format(slug=city['slug']),
        'URL_ES': LANG['es']['url'].format(slug=city['slug']),
        'OTHER_LANG_HREF': cfg['other_href'].format(slug=city['slug']),
        'CRUMB': page['crumb'],
        'H1': page['h1'],
        'LEAD': page['lead'],
        'SERVICES': services(page),
        'LOCAL_AREA': local_area(page),
        'GALLERY': gallery_html(city, lang, gallery) if with_gallery else '',
        'FAQ_ITEMS': ''.join('<details><summary>%s</summary><p>%s</p></details>' % (f['q'], f['a'])
                             for f in page['faqs']),
        'CITY_LINKS': city_links(cities, city, lang),
    }
    out = re.sub(r'\{\{([A-Z0-9_]+)\}\}', lambda m: fill[m.group(1)], tpl)
    return cfg['path'].format(slug=city['slug']), out


def main(argv):
    check = '--check' in argv
    with_gallery = '--no-gallery' not in argv
    cities, gallery = load()
    changed = 0
    for city in cities:
        for lang in LANG:
            rel, out = render(cities, city, lang, gallery, with_gallery)
            path = os.path.join(ROOT, rel)
            old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
            if old != out:
                changed += 1
                print(('would change ' if check else 'wrote ') + rel)
                if not check:
                    open(path, 'w', encoding='utf-8').write(out)
    print('%d of %d pages %s' % (changed, len(cities) * len(LANG), 'differ' if check else 'updated'))
    return 1 if (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
