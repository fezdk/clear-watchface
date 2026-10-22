#!/usr/bin/env python3
"""Behavioral checks of expressions and resource references from the actual WFF XML."""
import math
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT/'watchface/src/main/res'
DOC = ET.parse(RES/'raw/watchface.xml').getroot()

def evaluate(expression, values):
    # Only trusted project expressions, with no Python builtins available.
    expression = re.sub(r'\[([^]]+)\]', lambda m: f'values[{m[1]!r}]', expression)
    expression = expression.replace('&&',' and ').replace('||',' or ')
    return eval(expression, {'__builtins__':{}}, {'values':values, 'min':min, 'max':max,
                 'abs':abs, 'round':round, 'floor':math.floor, 'clamp':lambda v,lo,hi:max(lo,min(hi,v))})

def expression(name):
    return DOC.find(f".//Expression[@name='{name}']").text

class WatchfaceTests(unittest.TestCase):
    def test_arc_empty_full_and_clamped(self):
        for source,name,start,end in [('STEP_PERCENT','steps',285,345),('BATTERY_PERCENT','battery',15,75)]:
            fill = DOC.find(f".//PartDraw[@name='{name}_fill']/Arc/Transform").get('value')
            for value,expected in [(0,start),(50,(start+end)/2),(100,end),(150,end),(-1,start)]:
                self.assertAlmostEqual(evaluate(fill,{source:value}),expected)
            self.assertFalse(evaluate(expression(name+'_nonzero'),{source:0}))
            self.assertTrue(evaluate(expression(name+'_nonzero'),{source:1}))

    def test_progress_colors_crossfade_and_clamp(self):
        # Composite the actual WFF layers to check endpoints, midpoint, smoothness,
        # ordering, and out-of-range input without relying on generator constants.
        for name, source in [('steps', 'STEP_PERCENT'), ('battery', 'BATTERY_PERCENT')]:
            layers = [DOC.find(f".//PartDraw[@name='{name}_fill{suffix}']")
                      for suffix in ['', '_yellow', '_green']]
            previous = None
            for percent in range(-1, 152):
                rgb = [0., 0., 0.]
                for layer in layers:
                    transform = layer.find("Transform[@target='alpha']")
                    alpha = 1 if transform is None else evaluate(transform.get('value'), {source: percent}) / 255
                    self.assertTrue(0 <= alpha <= 1)
                    arc = layer.find('Arc')
                    reference = layers[0].find("Arc/Transform[@target='endAngle']").get('value')
                    self.assertEqual(arc.find("Transform[@target='endAngle']").get('value'), reference)
                    color = arc.find('Stroke').get('color').lstrip('#')
                    channels = [int(color[i:i+2], 16) for i in (0, 2, 4)]
                    rgb = [a * alpha + b * (1-alpha) for a, b in zip(channels, rgb)]
                if percent in (-1, 0, 50, 100, 151):
                    expected = (232, 93, 93) if percent <= 0 else ((234, 203, 85) if percent == 50 else (96, 200, 120))
                    self.assertEqual(tuple(round(c) for c in rgb), expected)
                if previous is not None:
                    self.assertLessEqual(max(abs(a-b) for a,b in zip(rgb, previous)), 3)
                previous = rgb

    def test_no_zero_goal_fraction(self):
        self.assertFalse(evaluate(expression('goal_known'),{'STEP_GOAL':0}))
        self.assertTrue(evaluate(expression('goal_known'),{'STEP_GOAL':10000}))
        self.assertIsNotNone(DOC.find(".//PartText[@name='step_count_without_goal']"))

    def test_forecast_requires_every_hour(self):
        values={}
        for h in range(1,5):
            values.update({f'WEATHER.HOURS.{h}.IS_AVAILABLE':True, f'WEATHER.HOURS.{h}.CONDITION':2})
        self.assertTrue(evaluate(expression('forecast_available'),values))
        for h in range(1,5):
            missing=dict(values)
            missing[f'WEATHER.HOURS.{h}.IS_AVAILABLE']=False
            del missing[f'WEATHER.HOURS.{h}.CONDITION']
            self.assertFalse(evaluate(expression('forecast_available'),missing))
            unknown=dict(values); unknown[f'WEATHER.HOURS.{h}.CONDITION']=0
            self.assertFalse(evaluate(expression('forecast_available'),unknown))

    def test_forecast_range_includes_middle_hours_and_negative_temperatures(self):
        params=DOC.findall(".//PartText[@name='forecast_range']//Parameter")
        for temps,expected in [([16,17,15,16],(15,17)),([-2,-8,3,-1],(-8,3)),([4,4,4,4],(4,4))]:
            values={f'WEATHER.HOURS.{h}.TEMPERATURE':t for h,t in enumerate(temps,1)}
            self.assertEqual(tuple(evaluate(p.get('expression'),values) for p in params),expected)

    def test_precipitation_in_any_hour_is_not_missed(self):
        # Inspect the forecast condition, which has a storm expression distinct from the current icon mapping.
        condition=next(c for c in DOC.findall('.//Condition') if c.find("Compare/PartText[@name='forecast_storm']") is not None)
        expressions={x.get('name'):x.text for x in condition.findall('Expressions/Expression')}
        for category,codes in {'storm':[9],'sleet':[10],'snow':[5,7,11],'rain':[4,6,12]}.items():
            for hour in range(1,5):
                for code in codes:
                    values={f'WEATHER.HOURS.{h}.CONDITION':2 for h in range(1,5)}
                    values[f'WEATHER.HOURS.{hour}.CONDITION']=code
                    self.assertTrue(evaluate(expressions[category],values))

    def test_aod_is_minute_driven_and_whole_group_shifts(self):
        aod=DOC.find(".//Group[@name='ambient_shift']")
        self.assertEqual({x.get('name') for x in aod.findall('PartText')},{'ambient_time','ambient_battery'})
        self.assertIsNotNone(aod.find("PartText[@name='ambient_time']//Outline/Template"))
        self.assertNotRegex(ET.tostring(aod,encoding='unicode'),r'\[(SECOND|MILLISECOND|WEATHER|STEP)')
        transforms={t.get('target'):t.get('value') for t in aod.findall('Transform')}
        positions=[]
        for minute in range(1440):
            values={'HOUR_0_23':minute//60,'MINUTE':minute%60}
            xy=tuple(evaluate(transforms[a],values) for a in ['x','y'])
            self.assertTrue(all(-2<=v<=2 for v in xy))
            positions.append(xy)
        self.assertEqual(len(set(positions[:25])),25)
        self.assertTrue(all(a!=b for a,b in zip(positions,positions[1:])))
        self.assertNotEqual(positions[-1],positions[0])
        for text in aod.findall('PartText'):
            self.assertGreaterEqual(float(text.get('x'))-2,20)
            self.assertLessEqual(float(text.get('x'))+float(text.get('width'))+2,430)

    def test_only_supported_wff_functions(self):
        allowed = {'abs','round','clamp','floor'}
        for element in DOC.iter():
            values = [element.get('expression',''), element.get('value','')]
            if element.tag == 'Expression': values.append(element.text or '')
            for value in values:
                self.assertTrue(set(re.findall(r'([a-zA-Z]+)\s*\(',value)) <= allowed, value)

    def test_battery_icon_fill_and_hidden_lower_slots(self):
        self.assertIsNone(DOC.find(".//PartDraw[@name='reserved_lower_right']"))
        self.assertIsNone(DOC.find(".//PartDraw[@name='reserved_lower_left']"))
        for name in ['active_battery_icon','ambient_battery_icon']:
            value=DOC.find(f".//PartDraw[@name='{name}_fill']/Rectangle/Transform").get('value')
            for percent,width in [(0,0),(25,5.25),(50,10.5),(78,16.38),(100,21),(120,21)]:
                self.assertAlmostEqual(evaluate(value,{'BATTERY_PERCENT':percent}),width)
            self.assertFalse(evaluate(expression(name+'_nonzero'),{'BATTERY_PERCENT':0}))

    def test_all_font_and_image_resources_exist(self):
        for img in DOC.findall('.//Image'):
            self.assertTrue((RES/'drawable-nodpi'/f"{img.get('resource')}.png").exists())
        for font in DOC.findall('.//Font'):
            self.assertTrue((RES/'font'/f"{font.get('family')}.ttf").exists())

    def test_apk_contains_no_runtime_code(self):
        apk=ROOT/'watchface/build/outputs/apk/debug/watchface-debug.apk'
        if not apk.exists(): self.skipTest('Build assembleDebug first for APK inspection')
        with zipfile.ZipFile(apk) as z:
            self.assertFalse(any(n.endswith('.dex') or n.endswith('.so') for n in z.namelist()))
            self.assertIn('res/raw/watchface.xml',z.namelist())

if __name__=='__main__': unittest.main(verbosity=2)
