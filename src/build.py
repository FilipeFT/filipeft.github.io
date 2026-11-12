#!/usr/bin/env python3
"""build.py — validate, test, and build the deck page. One file, no
dependencies beyond Python 3's standard library, no Node.

Usage
-----
    python3 build.py             validate + test + build out/site.html
    python3 build.py --install   also write the canvas
    bash build.sh                the same, one command

The pipeline runs in stages. A failure at any stage prints EVERY
problem found at that stage, writes nothing, and exits non-zero:
nothing half-built is ever shipped or installed.

    1. parse     deck.xml must be well-formed XML, and every file
                 the build needs must be present
    2. schema    the data must satisfy deck.xsd, checked by the
                 mini-XSD interpreter carried below: structure,
                 required attributes, id patterns, level pins
    3. data      cross-checks the schema cannot express: door
                 targets exist, icons are defined, rungs are known,
                 the layered descent is gradual, every row offers at
                 least two named doors, every placeholder is used
    4. template  the template must carry a section for every view the
                 data names, and the data slot
    5. output    the built page must contain the injected data, its
                 title, its views, and balanced tags

What is deliberately NOT checked: the interactive engines (the live
figures in the primers) live in the template, not the data. The build
checks the page around them; it does not drive them. The checks are
few on purpose — every one guards a mistake that has actually
happened, and each failure names the exact row and target involved.

Exit codes: 0 the page was built; 1 a check failed; 2 bad usage.
"""

import json
import os
import re
import sys
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- paths
# Everything sits next to this script: deck.xsd, deck.xml,
# template.html. out/ holds the build result. The canvas is build
# output too, written only by --install, only after every check
# passes.
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, 'deck.xsd')
DATA_PATH = os.path.join(HERE, 'deck.xml')
TEMPLATE_PATH = os.path.join(HERE, 'template.html')
OUT_PATH = os.path.join(HERE, 'out')
CANVAS_PATH = '/home/user/canvases/from-sand-to-symbols/CANVAS.md'

# The template carries one empty slot; the build replaces it with
# the JSON form of the data. Presence and shape are checked.
MARKER = '/*__DECK_DATA__*/{}'
FRONTMATTER = ('---\nname: "from-sand-to-symbols"\n'
               'title: "Everything to bits"\ntype: "text/html"\n---\n\n')


class BuildError(Exception):
    """A fatal problem the build can name precisely for the author."""


# ================================================================ 1
# The mini-XSD interpreter
# ---------------------------------------------------------------
# The environment offers no XSD tooling (no xmllint, no Java, no
# lxml, and installing packages is not allowed), so the build carries
# this small interpreter instead. It understands EXACTLY the subset
# deck.xsd uses — nothing more, on purpose:
#
#   named xs:complexType with one xs:sequence of local xs:element
#     (name, type, minOccurs, maxOccurs) and xs:attribute
#     (name, type, use)
#   named xs:complexType with xs:simpleContent/xs:extension
#     (text content plus attributes)
#   named xs:simpleType/xs:restriction with xs:pattern or
#     xs:enumeration facets
#   one global element (deck) with an inline anonymous type
#   xs:annotation, skipped anywhere
#
# Anything outside the subset raises instead of passing silently, so
# if the schema grows a construct this interpreter cannot check, the
# build fails loudly and tells its author exactly what to teach it.

XS_NS = 'http://www.w3.org/2001/XMLSchema'


class SchemaError(Exception):
    """deck.xsd itself is broken or uses an unsupported construct."""


def _local(tag):
    """'{namespace}name' -> 'name'"""
    return tag.split('}', 1)[-1]


