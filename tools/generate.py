#!/usr/bin/env python3
"""Generate the resource-only WFF document and original, code-drawn icons.

Run with Python 3 + Pillow. The generated XML/assets are checked in, so Gradle
builds need only Java/Android SDK. No image-generation service is used here.
"""
from pathlib import Path
import math
import xml.etree.ElementTree as E
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'watchface/src/main/res'
WHITE, MUTED, CYAN, TRACK, DIM = '#F2F3F4', '#CBD0D5', '#48C6D3', '#303439', '#E0E0E0'
AOD_BATTERY = '#A0A0A0'
PROGRESS_RED, PROGRESS_YELLOW, PROGRESS_GREEN = '#E85D5D', '#EACB55', '#60C878'
SIZE = 450
HOURS = range(1, 5)

def node(parent, tag, **attrs):
    return E.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})

def template(parent, fmt, *params):
    t = node(parent, 'Template')
    t.text = fmt
    for p in params:
        node(t, 'Parameter', expression=p)

def text(parent, name, x, y, w, h, size, fmt, *params, color=WHITE, bold=False, outline=False):
    p = node(parent, 'PartText', name=name, x=x, y=y, width=w, height=h)
    t = node(p, 'Text', align='CENTER', maxLines=1)
    f = node(t, 'Font', family='clear_bold' if bold else 'clear_regular', size=size, color=color)
    if outline:
        f = node(f, 'Outline', width=2.2, color=DIM)
    if params:
        template(f, fmt, *params)
    else:
        f.text = fmt
    return p

def image(parent, name, x, y, w, h, tint=None):
    p = node(parent, 'PartImage', x=x, y=y, width=w, height=h)
    if tint:
        p.set('tintColor', tint)
    node(p, 'Image', resource=name)
    return p

def condition(parent, name, expr):
    c = node(parent, 'Condition')
    es = node(c, 'Expressions')
    node(es, 'Expression', name=name).text = expr
    return c, node(c, 'Compare', expression=name)

def arc(parent, name, start, end, progress=None):
    p = node(parent, 'PartDraw', name=name, x=0, y=0, width=450, height=450)
    a = node(p, 'Arc', centerX=225, centerY=225, width=408, height=408, startAngle=start, endAngle=end)
    node(a, 'Stroke', color=TRACK, thickness=7, cap='ROUND')
    if progress:
        _, show = condition(parent, name+'_nonzero', f'{progress} > 0')
        # WFF 2 cannot transform Stroke.color. Crossfade identical arcs instead:
        # red -> yellow over 0..50%, then opaque yellow -> green over 50..100%.
        for suffix, color, offset in [('', PROGRESS_RED, None),
                                      ('_yellow', PROGRESS_YELLOW, 0),
                                      ('_green', PROGRESS_GREEN, 50)]:
            q = node(show, 'PartDraw', name=name+'_fill'+suffix, x=0, y=0, width=450, height=450)
            if offset is not None:
                node(q, 'Transform', target='alpha',
                     value=f'255 * clamp(({progress} - {offset}) / 50, 0, 1)')
            a = node(q, 'Arc', centerX=225, centerY=225, width=408, height=408, startAngle=start, endAngle=end)
            node(a, 'Transform', target='endAngle', value=f'{start} + {end-start} * clamp({progress}, 0, 100) / 100')
            node(a, 'Stroke', color=color, thickness=7, cap='ROUND')

def battery_icon(parent, name, x, y, color=WHITE):
    """Small outlined shell with a clamped, proportional fill in both modes."""
    group = node(parent, 'Group', name=name, x=x, y=y, width=32, height=20)
    p = node(group, 'PartDraw', x=0, y=0, width=32, height=20)
    shell = node(p, 'RoundRectangle', x=1, y=1, width=27, height=18,
                 cornerRadiusX=2, cornerRadiusY=2)
    node(shell, 'Stroke', color=color, thickness=1.4)
    terminal = node(p, 'Rectangle', x=29, y=7, width=2, height=6)
    node(terminal, 'Fill', color=color)
    _, filled = condition(group, name+'_nonzero', '[BATTERY_PERCENT] > 0')
    p = node(filled, 'PartDraw', name=name+'_fill', x=0, y=0, width=32, height=20)
    rect = node(p, 'Rectangle', x=4, y=4, width=21, height=12)
    node(rect, 'Transform', target='width', value='21 * clamp([BATTERY_PERCENT], 0, 100) / 100')
    node(rect, 'Fill', color=color)

def weather_icon(parent, source, x, y, size):
    c = node(parent, 'Condition')
    es = node(c, 'Expressions')
    mapping = {'clear': [1, 8], 'cloud': [2], 'fog': [3, 13], 'rain': [4, 6, 12],
               'snow': [5, 7, 11], 'storm': [9], 'sleet': [10], 'partly': [14], 'wind': [15]}
    for name, values in mapping.items():
        node(es, 'Expression', name=name).text = ' || '.join(f'{source} == {v}' for v in values)
        match = node(c, 'Compare', expression=name)
        if name == 'clear':
            day, sun = condition(match, 'day', '[WEATHER.IS_DAY]')
            image(sun, 'weather_clear', x, y, size, size)
            image(node(day, 'Default'), 'weather_moon', x, y, size, size)
        else:
            image(match, 'weather_'+name, x, y, size, size)
    image(node(c, 'Default'), 'weather_unknown', x, y, size, size)

