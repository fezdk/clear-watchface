#!/usr/bin/env python3
"""Conservative source-font coverage estimate, not a hardware burn-in guarantee.
Uses a 3 px outline (WFF uses 2.2), full-white coverage independent of dimming,
all 1,440 times, all 101 battery values, and the circular 450-unit screen area.
"""
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw, ImageFont, ImageChops
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'watchface/src/main/res'
bold=ImageFont.truetype(str(RES/'font/clear_bold.ttf'),100)
regular=ImageFont.truetype(str(RES/'font/clear_regular.ttf'),17)
def lit(im): return im.width*im.height-im.histogram()[0]
maximum=(0,'')
for minute in range(1440):
    label=f'{minute//60:02}:{minute%60:02}'
    im=Image.new('L',(450,450));d=ImageDraw.Draw(im)
    d.text((225,228),label,font=bold,anchor='mm',fill=0,stroke_width=3,stroke_fill=255)
    count=lit(im)
    if count>maximum[0]:maximum=(count,label)
battery=0
for value in range(101):
    im=Image.new('L',(450,450));d=ImageDraw.Draw(im)
    d.text((365,114),f'{value}%',font=regular,anchor='mm',fill=255)
    battery=max(battery,lit(im))
# Count the entire 32x20 battery box as lit: conservative even at full charge.
ratio=100*(maximum[0]+battery+32*20)/(math.pi*225**2)
report={'method':'conservative source-font estimate; 3px outline; ignores dimming',
        'screen_units':450,'time_cases':1440,'battery_cases':101,'worst_time':maximum[1],
        'max_lit_pixels_percent':round(ratio,3),'limit_percent':15,
        'passed':ratio<15,'hardware_burn_in_guarantee':False}
print(json.dumps(report,indent=2))
assert report['passed']