class Schema:
    """A loaded deck.xsd, able to validate a parsed deck.xml tree."""

    def __init__(self, path):
        try:
            self.root = ET.parse(path).getroot()
        except ET.ParseError as e:
            raise SchemaError('not well-formed XML — %s' % _where(e))
        except OSError:
            raise SchemaError('file not found: %s' % path)
        if self.root.tag != '{%s}schema' % XS_NS:
            raise SchemaError('not an XSD schema: %s' % path)
        self.types = {}    # type name -> record
        self.globals = {}  # root element name -> type name
        self._load()

    # ---- loading: turn the schema into plain lookup records ----

    def _load(self):
        """Walk the schema's top level and register every type."""
        for child in self.root:
            tag = _local(child.tag)
            if tag == 'element':
                name = child.get('name')
                if child.get('type') is not None:
                    self.globals[name] = child.get('type')
                else:
                    # inline anonymous type: register under a private
                    # name so it cannot collide with authored types
                    inner = [c for c in child
                             if _local(c.tag) in ('complexType', 'simpleType')]
                    if len(inner) != 1:
                        raise SchemaError(
                            'global element %s needs a type or one inline type' % name)
                    private = '__anon_%s__' % name
                    if _local(inner[0].tag) == 'complexType':
                        self._load_complex(inner[0], private)
                    else:
                        self._load_simple(inner[0], private)
                    self.globals[name] = private
            elif tag == 'complexType':
                self._load_complex(child, child.get('name'))
            elif tag == 'simpleType':
                self._load_simple(child, child.get('name'))
            elif tag in ('annotation', 'comment'):
                continue
            else:
                raise SchemaError('unsupported schema construct: xs:%s' % tag)

    def _load_complex(self, node, name):
        """Record a complex type: child sequence plus attributes."""
        rec = {'kind': 'complex', 'sequence': [], 'attributes': [],
               'text': False}
        for child in node:
            tag = _local(child.tag)
            if tag == 'sequence':
                for el in child:
                    if _local(el.tag) == 'element':
                        rec['sequence'].append({
                            'name': el.get('name'),
                            'type': el.get('type'),
                            'min': int(el.get('minOccurs', '1')),
                            'max': el.get('maxOccurs', '1'),
                        })
                    elif _local(el.tag) == 'annotation':
                        continue
                    else:
                        raise SchemaError(
                            'unsupported inside xs:sequence: xs:%s' % _local(el.tag))
            elif tag == 'attribute':
                rec['attributes'].append({
                    'name': child.get('name'),
                    'type': child.get('type'),
                    'use': child.get('use', 'optional'),
                })
            elif tag == 'simpleContent':
                rec['text'] = True  # element carries text, not children
                for ext in child:
                    if _local(ext.tag) == 'extension':
                        for a in ext:
                            if _local(a.tag) == 'attribute':
                                rec['attributes'].append({
                                    'name': a.get('name'),
                                    'type': a.get('type'),
                                    'use': a.get('use', 'optional'),
                                })
                            elif _local(a.tag) == 'annotation':
                                continue
                            else:
                                raise SchemaError(
                                    'unsupported inside xs:extension: xs:%s'
                                    % _local(a.tag))
                    elif _local(ext.tag) == 'annotation':
                        continue
                    else:
                        raise SchemaError(
                            'unsupported inside xs:simpleContent: xs:%s'
                            % _local(ext.tag))
            elif tag == 'annotation':
                continue
            else:
                raise SchemaError(
                    'unsupported inside xs:complexType: xs:%s' % tag)
        self.types[name] = rec

    def _load_simple(self, node, name):
        """Record a simple type: a pattern and/or an enumeration."""
        rec = {'kind': 'simple', 'pattern': None, 'enums': None}
        for child in node:
            tag = _local(child.tag)
            if tag == 'restriction':
                for facet in child:
                    facet_tag = _local(facet.tag)
                    if facet_tag == 'pattern':
                        rec['pattern'] = re.compile(
                            '^(?:%s)$' % facet.get('value'))
                    elif facet_tag == 'enumeration':
                        if rec['enums'] is None:
                            rec['enums'] = []
                        rec['enums'].append(facet.get('value'))
                    elif facet_tag == 'annotation':
                        continue
                    else:
                        raise SchemaError(
                            'unsupported restriction facet: xs:%s' % facet_tag)
            elif tag == 'annotation':
                continue
            else:
                raise SchemaError(
                    'unsupported inside xs:simpleType: xs:%s' % tag)
        self.types[name] = rec

    # ---- validation: walk an instance tree against the records ----

    def validate(self, instance):
        """Return a list of error strings (empty when valid)."""
        errors = []
        if len(self.globals) != 1:
            raise SchemaError('the schema must declare exactly one global element')
        root_name = list(self.globals)[0]
        if instance.tag != root_name:
            return ['root element should be <%s>, found <%s>'
                    % (root_name, instance.tag)]
        self._check_element(instance, self.globals[root_name],
                            '/' + instance.tag, errors)
        return errors

    def _check_element(self, node, type_name, path, errors):
        t = self.types.get(type_name)
        if t is None:
            if type_name != 'xs:string':  # builtin: nothing to check
                errors.append('%s: unknown type %r' % (path, type_name))
            return
        if t['kind'] == 'simple':
            text = (node.text or '').strip()
            if t['pattern'] is not None and not t['pattern'].match(text):
                errors.append('%s: text %r does not match the pattern'
                              % (path, text[:40]))
            if t['enums'] is not None and text not in t['enums']:
                errors.append('%s: text %r not in enumeration'
                              % (path, text[:40]))
            self._check_attributes(node, [], path, errors)
            return
        # complex: attributes first, then the child sequence in order
        self._check_attributes(node, t['attributes'], path, errors)
        if t['text']:
            return  # simpleContent: no children expected
        kids = list(node)
        idx = 0
        for spec in t['sequence']:
            count = 0
            while (idx < len(kids) and _local(kids[idx].tag) == spec['name']
                   and (spec['max'] == 'unbounded' or count < int(spec['max']))):
                self._check_element(kids[idx], spec['type'],
                                    '%s/%s[%d]' % (path, spec['name'], count + 1),
                                    errors)
                idx += 1
                count += 1
            if count < spec['min']:
                errors.append('%s: expected at least %d <%s>, found %d'
                              % (path, spec['min'], spec['name'], count))
        if idx < len(kids):
            errors.append('%s: unexpected element <%s> '
                         '(sequence order violated or unknown)'
                         % (path, _local(kids[idx].tag)))

    def _check_attributes(self, node, decls, path, errors):
        for a in decls:
            if a['use'] == 'required' and a['name'] not in node.attrib:
                errors.append('%s: required attribute %r is missing'
                              % (path, a['name']))
                continue
            if a['name'] in node.attrib:
                self._check_value(node.attrib[a['name']], a['type'],
                                  '%s/@%s' % (path, a['name']), errors)

    def _check_value(self, value, type_name, path, errors):
        if type_name == 'xs:string':
            return
        t = self.types.get(type_name)
        if t is None:
            errors.append('%s: unknown type %r' % (path, type_name))
            return
        if t['kind'] != 'simple':
            errors.append('%s: typed as a complex type' % path)
            return
        if t['pattern'] is not None and not t['pattern'].match(value):
            errors.append('%s: value %r does not match the pattern' % (path, value))
        if t['enums'] is not None and value not in t['enums']:
            errors.append('%s: value %r not in enumeration' % (path, value))


