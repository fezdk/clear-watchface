#!/usr/bin/env python3
"""Render the supported WFF subset as a self-contained review page, without editing screenshots.
Typography uses the bundled font metrics. This is a layout preview, not a device brightness simulation.
"""
from pathlib import Path
import base64, html, math, re, xml.etree.ElementTree as ET
from PIL import ImageFont
from test_watchface import evaluate
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'watchface/src/main/res'
VALUES={'HOUR_0_23_Z':'10','MINUTE_Z':'38','HOUR_0_23':10,'MINUTE':38,'DAY_OF_WEEK_S':'Fre','DAY':11,'MONTH_S':'Sep','STEP_PERCENT':64,'STEP_COUNT':6400,'STEP_GOAL':10000,'BATTERY_PERCENT':78,'WEATHER.IS_AVAILABLE':True,'WEATHER.IS_ERROR':False,'WEATHER.IS_DAY':True,'WEATHER.TEMPERATURE':16,'WEATHER.CONDITION':14}
for h,t in enumerate([16,17,15,16],1):VALUES.update({f'WEATHER.HOURS.{h}.IS_AVAILABLE':True,f'WEATHER.HOURS.{h}.CONDITION':12,f'WEATHER.HOURS.{h}.TEMPERATURE':t})
def esc(v):return html.escape(str(v),quote=True)
def data(path):return base64.b64encode(path.read_bytes()).decode()
def val(s):return evaluate(s,VALUES)
def attrs(n):
 a=dict(n.attrib)
 for t in n.findall('Transform'):a[t.get('target')]=val(t.get('value'))
 return a

def formatted(f):
 t=f.find('.//Template')
 if t is None:return (f.text or '').strip()
 ps=iter([val(p.get('expression')) for p in t.findall('Parameter')])
 def repl(m):
  if m[2]=='%':return '%'
  v=next(ps)
  return (f'{int(v):,}'.replace(',','.') if m[1] else str(int(v))) if m[2]=='d' else str(v)
 return re.sub(r'%([,]?)([ds%])',repl,t.text or '')

def arcpath(cx,cy,r,start,end):
 def pt(angle):return (cx+r*math.sin(math.radians(angle)),cy-r*math.cos(math.radians(angle)))
 a,b=pt(start),pt(end)
 return f'M {a[0]:.3f} {a[1]:.3f} A {r} {r} 0 {int(end-start>180)} 1 {b[0]:.3f} {b[1]:.3f}'

def render(n,ambient=False):
 a=attrs(n); tag=n.tag
 if tag in ['Expressions','Transform','Variant','Localization']:return ''
 if tag=='Condition':
  expr={e.get('name'):e.text for e in n.findall('Expressions/Expression')}
  match=next((c for c in n.findall('Compare') if val(expr[c.get('expression')])),n.find('Default'))
  return '' if match is None else ''.join(render(c,ambient) for c in match)
 if tag=='Group':
  alpha=float(a.get('alpha',255))
  if ambient:
   for v in n.findall('Variant'):
    if v.get('mode')=='AMBIENT' and v.get('target')=='alpha':alpha=float(v.get('value'))
  if alpha==0:return ''
  return f'<g transform="translate({a.get("x",0)} {a.get("y",0)})" opacity="{alpha/255}">'+''.join(render(c,ambient) for c in n)+'</g>'
 if tag=='PartText':
  f=n.find('Text/Font'); outline=f.find('Outline'); size=float(f.get('size')); name=f.get('family')
  font=ImageFont.truetype(str(RES/'font'/f'{name}.ttf'),int(size)); asc,desc=font.getmetrics()
  y=float(a['y'])+(float(a['height'])-asc-desc)/2+asc; x=float(a['x'])+float(a['width'])/2
  style=f'font-family:{name};font-size:{size}px;fill:{f.get("color")};'
  if outline is not None:style+=f'stroke:{outline.get("color")};stroke-width:{2*float(outline.get("width"))};paint-order:stroke fill;stroke-linejoin:round;'
  dynamic=' data-battery-text="true"' if 'BATTERY_PERCENT' in ET.tostring(n,encoding='unicode') else ''
  return f'<text x="{x}" y="{y}" text-anchor="middle" style="{style}"{dynamic}>{esc(formatted(f))}</text>'
 if tag=='PartImage':
  resource=n.find('Image').get('resource'); uri='data:image/png;base64,'+data(RES/'drawable-nodpi'/f'{resource}.png')
  # Old AOD icon is white multiplied by the grayscale tint.
  opacity=int(a.get('tintColor','#FFFFFF')[1:3],16)/255
  return f'<image x="{a["x"]}" y="{a["y"]}" width="{a["width"]}" height="{a["height"]}" href="{uri}" opacity="{opacity}"/>'
 if tag=='PartDraw':
  alpha_transform=n.find("Transform[@target='alpha']")
  extra=''
  if alpha_transform is not None and 'BATTERY_PERCENT' in alpha_transform.get('value',''):
   offset=50 if n.get('name','').endswith('_green') else 0
   extra=f' data-battery-alpha-offset="{offset}"'
  return f'<g transform="translate({a.get("x",0)} {a.get("y",0)})" opacity="{float(a.get("alpha",255))/255}"{extra}>'+''.join(render(c,ambient) for c in n)+'</g>'
 if tag in ['Arc','Rectangle','RoundRectangle']:
  stroke=n.find('Stroke'); fill=n.find('Fill')
  style=f'fill:{fill.get("color") if fill is not None else "none"};'
  if stroke is not None:style+=f'stroke:{stroke.get("color")};stroke-width:{stroke.get("thickness")};stroke-linecap:{stroke.get("cap","BUTT").lower()};'
  dynamic=any('BATTERY_PERCENT' in t.get('value','') for t in n.findall('Transform'))
  if tag=='Arc':
   cx,cy=float(a['centerX']),float(a['centerY']);r=float(a['width'])/2;start,end=float(a['startAngle']),float(a['endAngle'])
   extra=f' data-battery-arc="{start}"' if dynamic else ''
   return f'<path d="{arcpath(cx,cy,r,start,end)}" style="{style}"{extra}/>'
  extra=' data-battery-fill="21"' if dynamic else ''
  return f'<rect x="{a["x"]}" y="{a["y"]}" width="{a["width"]}" height="{a["height"]}" rx="{a.get("cornerRadiusX",0)}" style="{style}"{extra}/>'
 return ''.join(render(c,ambient) for c in n)

