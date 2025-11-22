# bms_controller.py
from collections import defaultdict
import numpy as np

class BMSController:
    def __init__(self, pack, soc_estimator,
                 ov_thresh=4.25, uv_thresh=2.7,
                 ot_thresh=60.0, ut_thresh=0.0,
                 max_discharge_current=10.0):
        self.pack = pack
        self.est = soc_estimator
        self.ov = ov_thresh
        self.uv = uv_thresh
        self.ot = ot_thresh
        self.ut = ut_thresh
        self.max_discharge_current = max_discharge_current
        self.state = 'NORMAL'
        # persistence counters
        self.counters = [defaultdict(int) for _ in pack.cells]
        self.persist_limit = 3  # number of consecutive steps to escalate

        # balancing targets (simple passive bleed)
        self.balance_threshold = 0.02  # SOC difference to start balancing

    def check_cell_faults(self):
        faults = []
        for i, c in enumerate(self.pack.cells):
            cell_faults = []
            if c.voltage > self.ov:
                self.counters[i]['ov'] += 1
            else:
                self.counters[i]['ov'] = 0
            if c.voltage < self.uv:
                self.counters[i]['uv'] += 1
            else:
                self.counters[i]['uv'] = 0
            if c.temp > self.ot:
                self.counters[i]['ot'] += 1
            else:
                self.counters[i]['ot'] = 0
            if c.temp < self.ut:
                self.counters[i]['ut'] += 1
            else:
                self.counters[i]['ut'] = 0

            # escalate if persistency reached
            if self.counters[i]['ov'] >= self.persist_limit:
                cell_faults.append('OVERVOLTAGE')
            if self.counters[i]['uv'] >= self.persist_limit:
                cell_faults.append('UNDERVOLTAGE')
            if self.counters[i]['ot'] >= self.persist_limit:
                cell_faults.append('OVERTEMP')
            if self.counters[i]['ut'] >= self.persist_limit:
                cell_faults.append('UNDERTEMP')
            faults.append(cell_faults)
        return faults

    def check_pack_faults(self, pack_current):
        pack_faults = []
        if abs(pack_current) > self.max_discharge_current:
            pack_faults.append('OVERCURRENT')
        return pack_faults

    def balancing_actions(self):
        socs = [c.soc for c in self.pack.cells]
        avg = np.mean(socs)
        actions = []
        for i, s in enumerate(socs):
            if s - avg > self.balance_threshold:
                # cell i is high -> bleed
                actions.append((i, 'BLEED'))
            else:
                actions.append((i, 'IDLE'))
        return actions

    def cooling_control(self):
        # if any cell temp > 60 -> emergency shutdown
        temps = [c.temp for c in self.pack.cells]
        if any(t > 60 for t in temps):
            return 'EMERGENCY_SHUTDOWN'
        if any(t > 45 for t in temps):
            return 'COOLING_ON'
        return 'COOLING_OFF'

    def step(self, pack_current):
        cell_faults = self.check_cell_faults()
        pack_faults = self.check_pack_faults(pack_current)
        balancing = self.balancing_actions()
        cooling = self.cooling_control()

        # priority: emergency temp -> shutdown
        if cooling == 'EMERGENCY_SHUTDOWN':
            self.state = 'SHUTDOWN'
        elif any(len(f)>0 for f in cell_faults) or len(pack_faults)>0:
            # if faults exist, enter FAULT
            self.state = 'FAULT'
        else:
            # normal
            self.state = 'NORMAL'
        return {
            'state': self.state,
            'cell_faults': cell_faults,
            'pack_faults': pack_faults,
            'balancing': balancing,
            'cooling': cooling
        }