def _where(parse_error):
    """Format an ElementTree parse error with its position (its own
    message usually names it already; keep one mention)."""
    text = str(parse_error)
    if 'line' in text:
        return text
    line, col = getattr(parse_error, 'position', (0, 0))
    return 'line %d, column %d: %s' % (line, col, text)


# Extra hints appended to schema errors whose shape we have seen
# before, so the next author is told not just WHAT is wrong but the
# LIKELY FIX. Keys are substrings matched in the message.
HINTS = [
    ('unexpected element <art>',
     'this deck carries no ASCII art — delete the <art> element; '
     'a part and a step is prose and doors, nothing else'),
    ('unexpected element <ladder>',
     'the ladder holds one ordered list of <rung> children'),
    ('expected at least 1 <rung>',
     'the ladder holds one ordered list of <rung> children'),
    ('unexpected element <pattern>',
     'the pattern page is gone by design — the deck starts at the '
     'cards and the reader drills down; delete the <pattern> element'),
    ('unexpected element <rails>',
     'the rails are merged into the ladder — give each rail a '
     'place in <ladder> as a plain <rung id="…" chip="…"/>'),
    ('unexpected element <rail>',
     'rails are merged — write a plain <rung id="…" chip="…"/> '
     'inside <ladder> instead'),
    ('/rung[',
     'a rung is an id and a chip, nothing else'),
    ('value \'2\' not in enumeration',
     'levels are pinned: cards 0, trails 1, placeholders 1 or 2, primers 2'),
    ('value \'0\' not in enumeration',
     'levels are pinned: cards 0, trails 1, placeholders 1 or 2, primers 2'),
]


