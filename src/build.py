#!/usr/bin/env python3
"""build.py — validate, test, and build the deck page. One command,
no dependencies beyond Python 3's standard library, no Node.

Usage
-----
    python3 build.py               validate + test + build out/site.html
    python3 build.py --install    also write the canvas
    python3 build.py --data        validate + test the data, no render
    python3 build.py --part NAME   schema-validate data/NAME.xml alone
    python3 build.py --only map    build out/map.html: the map module
                                   in isolation, with its path report
    bash build.sh                  the full build, one command

The pipeline runs in stages. A failure at any stage prints EVERY
problem found at that stage, writes nothing, and exits non-zero:
nothing half-built is ever shipped or installed.

    1. parse     every data part under data/ must be well-formed
                 XML, and every file the build needs must be
                 present; --part stops after parsing and
                 schema-checking the one named part
    2. schema    the parts, each against its own declaration in
                 deck.xsd, checked by the mini-XSD interpreter
                 carried below: structure, required attributes, id
                 patterns, level pins
    3. data      cross-checks the schema cannot express: door
                 targets exist, icons are defined, rungs are known,
                 the layered descent is gradual, every row offers at
                 least two named doors, every placeholder is used,
                 every view beneath the stories is a node of exactly
                 one stratum of the model, every edge leads somewhere,
                 a landing never climbs, every door a trail opens is
                 a road the model has, each built-from edge spans one
                 storey, and every trail, hovered, lights a full
                 path down to the construction
    4. template  the template must carry a section for every view the
                 data names, the data slot, and the slots for the
                 fundamentals map module (fund.js, fund.css), which
                 the build inlines so the page stays one file
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
# Everything sits next to this script: deck.xsd, the data parts
# under data/, template.html, and the fundamentals map module
# (fund.js + fund.css). out/ holds the build results. The canvas
# is build output too, written only by --install, only after every
# check passes.
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, 'deck.xsd')
DATA_DIR = os.path.join(HERE, 'data')
TEMPLATE_PATH = os.path.join(HERE, 'template.html')
FUND_JS_PATH = os.path.join(HERE, 'fund.js')
FUND_CSS_PATH = os.path.join(HERE, 'fund.css')
OUT_PATH = os.path.join(HERE, 'out')
CANVAS_PATH = '/home/user/canvases/from-sand-to-symbols/CANVAS.md'

# The data is authored as parts, one file each under data/, named
# here in the deck's reading order. The build can validate one part
# alone (--part NAME); every full check assembles them into one
# deck, so the assembled document is never authored by hand.
PARTS = ['icons', 'primers', 'placeholders', 'cards', 'trails',
         'ladder', 'model']

# The template carries one empty slot for the data and two for the
# fundamentals map module (its script and its styles). The build
# inlines both, so the reader still receives one self-contained
# file — and the isolated map build (--only map) loads the very
# same module source into a bare harness, so the map is tested in
# isolation with exactly the code the deck ships.
MARKER = '/*__DECK_DATA__*/{}'
FUND_JS_MARKER = '/*__FUND_MODULE__*/'
FUND_CSS_MARKER = '/*__FUND_CSS__*/'
SHARED_BEGIN = '/* [shared helpers] */'
SHARED_END = '/* [/shared helpers] */'
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
#   global elements: the deck (inline anonymous type) and one per
#     data part (named type), so parts validate alone
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

    def validate(self, instance, name=None):
        """Return a list of error strings (empty when valid). The
        instance may be a whole deck or a single data part; a part
        is validated against its own global declaration, so the
        build can name the exact file that is wrong."""
        name = name if name is not None else instance.tag
        if name not in self.globals:
            return ['unknown root element <%s> — the schema declares '
                    'no part by that name' % name]
        if instance.tag != name:
            return ['root element should be <%s>, found <%s>'
                    % (name, instance.tag)]
        errors = []
        self._check_element(instance, self.globals[name],
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
    ('belongs to no stratum',
     'the model is the territory: every view beneath the stories is '
     'a node of exactly one stratum; add a <node ref="…"/> to its '
     'stratum in data/model.xml'),
    ('the model has no road',
     'a trail may only open a door the model has a road for; add '
     'the <edge from="…" to="…" kind="…"/> to data/model.xml first'),
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
    # the model: the whole system as one structure, the source of
    # truth. The strata are the layers of the territory; the edges
    # are the roads it has, each with a kind — land (a landing,
    # lit on hover, never drawn climbing), cross (a crossing, drawn
    # only when it descends exactly one storey), build (built
    # from, one storey up). The cards are not nodes: the stories
    # sit above the territory; the build enforces the rest
    model = root.find('model')
    data['map'] = [
        {'id': s.get('id'), 'label': s.get('label'), 'col': s.get('col'),
         'views': [n.get('ref') for n in s.findall('node')]}
        for s in model.findall('stratum')
    ]
    data['edges'] = [
        {'from': e.get('from'), 'to': e.get('to'), 'kind': e.get('kind')}
        for e in model.findall('edge')
    ]
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
        n = len(t['steps'])
        for i, s in enumerate(t['steps']):
            where = 'trail %s, step %d (%s)' % (tid, i + 1, s['name'])
            k.that(s['icon'] in icons, '%s: unknown icon %r' % (where, s['icon']))
            k.that(bool(s['blurb']), '%s: the blurb is empty' % where)
            floor(s['cross'], where)
            for d in s['cross']:
                door_ok(d, where, False)  # trails may reach the primers —
                # but by degrees: the first half of a trail stays
                # high, on trails and promises; the sand is walked
                # to in the second half, or landed on at the bottom
                if (i + 1) <= n / 2 and d['to'] in data['primers']:
                    k.that(False,
                           '%s: door to %r reaches the sand from the '
                           "trail's first half — a trail starts high, "
                           'on trails and promises, and descends by '
                           'degrees' % (where, d['to']))
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

    # the strata: the layers of the territory. The stories are the
    # cards above, never nodes of the model; every other view is a
    # node of exactly one stratum
    stratum_of = {}
    stratum_ids = set()
    for b in data['map']:
        k.that(bool(b['label']), 'stratum %s: a stratum must be named'
               % b['id'])
        k.that(b['id'] not in stratum_ids,
               'stratum %s: two strata share one id — each stratum '
               'is its own layer of the territory' % b['id'])
        stratum_ids.add(b['id'])
        k.that(len(b['views']) >= 1,
               'stratum %s (%s) is empty — a stratum holds at least '
               'one node' % (b['id'], b['label']))
        for ref in b['views']:
            k.that(ref in views, 'stratum %s: node %r leads nowhere'
                   % (b['id'], ref))
            k.that(ref not in data['cards'],
                   'stratum %s: %r is a story, not a node — the '
                   'stories sit above the territory' % (b['id'], ref))
            if ref in stratum_of:
                k.that(False, 'node %r sits in two strata (%s and %s)'
                       % (ref, stratum_of[ref], b['id']))
            else:
                stratum_of[ref] = b['id']
    for vid in set(data['trails']) | set(placeholders) | set(data['primers']):
        k.that(vid in stratum_of,
               'view %r belongs to no stratum — every view beneath '
               'the stories is a node of exactly one stratum' % vid)

    # the fork: beneath the subsystems the machine is drawn two
    # ways, side by side — the abstract computers on the left, the
    # machine as built on the right — and the fork runs to the
    # floor: nothing below it spans both sides again
    cols = [b.get('col') for b in data['map']]
    first = next((i for i, c in enumerate(cols) if c), None)
    k.that(first is not None,
           'the model has no fork — beneath the words and numbers '
           'the machine is drawn two ways: col="left" the abstract '
           'computers, col="right" the machine as built')
    if first is not None:
        k.that(cols[first] == 'left',
               'stratum %s opens the fork with col=%r — the fork '
               'opens with the abstract computers (col="left"), '
               'and the machine as built follows on the right'
               % (data['map'][first]['id'], cols[first]))
        k.that('right' in cols[first:],
               'the fork has no right side — the abstract computers '
               'stand alone; add the machine as built (col="right")')
        for i, c in enumerate(cols[first + 1:], first + 1):
            k.that(c is not None,
                   'stratum %s runs full width under the fork — the '
                   'fork runs to the floor; nothing below it spans '
                   'both sides' % data['map'][i]['id'])

    # the roads: every edge of the model must lead somewhere real,
    # the territory has each road once, only a trail opens a land
    # or cross road, and a landing never climbs — the strata are
    # one descent
    brow = map_rows(data)
    stratum_row = {b['id']: brow[b['id']] for b in data['map']}
    node_row = {v: stratum_row[stratum_of[v]]
                for v in stratum_of}
    node_col = {v: b.get('col') for b in data['map'] for v in b['views']}
    roads = {}
    for e in data['edges']:
        for end in ('from', 'to'):
            k.that(e[end] in views,
                   'edge %r→%r (%s): the %s end %r leads nowhere'
                   % (e['from'], e['to'], e['kind'], end, e[end]))
        k.that((e['from'], e['to']) not in roads,
               'two edges share one road %r→%r — the territory has '
               'each road once' % (e['from'], e['to']))
        roads[(e['from'], e['to'])] = e['kind']
        if e['kind'] in ('land', 'cross'):
            k.that(e['from'] in data['trails'],
                   'edge %r→%r (%s): only a trail opens a %s road — '
                   'the stories sit above the territory, and the '
                   'construction is built, not walked'
                   % (e['from'], e['to'], e['kind'], e['kind']))
        if e['kind'] == 'land' and e['from'] in node_row and e['to'] in node_row:
            k.that(node_row[e['to']] >= node_row[e['from']],
                   'edge %r→%r (land): a landing never climbs — the '
                   'strata are one descent; move the stratum or '
                   'move the landing' % (e['from'], e['to']))

    # a trail walks only the roads the territory has: every door a
    # trail opens must be a road in the model, with the kind the
    # door deserves — a land road for a bottom door, a land or
    # cross road for a step door. Roads no trail walks still
    # stand, unclaimed: the territory is richer than its walks
    for tid, t in data['trails'].items():
        for s in t['steps']:
            for d in s['cross']:
                k.that(roads.get((tid, d['to'])) in ('land', 'cross'),
                       'the model has no road %r→%r — a trail walks '
                       'only the roads the territory has; add the '
                       'edge to the model first' % (tid, d['to']))
        for d in t['deep']:
            k.that(roads.get((tid, d['to'])) == 'land',
                   'the model has no landing %r→%r — a trail bottoms '
                   'out only on a land road; the edge is missing or '
                   'carries the wrong kind' % (tid, d['to']))

    # the built-from roads: drawn upward from ingredient to built
    # thing. One spans exactly one storey upward, stays on its
    # side of the fork, and no promise is ever built from or into
    for e in data['edges']:
        if e['kind'] != 'build':
            continue
        l = e
        ra, rb = node_row.get(l['from']), node_row.get(l['to'])
        if ra is not None and rb is not None:
            k.that(ra - rb == 1,
                   'built-from edge %r→%r skips a storey — a '
                   'built-from link reaches exactly one storey up'
                   % (l['from'], l['to']))
            k.that({node_col[l['from']], node_col[l['to']]}
                   != {'left', 'right'},
                   'built-from edge %r→%r crosses the fork — the '
                   'abstract computers and the machine as built are '
                   'two ways of seeing one machine, not ingredient '
                   'and product' % (l['from'], l['to']))
        for end in ('from', 'to'):
            k.that(l[end] not in placeholders,
                   'built-from edge %r→%r: the %s end %r is a '
                   'promise, and a promise is not built yet'
                   % (l['from'], l['to'], end, l[end]))

    # the hover contract: hovering a circle on the map lights the
    # full path down — the landings and, beneath them, the
    # construction. Every trail must have one: its landing must
    # reach at least one primer, so no circle the reader hovers
    # ever fails to show the way down
    _, _, hover_paths, hover_tracks = map_paths(data)
    for tid in sorted(data['trails']):
        # a trail outside the model cannot be hovered at all: the
        # stratum check above names it, and no tracebacks
        if tid not in hover_paths:
            continue
        k.that(any(v in data['primers'] for v in hover_paths[tid]),
               'trail %s, hovered, never reaches the construction — '
               'its landing must door at least one primer, so every '
               'circle lights a full path down' % tid)

    # and the way down must show as one connected route: the drawn
    # lines between lit circles, plus the lit steps the map leaves
    # undrawn, traced live as walks. Together the two must reach
    # every lit circle from the hovered one — the contract holds
    # by construction, and this check guards it against drift. A
    # bottom rings alone: no dimming, no tracks
    for v in sorted(hover_paths):
        lit = hover_paths[v]
        lines, walks = hover_tracks[v]
        if len(lit) == 1:
            k.that(not lines and not walks,
                   'view %s, hovered, is a bottom — it rings alone, '
                   'and must not light tracks' % v)
            continue
        adj = {}
        for a, b in lines + walks:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
        seen = {v}
        stack = [v]
        while stack:
            for n in adj.get(stack.pop(), ()):
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        k.that(seen == lit,
               'view %s, hovered, lights a broken route — %s lit but '
               'never reached, the tracks must connect the whole way '
               'down' % (v, ', '.join(sorted(lit - seen))))

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
    k.that('DATA.map' in template,
           'template ignores the map bands (DATA.map)')
    k.that('DATA.edges' in template,
           'template ignores the roads of the model (DATA.edges)')
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


def read_text(path, name):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except OSError:
        raise BuildError('%s is missing — restore it from the artifacts' % name)


def load_parts(names):
    """Parse the named data parts; return {name: Element}."""
    parts = {}
    for name in names:
        path = os.path.join(DATA_DIR, name + '.xml')
        try:
            parts[name] = ET.parse(path).getroot()
        except ET.ParseError as e:
            fail('parse (data/%s.xml)' % name,
                 ['data/%s.xml is not well-formed XML — %s'
                  % (name, _where(e))])
        except OSError:
            fail('startup',
                 ['data/%s.xml is missing — restore it from the artifacts'
                  % name])
    return parts


def assemble(parts):
    """The deck is its parts, in reading order. The assembled
    document exists only in memory: the parts are the source."""
    root = ET.Element('deck')
    for name in PARTS:
        root.append(parts[name])
    return root


def map_rows(data):
    """The storeys, fork-aware: a stratum with no column runs the
    full width of the map and opens a new storey; the left stratum
    opens the fork and its own storey; a right stratum shares the
    left stratum's storey when it follows it directly, and opens
    its own below. Two strata side by side across the fork seam
    share one row: nothing lights upward across the seam, and
    nothing on the left is ever below anything on the right."""
    row = {}
    r = -1
    prev = None
    for b in data['map']:
        col = b.get('col')
        if col is None or col == 'left' or prev != 'left':
            r += 1
        row[b['id']] = r
        prev = col
    return row


def map_paths(data):
    """The hover contract, computed from the model: for every
    circle on the map, the full path down — its landings (the
    land roads of the model) and the built-from roads read
    downward, followed transitively, over views the map actually
    draws — then the construction completed: once any part of the
    built-from web is lit, the rest of it joins, provided it sits
    strictly below the hovered circle, so nothing lights upward
    and a bottom still rings alone. Returns (members,
    down-adjacency, per-view closures, per-view tracks), where the
    tracks split the lit steps into the lines the map draws (a
    road that descends exactly one storey, or a built-from link)
    and the walks it leaves undrawn — traced live on hover
    instead."""
    members = set()
    brow = map_rows(data)
    row = {}
    for b in data['map']:
        for v in b['views']:
            members.add(v)
            row[v] = brow[b['id']]
    down = {}
    for e in data['edges']:
        if e['kind'] == 'land' and e['from'] in members and e['to'] in members:
            down.setdefault(e['from'], []).append(e['to'])
    for e in data['edges']:
        if e['kind'] == 'build' and e['from'] in members:
            down.setdefault(e['to'], []).append(e['from'])
    paths = {}
    for v in sorted(members):
        seen = {v}
        stack = [v]
        grew = True
        while grew:
            while stack:
                for n in down.get(stack.pop(), ()):
                    if n not in seen:
                        seen.add(n)
                        stack.append(n)
            grew = False
            for l in data['edges']:
                if l['kind'] != 'build':
                    continue
                for end, other in ((l['to'], l['from']), (l['from'], l['to'])):
                    if (end in seen and other not in seen
                            and other in row and row[other] > row[v]):
                        seen.add(other)
                        stack.append(other)
                        grew = True
        paths[v] = seen
    # the drawn set: the roads of the model that descend exactly
    # one storey — a road that climbs, runs level, or skips storeys
    # is walked in the views, never drawn — plus the built-from
    # links, whose arrows point up while the hover walks them down
    drawn = set()
    for e in data['edges']:
        a, b = e['from'], e['to']
        if e['kind'] == 'build':
            drawn.add((a, b))
            continue
        if a in row and b in row and row[b] - row[a] == 1:
            drawn.add((a, b))
    tracks = {}
    for v in sorted(members):
        lit = paths[v]
        lines, walks = [], []
        seen_pairs = set()
        for a, targets in down.items():
            for b in targets:
                if a in lit and b in lit and (a, b) not in seen_pairs:
                    seen_pairs.add((a, b))
                    if (a, b) in drawn or (b, a) in drawn:
                        lines.append((a, b))
                    else:
                        walks.append((a, b))
        tracks[v] = (lines, walks)
    return members, down, paths, tracks


def build_map_page(data, fund_css, fund_js, raw_template):
    """The fundamentals map in isolation: same data, same module
    source, none of the deck around it — the harness that makes
    the map and its hover testable on their own."""
    i = raw_template.index(SHARED_BEGIN)
    j = raw_template.index(SHARED_END) + len(SHARED_END)
    shared = raw_template[i:j]
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>the map, in isolation — Everything to bits</title>\n'
        '<style>\n'
        '/* the harness: the map module and nothing else. The module\n'
        '   carries its own styles and root variables; the rules here\n'
        '   are only the page around it */\n'
        'body{margin:0 auto;max-width:1150px;padding:2.5em 2em 4em;'
        'font:16px/1.6 Georgia,serif;color:var(--ink);background:var(--paper)}\n'
        'h1{font-size:1.25rem;font-weight:600;margin:0 0 .2em}\n'
        'h2{font-size:1rem;font-weight:600;margin:2.5em 0 .8em}\n'
        '.note{font-size:.85rem;color:var(--faint);max-width:46em;'
        'margin:0 0 1.5em}\n'
        '.rep{font:12.5px/1.7 var(--sans)}\n'
        '.rep .row{display:flex;gap:1.2em;border-bottom:1px solid var(--hair);'
        'padding:3px 0}\n'
        '.rep .row span:first-child{width:200px}\n'
        '.rep em{color:var(--faint);font-style:normal}\n'
        '.rep .bottom{color:var(--faint)}\n'
        + fund_css +
        '\n</style>\n</head>\n<body>\n'
        '<h1>the map, in isolation</h1>\n'
        '<p class="note">The fundamentals map and its hover, built with '
        '<code>build.py --only map</code>: the same module source the deck '
        'inlines, the same data, none of the deck around it. The strata '
        'run top to bottom, one zoom deeper each storey — what a person '
        'sees; the boundary where the world crosses into data and data '
        'crosses back; machines together; one machine, at work; the words '
        'and numbers inside — then the fork: the abstract computers on '
        'the left, and on the right the machine as built, opening into '
        'its components and ending in the bedrock; the left side bottoms '
        'in mathematics itself, nothing drawn beneath it. One line per '
        'road that descends exactly one storey; a road that climbs, runs '
        'level, or skips storeys is walked in the views, never drawn. '
        'Hovering a circle lights the full path down from it — its '
        'landings, and the construction they stand on, completed as one '
        'web of tracks: the drawn lines light, and every lit step the '
        'map leaves undrawn, a long walk, is traced live, dashed, only '
        'while hovered. A circle with nothing beneath it, a promise or '
        'the bedrock, rings alone.</p>\n'
        '<div class="dag" id="fund-dag"></div>\n'
        '<h2>the report</h2>\n'
        '<div class="rep" id="fund-report"></div>\n'
        "<script>\n'use strict';\n"
        'const DATA = ' + payload + ';\n'
        'const SYSTEMS = DATA.cards;\n'
        'const EXPLAINERS = DATA.trails;\n'
        'const ICONS = DATA.icons;\n'
        'const PRIMER_META = DATA.primers;\n'
        'const PLACEHOLDERS = DATA.placeholders;\n'
        'const MAP = DATA.map;\n'
        'const EDGES = DATA.edges || [];\n'
        'const CHAIN = EDGES.filter((e) => e.kind === "build");\n'
        + shared + '\n'
        + fund_js + '\n'
        'renderFundDAG();\n'
        "fundReport(document.querySelector('#fund-report'));\n"
        '</script>\n</body>\n</html>\n')


def print_census(data, members, paths):
    """The map census, read off the model: the lines the map draws
    (roads that descend exactly one storey), the walks inside a
    layer, the long walks left to the views — including every
    upward road, which the map never draws — and the built-from
    links."""
    brow = map_rows(data)
    band_of = {v: b['id'] for b in data['map'] for v in b['views']}
    band_row = {v: brow[band_of[v]] for v in band_of}
    lines = walked = skipped = 0
    build = 0
    for e in data['edges']:
        if e['kind'] == 'build':
            build += 1
            continue
        a, b = e['from'], e['to']
        ra, rb = band_row.get(a), band_row.get(b)
        if ra is None or rb is None:
            continue
        d = rb - ra
        if d == 1:
            lines += 1
        elif d == 0:
            walked += 1
        else:
            skipped += 1
    print('  map: %d lines · %d walked inside a layer · %d long walks not drawn · %d built-from links'
          % (lines, walked, skipped, build))
    full = sum(1 for v in members if len(paths[v]) > 1)
    print('  hover: %d full paths down · %d bottoms ring alone'
          % (full, len(members) - full))


def main(argv):
    # ---- usage ----
    usage = ('usage: python3 build.py [--install] [--data] '
             '[--part NAME] [--only map]\n'
             '  (no options)   validate + test + build out/site.html\n'
             '  --data          validate + test the data, no render\n'
             '  --part NAME     schema-validate data/NAME.xml alone\n'
             '  --only map      build out/map.html, the map module in isolation\n'
             '  --install       with the full build, also write the canvas\n')
    args = argv[1:]
    flags = {'--install': False, '--data': False}
    part = only = None
    i = 0
    while i < len(args):
        a = args[i]
        if a in flags:
            flags[a] = True
        elif a == '--part':
            i += 1
            part = args[i] if i < len(args) else ''
        elif a == '--only':
            i += 1
            only = args[i] if i < len(args) else ''
        else:
            sys.stderr.write('unknown argument: %s\n%s' % (a, usage))
            return 2
        i += 1
    if part is not None:
        if part not in PARTS:
            sys.stderr.write('unknown part: %r — choose one of %s\n%s'
                             % (part, ', '.join(PARTS), usage))
            return 2
    if only is not None and only != 'map':
        sys.stderr.write('unknown isolation target: %r — only the map '
                         'is built in isolation\n%s' % (only, usage))
        return 2
    install, data_only = flags['--install'], flags['--data']

    # ---- stage 1: parse (missing files, malformed XML) ----
    for path in (SCHEMA_PATH, TEMPLATE_PATH, FUND_JS_PATH, FUND_CSS_PATH):
        if not os.path.exists(path):
            fail('startup', ['%s is missing — restore it from the artifacts'
                             % os.path.basename(path)])
    try:
        schema = Schema(SCHEMA_PATH)
    except SchemaError as e:
        fail('schema load (deck.xsd)', [str(e)])

    if part is not None:
        # one part, in isolation: schema-check it and stop
        lone = load_parts([part])
        errors = schema.validate(lone[part], part)
        if errors:
            fail('schema validation (data/%s.xml)' % part, errors)
        print('data/%s.xml — schema clean (%d child element%s)'
              % (part, len(lone[part]), '' if len(lone[part]) == 1 else 's'))
        return 0

    parts = load_parts(PARTS)
    root = assemble(parts)

    # ---- stage 2: schema, part by part. The assembly's order is
    # the build's own (PARTS above), so the assembled deck needs
    # no separate pass ----
    for name in PARTS:
        errors = schema.validate(parts[name], name)
        if errors:
            fail('schema validation (data/%s.xml)' % name, errors)

    # ---- stage 3: data + template checks ----
    raw_template = read_template()
    fund_js = read_text(FUND_JS_PATH, 'fund.js')
    fund_css = read_text(FUND_CSS_PATH, 'fund.css')
    for marker, what in ((FUND_JS_MARKER, 'the map module slot'),
                         (FUND_CSS_MARKER, 'the map style slot')):
        if marker not in raw_template:
            fail('startup',
                 ['template.html has no %s (%s) — the fundamentals '
                  'map cannot be inlined' % (what, marker)])
    if SHARED_BEGIN not in raw_template or SHARED_END not in raw_template:
        fail('startup',
             ['template.html has no shared helper block (%s … %s) — '
              'the isolated map build cannot extract it'
              % (SHARED_BEGIN, SHARED_END)])
    template = (raw_template
                .replace(FUND_CSS_MARKER, fund_css)
                .replace(FUND_JS_MARKER, fund_js))
    data = build_data(root)
    checks = check_data(root, data, template)
    if checks.errors:
        fail('data checks', checks.errors)
    members, down, paths, tracks = map_paths(data)

    if data_only:
        total = checks.count + len(PARTS)  # one schema pass per part
        print('data checks passed — %d checks' % total)
        print('  cards %d · trails %d · ladder %d · icons %d · placeholders %d'
              % (len(data['cards']), len(data['trails']), len(data['ladder']),
                 len(data['icons']), len(data['placeholders'])))
        print_census(data, members, paths)
        return 0

    if only == 'map':
        page = build_map_page(data, fund_css, fund_js, raw_template)
        k = Checks()
        k.that('id="fund-dag"' in page,
               'the isolated page has no map holder')
        k.that('const DATA = {' in page,
               'the isolated page has no data payload')
        k.that('function renderFundDAG' in page,
               'the isolated page has no map module')
        k.that('function fundReport' in page,
               'the isolated page has no report')
        k.that('/*__' not in page and '__DECK_DATA__' not in page,
               'the isolated page still carries an unfilled slot')
        if k.errors:
            fail('output checks (out/map.html)', k.errors)
        os.makedirs(OUT_PATH, exist_ok=True)
        with open(os.path.join(OUT_PATH, 'map.html'), 'w',
                  encoding='utf-8') as f:
            f.write(page)
        print('built out/map.html — the map module in isolation '
              '(%d checks passed)' % (checks.count + k.count + len(PARTS)))
        pos = {}
        for i, b in enumerate(data['map']):
            for j, v in enumerate(b['views']):
                pos[v] = (i, j)
        for b in data['map']:
            for v in b['views']:
                lands = sorted((x for x in paths[v] if x != v),
                               key=lambda x: pos[x])
                lines, walks = tracks[v]
                kind = ('lands on ' + ', '.join(lands)) if lands \
                    else 'bottom — rings alone'
                print('  %-13s %-3d %2dt %s'
                      % (v, len(paths[v]), len(lines) + len(walks), kind))
        return 0

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
    total = checks.count + out_checks.count + len(PARTS)  # + a schema pass per part
    print('built out/site.html — %d checks passed' % total)
    print('  cards %d · trails %d · ladder %d · icons %d · placeholders %d'
          % (len(data['cards']), len(data['trails']), len(data['ladder']),
             len(data['icons']), len(data['placeholders'])))
    print_census(data, members, paths)
    print('  %d KB' % (len(page) // 1024))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except BuildError as e:
        sys.stderr.write('BUILD FAILED: %s\n' % e)
        sys.exit(1)
