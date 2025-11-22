# utils.py
import numpy as np

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def now_str():
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")