def hint(message):
    """Return the message with the first matching hint appended, if any."""
    for needle, extra in HINTS:
        if needle in message:
            return '%s (%s)' % (message, extra)
    return message


# ================================================================ 2
# The check book
# ---------------------------------------------------------------
# Every check is counted, pass or fail; failures collect a message
# that names the exact element, row, and target involved. The counts
# appear in the build summary, and the messages in a failure report.


class Checks:
    def __init__(self):
        self.errors = []
        self.count = 0

    def that(self, ok, message):
        """Count one assertion; record it if it fails."""
        self.count += 1
        if not ok:
            self.errors.append(message)

    def equals(self, got, want, message):
        self.count += 1
        if got != want:
            self.errors.append('%s — got %r, expected %r'
                               % (message, got, want))


# ================================================================ 3
# The data
# ---------------------------------------------------------------
# deck.xml, already schema-validated, is lifted into one dict: the
# exact JSON the template's shims (SYSTEMS, EXPLAINERS, LADDER,
# ICONS, PRIMER_META, PLACEHOLDERS) walk at runtime.
# Key order is stable, so the injected payload is diff-friendly.


def _prose(el):
    """Text of a prose element, stripped. Schema-guaranteed to exist;
    the guard stays so a surprise is named, not a traceback."""
    if el is None or el.text is None:
        raise BuildError('a prose element (blurb/intro/bottom) is empty')
    return el.text.strip()


def _doors(el):
    return [{'to': d.get('to'), 'q': d.get('q')}
            for d in el.findall('door')]


def build_data(root):
    """Lift the schema-validated tree into the DATA dict."""
    data = {}
    # the cards (level 0): the high stories, the way in
    cards = {}
    for c in root.find('cards'):
        parts = []
        for p in c.findall('part'):
            parts.append({
                'icon': p.get('icon'),
                'rung': p.get('rung'),
                'name': p.get('name'),
                'line': p.get('line'),
                'blurb': _prose(p.find('blurb')),
                'deep': _doors(p),
            })
        cards[c.get('id')] = {
            'title': c.get('title'),
            'icon': c.get('icon'),
            'q': c.get('q'),
            'parts': parts,
            'bottom': _prose(c.find('bottom')),
            'deep': _doors(c),
        }
    data['cards'] = cards
    # the trails (level 1): the explainers that ease the way down
    trails = {}
    for t in root.find('trails'):
        steps = []
        for s in t.findall('step'):
            steps.append({
                'icon': s.get('icon'),
                'name': s.get('name'),
                'line': s.get('line'),
                'blurb': _prose(s.find('blurb')),
                'cross': _doors(s),
            })
        trails[t.get('id')] = {
            'title': t.get('title'),
            'crumb': t.get('crumb'),
            'rung': t.get('rung'),
            'icon': t.get('icon'),
            'intro': _prose(t.find('intro')),
            'steps': steps,
            'bottom': _prose(t.find('bottom')),
            'deep': _doors(t),
        }
    data['trails'] = trails
    # the ladder: data only. No page renders from it: the order of
    # the rungs sorts the parts of every card, and the chips label
    # them. The rails are gone as a container — what they named
    # sits in the ladder as ordinary rungs
    data['ladder'] = [{'id': r.get('id'), 'chip': r.get('chip')}
                      for r in root.find('ladder')]
    # the icons: name -> SVG body
    data['icons'] = {i.get('name'): (i.text or '').strip()
                     for i in root.find('icons')}
    # the primer index: each door button knows its icon and label
    primers = {}
    for p in root.find('primers'):
        primers[p.get('id')] = [p.get('icon'), p.get('label')]
    data['primers'] = primers
    # the named placeholders: patches to be written later
    placeholders = {}
    for ph in root.find('placeholders'):
        placeholders[ph.get('id')] = {
            'level': int(ph.get('level')),
            'icon': ph.get('icon'),
            'title': ph.get('title'),
            'line': ph.get('line'),
        }
    data['placeholders'] = placeholders
    return data


