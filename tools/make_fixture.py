#!/usr/bin/env python3
"""Create an isolated emulator-only package with explicit example data.
Never changes the production source or production application id.
"""
import argparse
from pathlib import Path
import shutil
import re

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('output', type=Path)
p.add_argument('--time', default='10:38')
p.add_argument('--battery', type=int, default=78)
p.add_argument('--scenario', choices=['rain','dry','snow','storm','missing','partial'], default='rain')
a = p.parse_args()
if a.output.resolve() == ROOT or a.output.exists():
    p.error('Choose a new empty output path outside the project.')
shutil.copytree(ROOT, a.output, ignore=shutil.ignore_patterns('build','.gradle','.git','__pycache__','output'))
p = a.output/'watchface/build.gradle.kts'
p.write_text(p.read_text().replace('applicationId = "dk.nezar.clearwatchface"','applicationId = "dk.nezar.clearwatchface.fixture"'))
p = a.output/'watchface/src/main/res/values/strings.xml'
p.write_text(p.read_text().replace('Clear Watchface','Clear · TESTDATA'))
h, m = map(int, a.time.split(':'))
values = {'HOUR_0_23_Z': f'"{h:02}"', 'MINUTE_Z': f'"{m:02}"', 'HOUR_0_23':str(h), 'MINUTE':str(m),
          'DAY_OF_WEEK_S':'"Fre"', 'DAY':'11', 'MONTH_S':'"Sep"',
          'STEP_COUNT':'6400', 'STEP_GOAL':'10000', 'STEP_PERCENT':'64', 'BATTERY_PERCENT':str(a.battery),
          'WEATHER.IS_AVAILABLE':'false' if a.scenario=='missing' else 'true', 'WEATHER.IS_ERROR':'false',
          'WEATHER.IS_DAY':'true', 'WEATHER.CONDITION':'14', 'WEATHER.TEMPERATURE':'16'}
code = {'rain':12,'dry':2,'snow':7,'storm':9,'missing':0,'partial':12}[a.scenario]
for i,temp in enumerate([16,17,15,16],1):
    values.update({f'WEATHER.HOURS.{i}.IS_AVAILABLE': 'false' if a.scenario=='missing' or (a.scenario=='partial' and i==3) else 'true',
                   f'WEATHER.HOURS.{i}.TEMPERATURE':str(temp), f'WEATHER.HOURS.{i}.CONDITION':str(code)})
p = a.output/'watchface/src/main/res/raw/watchface.xml'
s=p.read_text()
from xml.sax.saxutils import escape
s=re.sub(r'\[([^]]+)\]',lambda match:escape(values.get(match[1],match[0]), {'"':'&quot;'}),s)
p.write_text(s)
print(a.output)
