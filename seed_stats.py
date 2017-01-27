# -*- coding: utf-8 -*-
"""
@author: podolnik
"""

import json
import codecs
import matplotlib.pyplot as plt
import numpy

seed_stats = [];
with codecs.open('data/seed_stats.json', 'r', encoding='utf8') as f:
    seed_stats = json.loads(f.read())

flat_stats = []
for s in seed_stats:
    flat_stats += s


plt.hist(flat_stats, 20)