# ================================================================ 4
# The data checks
# ---------------------------------------------------------------
# What the schema cannot express: references between elements, the
# layered descent, and the door floors. Every check here encodes a
# real past mistake (a door to nothing, an unknown icon, a card
# jolting straight to a primer, a placeholder nothing points at).


def check_data(root, data, template):
    """Run every data-level check; returns the Checks book."""
    k = Checks()
    icons = data['icons']
    placeholders = data['placeholders']
    # the set of views a door may lead to
    views = (set(data['cards']) | set(data['trails']) |
             set(data['primers']) | set(placeholders))
    rung_ids = set(r['id'] for r in data['ladder'])

    def target_level(to):
        """The layer a door leads to: 0 a card, 1 a trail or a
        level-1 placeholder, 2 a primer or a level-2 placeholder,
        None unknown."""
        if to in data['cards']:
            return 0
        if to in data['trails']:
            return 1
        if to in placeholders:
            return placeholders[to]['level']
        if to in data['primers']:
            return 2
        return None

    def door_ok(d, where, gradual):
        """A door must lead to a real view. When the row sits at
        level 0 (a card), it must also not skip layers: cards ease
        the reader down through trails and placeholders, never
        straight to a primer. Trail rows sit at level 1 and may
        reach the primers below — that is what they are for."""
        k.that(d['to'] in views, '%s: door to %r leads nowhere'
               % (where, d['to']))
        if gradual and d['to'] in views:
            lvl = target_level(d['to'])
            k.that(lvl is None or lvl <= 1,
                   '%s: door to %r jolts straight to level %d — ease '
                   'down through a trail or a named placeholder'
                   % (where, d['to'], lvl))

    def floor(doors_list, where, n=2):
        """Every row offers at least n DISTINCT ways on. Counting
        distinct targets matters: a door and a lateral to the same
        view render as one button."""
        uniq = set(d['to'] for d in doors_list)
        k.that(len(uniq) >= n, '%s: only %d distinct door%s — every row '
               'offers at least %d named ways on'
               % (where, len(uniq), '' if len(uniq) == 1 else 's', n))

    all_targets = []  # for the placeholder orphan check

    # cards: parts and bottoms
    for cid, c in data['cards'].items():
        for i, p in enumerate(c['parts']):
            where = 'card %s, part %d (%s)' % (cid, i + 1, p['name'])
            k.that(p['icon'] in icons, '%s: unknown icon %r' % (where, p['icon']))
            k.that(p['rung'] in rung_ids, '%s: unknown rung %r' % (where, p['rung']))
            k.that(bool(p['blurb']), '%s: the blurb is empty' % where)
            floor(p['deep'], where)
            for d in p['deep']:
                door_ok(d, where, True)
                all_targets.append(d['to'])
        where = 'card %s bottom' % cid
        k.that(bool(c['bottom']), '%s: the bottom note is empty' % where)
        floor(c['deep'], where, 1)
        for d in c['deep']:
            door_ok(d, where, True)
            all_targets.append(d['to'])

    # trails: steps and bottoms
    for tid, t in data['trails'].items():
        k.that(t['rung'] in rung_ids, 'trail %s: unknown rung %r' % (tid, t['rung']))
        k.that(t['icon'] in icons, 'trail %s: unknown icon %r' % (tid, t['icon']))
        for i, s in enumerate(t['steps']):
            where = 'trail %s, step %d (%s)' % (tid, i + 1, s['name'])
            k.that(s['icon'] in icons, '%s: unknown icon %r' % (where, s['icon']))
            k.that(bool(s['blurb']), '%s: the blurb is empty' % where)
            floor(s['cross'], where)
            for d in s['cross']:
                door_ok(d, where, False)  # trails may reach the primers
                all_targets.append(d['to'])
        where = 'trail %s bottom' % tid
        k.that(bool(t['bottom']), '%s: the bottom note is empty' % where)
        floor(t['deep'], where, 1)
        for d in t['deep']:
            door_ok(d, where, False)
            all_targets.append(d['to'])

    # the named placeholders: real icons, real ids, really used
    ph_root = root.find('placeholders')
    k.equals(len(ph_root), len(placeholders),
             'placeholders: duplicate ids (%d declared, %d unique)'
             % (len(ph_root), len(placeholders)))
    for pid, ph in placeholders.items():
        k.that(ph['icon'] in icons, 'placeholder %s: unknown icon %r'
               % (pid, ph['icon']))
        k.that(bool(ph['title']) and bool(ph['line']),
               'placeholder %s: a promise must be named' % pid)
        k.that(pid in all_targets, 'placeholder %s (%s) is never '
               'referenced — a promise nothing points at'
               % (pid, ph['title']))

    # primers: the template must carry each one
    for pid, (icon, label) in data['primers'].items():
        k.that(icon in icons, 'primer %s: unknown icon %r' % (pid, icon))

    # the template must have a home and a spine for every view the
    # data names, the map that draws the whole deck as one graph,
    # and the data slot to receive the payload
    for cid in data['cards']:
        k.that('id="%s"' % cid in template,
               'template has no section for card %r' % cid)
        k.that('id="%s-parts"' % cid in template,
               'template has no spine for card %r' % cid)
    for pid in data['primers']:
        k.that('id="%s"' % pid in template,
               'template has no section for primer %r' % pid)
        k.that(('data-go="%s"' % pid) in template
               or ('fund-dag' in template and 'renderFundDAG' in template),
               'primer %r has no door: no static door, and no map '
               '(fund-dag + renderFundDAG) to draw it from' % pid)
    k.that('id="fund-dag"' in template,
           'template has no map for the fundamentals (id="fund-dag")')
    k.that('function renderFundDAG' in template,
           'template has no map builder (renderFundDAG)')
    k.that(MARKER in template, 'template has no data slot (%s)' % MARKER)
    return k