def svg(path,ambient):
 root=ET.parse(path).getroot()
 return '<svg viewBox="0 0 450 450" role="img" aria-label="Watch face"><circle cx="225" cy="225" r="225" fill="black"/>'+render(root,ambient)+'</svg>'

old=ROOT/'design/before.xml';new=RES/'raw/watchface.xml'
fonts=''.join('@font-face{font-family:'+name+';src:url(data:font/ttf;base64,'+data(RES/'font'/f'{name}.ttf')+')} ' for name in ['clear_bold','clear_regular'])
cards=''
for mode,label in [(False,'ACTIVE'),(True,'AOD')]:
 cards+=f'<div class="mode-label">{label}</div><div class="pair">'
 for path,caption in [(old,'Before · 0.1'),(new,'Updated · 0.2')]:
  cards+='<figure>'+svg(path,mode)+f'<figcaption>{caption}</figcaption></figure>'
 cards+='</div>'
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Clear Watchface · Before and after</title><style>'''+fonts+'''
*{box-sizing:border-box}body{margin:0;background:#15181b;color:#e8ebed;font:16px system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:30px 38px}header{display:flex;justify-content:space-between;gap:24px;align-items:center;margin-bottom:20px}h1{font-size:25px;font-weight:550;margin:0 0 6px}p{color:#aeb6bd;margin:4px 0;line-height:1.5}.badge{border:1px solid #38434a;color:#8fdae1;border-radius:20px;padding:7px 13px;font-size:13px;white-space:nowrap}.pair{display:grid;grid-template-columns:1fr 1fr;gap:60px;margin-bottom:26px}figure{margin:0;text-align:center}svg{width:100%;max-width:420px;display:block;margin:auto}figcaption{font-size:16px;color:#bec7cd;margin-top:10px}.mode-label{font-size:13px;letter-spacing:.15em;color:#89979f;border-top:1px solid #30373c;padding:15px 0 12px}.controls{display:flex;align-items:center;gap:14px;margin-bottom:20px}input{accent-color:#48c6d3;width:220px}output{font-variant-numeric:tabular-nums;min-width:42px}.note{font-size:13px}.changes{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 20px}.changes span{background:#21282d;border-radius:6px;padding:6px 10px;font-size:13px;color:#c4d0d6}@media(max-width:700px){main{padding:20px 14px}.pair{gap:14px}header{display:block}.badge{display:inline-block;margin-top:10px}h1{font-size:22px}figcaption{font-size:13px}}
</style><main><header><div><h1>Clear Watchface — before and after</h1><p>The same time and example data in both versions.</p></div><div class="badge">Layout comparison</div></header><div class="changes"><span>Proportional battery fill</span><span>Empty lower arcs hidden</span><span>Larger secondary text</span><span>Brighter AOD outlines</span></div><div class="controls"><label for="battery">Battery</label><input id="battery" type="range" min="0" max="100" value="78"><output id="percent">78 %</output></div>'''+cards+'''<p class="note">Layout preview from the watch-face XML and fonts. AOD uses the design colors; the watch applies further dimming. Pixel shifting is preserved.</p></main><script>
(() => {
  const slider = document.querySelector('#battery');
  const percent = document.querySelector('#percent');
  function updateBattery() {
    const value = Math.max(0, Math.min(100, Number(slider.value)));
    percent.textContent = value + ' %';
    document.querySelectorAll('[data-battery-text]').forEach(node => {
      node.textContent = value + '%';
    });
    document.querySelectorAll('[data-battery-alpha-offset]').forEach(node => {
      const offset = Number(node.getAttribute('data-battery-alpha-offset'));
      node.setAttribute('opacity', Math.max(0, Math.min(1, (value - offset) / 50)));
    });
    document.querySelectorAll('[data-battery-fill]').forEach(node => {
      node.setAttribute('width', Number(node.getAttribute('data-battery-fill')) * value / 100);
    });
    document.querySelectorAll('[data-battery-arc]').forEach(node => {
      const start = Number(node.getAttribute('data-battery-arc'));
      const end = start + 60 * value / 100;
      const radius = 204;
      const point = angle => [225 + radius * Math.sin(angle * Math.PI / 180),
                              225 - radius * Math.cos(angle * Math.PI / 180)];
      node.setAttribute('d', `M ${point(start)} A ${radius} ${radius} 0 0 1 ${point(end)}`);
      node.style.display = value === 0 ? 'none' : '';
    });
  }
  slider.addEventListener('input', updateBattery);
  slider.addEventListener('change', updateBattery);
  updateBattery();
})();
</script></html>'''
(ROOT/'design/comparison.html').write_text(page)
(ROOT/'design/comparison-v2.html').write_text(page)
print(ROOT/'design/comparison-v2.html')