def generate_xml():
    root = E.Element('WatchFace', width='450', height='450')
    scene = node(root, 'Scene', backgroundColor='#000000')
    active = node(scene, 'Group', name='interactive', x=0, y=0, width=450, height=450)
    node(active, 'Variant', mode='AMBIENT', target='alpha', value=0)
    node(active, 'Localization', locales='da_DK')
    arc(active, 'steps', 285, 345, '[STEP_PERCENT]')
    arc(active, 'battery', 15, 75, '[BATTERY_PERCENT]')
    # Lower slots have no assigned data yet: render no placeholder arcs.
    image(active, 'steps', 90, 94, 30, 30)
    goal, goal_known = condition(active, 'goal_known', '[STEP_GOAL] > 0')
    text(node(goal, 'Default'), 'step_count_without_goal', 26, 124, 172, 27, 17, '%,d skridt', '[STEP_COUNT]')
    text(goal_known, 'step_count_and_goal', 26, 124, 172, 27, 17, '%,d / %,d', '[STEP_COUNT]', '[STEP_GOAL]')
    battery_icon(active, 'active_battery_icon', 320, 100)
    text(active, 'battery_percent', 301, 124, 74, 28, 20, '%d%%', '[BATTERY_PERCENT]')
    text(active, 'date', 90, 145, 270, 31, 23, '%s %d. %s', '[DAY_OF_WEEK_S]', '[DAY]', '[MONTH_S]', color=MUTED)
    text(active, 'time', 35, 174, 380, 108, 100, '%s:%s', '[HOUR_0_23_Z]', '[MINUTE_Z]', bold=True)

    # Keep old weather visible with an explicit stale-data mark when the provider reports an error.
    current, valid = condition(active, 'current_available', '[WEATHER.IS_AVAILABLE]')
    weather_icon(valid, '[WEATHER.CONDITION]', 179, 63, 40)
    text(valid, 'temperature', 218, 66, 65, 38, 28, '%d°', '[WEATHER.TEMPERATURE]')
    _, stale = condition(valid, 'stale', '[WEATHER.IS_ERROR]')
    text(stale, 'weather_stale', 166, 106, 130, 21, 12, 'Sidst kendte vejr', color=MUTED)
    fallback = node(current, 'Default')
    text(fallback, 'weather_missing', 151, 76, 148, 28, 19, 'Vejr —', color=MUTED)

    # Only summarize a complete, known four-hour forecast. No invented placeholder data.
    available = ' && '.join(f'[WEATHER.HOURS.{h}.IS_AVAILABLE] && [WEATHER.HOURS.{h}.CONDITION] > 0' for h in HOURS)
    forecast, valid = condition(active, 'forecast_available', available)
    text(valid, 'forecast_heading', 95, 331, 260, 28, 18, 'NÆSTE 4 TIMER', color=MUTED)
    temps = [f'[WEATHER.HOURS.{h}.TEMPERATURE]' for h in HOURS]
    # WFF 2 has abs()/round(), but no min()/max().
    def extremum(a, b, sign):
        return f'(({a}) + ({b}) {sign} abs(({a}) - ({b}))) / 2'
    lo = 'round(' + extremum(extremum(temps[0], temps[1], '-'), extremum(temps[2], temps[3], '-'), '-') + ')'
    hi = 'round(' + extremum(extremum(temps[0], temps[1], '+'), extremum(temps[2], temps[3], '+'), '+') + ')'
    text(valid, 'forecast_range', 125, 359, 200, 34, 26, '%d–%d°', lo, hi)
    c = node(valid, 'Condition')
    es = node(c, 'Expressions')
    for name, codes, label in [('storm', [9], 'Torden i perioden'), ('sleet', [10], 'Slud i perioden'), ('snow', [5,7,11], 'Sne i perioden'), ('rain', [4,6,12], 'Regn i perioden')]:
        node(es, 'Expression', name=name).text = ' || '.join(f'[WEATHER.HOURS.{h}.CONDITION] == {code}' for h in HOURS for code in codes)
        match = node(c, 'Compare', expression=name)
        image(match, 'weather_'+name, 205, 286, 40, 40)
        text(match, 'forecast_'+name, 95, 392, 260, 27, 18, label, color=MUTED)
    dry = node(c, 'Default')
    image(dry, 'weather_partly', 205, 286, 40, 40)
    text(dry, 'forecast_dry', 95, 392, 260, 27, 18, 'Ingen nedbør meldt', color=MUTED)
    fallback = node(forecast, 'Default')
    text(fallback, 'forecast_missing', 75, 334, 300, 30, 20, 'Prognose ikke tilgængelig', color=MUTED)

    ambient = node(scene, 'Group', name='ambient_shift', x=0, y=0, width=450, height=450, alpha=0)
    node(ambient, 'Variant', mode='AMBIENT', target='alpha', value=255)
    # 25 distinct offsets, 1 logical pixel apart, sampled only from minute/hour data.
    # This supplements any device-level shift. The entire AOD, including colon/battery, moves.
    minute = '([HOUR_0_23] * 60 + [MINUTE])'
    node(ambient, 'Transform', target='x', value=f'({minute} % 5) - 2')
    node(ambient, 'Transform', target='y', value=f'(floor({minute} / 5) % 5) - 2')
    text(ambient, 'ambient_time', 35, 174, 380, 108, 100, '%s:%s', '[HOUR_0_23_Z]', '[MINUTE_Z]', color='#000000', bold=True, outline=True)
    battery_icon(ambient, 'ambient_battery_icon', 301, 104, color=AOD_BATTERY)
    text(ambient, 'ambient_battery', 337, 100, 65, 29, 20, '%d%%', '[BATTERY_PERCENT]', color=AOD_BATTERY)
    E.indent(root, space='  ')
    (RES/'raw').mkdir(parents=True, exist_ok=True)
    E.ElementTree(root).write(RES/'raw/watchface.xml', encoding='utf-8', xml_declaration=True)