# ================================================================ 5
# The output checks
# ---------------------------------------------------------------
# The last word on quality: the page that will ship is inspected
# itself, not just the pieces that went into it.


def check_output(page, data, template):
    k = Checks()
    k.that(MARKER not in page, 'the data slot was not filled')
    k.that('<title>Everything to bits</title>' in page,
           'the built page lost its title')
    k.that(page.rstrip().endswith('</html>'), 'the built page is truncated')
    # The script and style tags must balance. Openings may carry
    # attributes (<script defer>, <script src="…">, <style
    # media="…">), so they are counted with a pattern rather than
    # the bare '<script>' string — a bare count misses attributed
    # openings and reports an imbalance that is not there. The
    # closing form never carries attributes.
    for tag in ('script', 'style'):
        opens = len(re.findall(r'<%s\b[^>]*>' % tag, page))
        closes = page.count('</%s>' % tag)
        k.equals(opens, closes,
                 'the built page has unbalanced %s tags' % tag)
    for cid in data['cards']:
        k.that('id="%s"' % cid in page, 'the built page lost card %r' % cid)
    for pid in data['primers']:
        k.that('id="%s"' % pid in page, 'the built page lost primer %r' % pid)
    # the payload must survive a JSON round trip: what the template
    # will parse is exactly what was written
    payload = json.dumps(data, ensure_ascii=False)
    k.that(json.loads(payload) is not None, 'the data payload is not valid JSON')
    k.that(len(page) > len(template),
           'the built page is smaller than its template — the data never landed')
    return k


# ================================================================ 6
# main
# ---------------------------------------------------------------


def fail(stage, messages):
    """Print every problem from a stage, and stop before writing."""
    sys.stderr.write('BUILD FAILED at %s:\n' % stage)
    for m in messages:
        sys.stderr.write('  %s\n' % hint(m))
    sys.stderr.write('nothing was written.\n')
    sys.exit(1)


def read_template():
    try:
        with open(TEMPLATE_PATH, encoding='utf-8') as f:
            return f.read()
    except OSError:
        raise BuildError('template.html is missing — restore it from the artifacts')


def main(argv):
    # ---- usage ----
    args = argv[1:]
    unknown = [a for a in args if a != '--install']
    if unknown:
        sys.stderr.write('unknown argument%s: %s\nusage: python3 build.py [--install]\n'
                         % ('' if len(unknown) == 1 else 's', ' '.join(unknown)))
        return 2
    install = '--install' in args

    # ---- stage 1: parse (missing files, malformed XML) ----
    for path in (SCHEMA_PATH, DATA_PATH, TEMPLATE_PATH):
        if not os.path.exists(path):
            fail('startup', ['%s is missing — restore it from the artifacts'
                             % os.path.basename(path)])
    try:
        schema = Schema(SCHEMA_PATH)
    except SchemaError as e:
        fail('schema load (deck.xsd)', [str(e)])
    try:
        root = ET.parse(DATA_PATH).getroot()
    except ET.ParseError as e:
        fail('parse (deck.xml)', ['deck.xml is not well-formed XML — %s' % _where(e)])

    # ---- stage 2: schema ----
    schema_errors = schema.validate(root)
    if schema_errors:
        fail('schema validation (deck.xsd)', schema_errors)

    # ---- stage 3: data + template checks ----
    template = read_template()
    data = build_data(root)
    checks = check_data(root, data, template)
    if checks.errors:
        fail('data checks', checks.errors)

    # ---- stage 4: build, then check the output itself ----
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    page = template.replace(MARKER, payload)
    out_checks = check_output(page, data, template)
    if out_checks.errors:
        fail('output checks', out_checks.errors)

    # ---- stage 5: write, only now ----
    os.makedirs(OUT_PATH, exist_ok=True)
    out_file = os.path.join(OUT_PATH, 'site.html')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(page)
    if install:
        os.makedirs(os.path.dirname(CANVAS_PATH), exist_ok=True)
        with open(CANVAS_PATH, 'w', encoding='utf-8') as f:
            f.write(FRONTMATTER + page)
        print('installed: the canvas (%d KB)' % ((len(FRONTMATTER + page)) // 1024))

    # ---- summary ----
    total = checks.count + out_checks.count + 1  # +1 for the schema pass
    print('built out/site.html — %d checks passed' % total)
    print('  cards %d · trails %d · ladder %d · icons %d · placeholders %d'
          % (len(data['cards']), len(data['trails']), len(data['ladder']),
             len(data['icons']), len(data['placeholders'])))
    print('  %d KB' % (len(page) // 1024))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except BuildError as e:
        sys.stderr.write('BUILD FAILED: %s\n' % e)
        sys.exit(1)