def generate_icons():
    out = RES/'drawable-nodpi'
    out.mkdir(parents=True, exist_ok=True)
    s = 4
    def canvas():
        im = Image.new('RGBA', (64*s,64*s))
        return im, ImageDraw.Draw(im)
    def box(b): return tuple(int(x*s) for x in b)
    def cloud(d):
        for b in [(10,27,36,51),(23,18,50,51),(37,31,59,51)]: d.ellipse(box(b), fill=WHITE)
        d.rectangle(box((22,36,48,51)), fill=WHITE)
    def sun(d):
        d.ellipse(box((19,19,45,45)), fill='#E8CD68')
        for a in range(0,360,45):
            r=math.radians(a)
            d.line(tuple((int((32+rr*math.cos(r))*s),int((32+rr*math.sin(r))*s)) for rr in (19,25)), fill='#E8CD68',width=3*s)
    for kind in ['clear','moon','cloud','partly','fog','rain','snow','sleet','storm','wind','unknown']:
        im,d=canvas()
        if kind=='clear': sun(d)
        elif kind=='moon':
            d.ellipse(box((12,10,52,52)), fill=WHITE)
            d.ellipse(box((26,3,61,39)), fill=(0,0,0,0))
        elif kind=='unknown':
            d.ellipse(box((15,15,49,49)), outline=MUTED,width=3*s)
            d.line((box((26,32)),box((38,32))), fill=MUTED,width=3*s)
        elif kind=='wind':
            for y,x in [(22,50),(32,57),(42,44)]: d.line((box((10,y)),box((x,y))), fill=WHITE,width=3*s)
        else:
            if kind=='partly':
                d.ellipse(box((29,7,51,29)),fill='#E8CD68')
                for a in (220,270,320,0):
                    r=math.radians(a)
                    d.line(tuple((int((40+rr*math.cos(r))*s),int((18+rr*math.sin(r))*s)) for rr in (15,20)),fill='#E8CD68',width=2*s)
            cloud(d)
            if kind in ('rain','sleet'):
                for x in (21,34,47): d.line((box((x,54)),box((x-3,61))),fill=CYAN,width=3*s)
            if kind in ('snow','sleet'):
                for x in (24,44): d.ellipse(box((x-2,55,x+2,59)),fill=WHITE)
            if kind=='storm': d.polygon([box(p) for p in [(32,42),(23,55),(32,55),(28,64),(43,48),(34,48)]],fill='#E8CD68')
            if kind=='fog':
                for y in (54,60): d.line((box((10,y)),box((57,y))),fill=MUTED,width=2*s)
        im.resize((64,64),Image.Resampling.LANCZOS).save(out/f'weather_{kind}.png')
    im=Image.new('RGBA',(112,72)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((4,5,95,66),radius=6,outline=WHITE,width=6)
    d.line((102,26,102,45),fill=WHITE,width=6)
    im.resize((56,36),Image.Resampling.LANCZOS).save(out/'battery.png')
    im,d=canvas()
    for b in [(11,23,28,45),(17,46,27,57),(35,6,52,28),(36,30,46,41)]:
        d.ellipse(box(b),fill=WHITE)
    im.resize((52,52),Image.Resampling.LANCZOS).save(out/'steps.png')
    im = Image.new('RGBA', (192,192))
    d = ImageDraw.Draw(im)
    d.ellipse((8,8,184,184),fill='#000000')
    d.arc((17,17,175,175),205,255,fill=CYAN,width=4)
    d.arc((17,17,175,175),285,335,fill=CYAN,width=4)
    font = ImageFont.truetype(str(RES/'font/clear_bold.ttf'),44)
    d.text((96,96),'10:38',font=font,anchor='mm',fill=WHITE)
    im.save(out/'app_icon.png')

if __name__ == '__main__':
    generate_icons()
    generate_xml()
    print('Generated WFF XML and icons.')
