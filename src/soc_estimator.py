# soc_estimator.py
import numpy as np

class SOC_Estimator:
    def __init__(self, pack, initial_soc=0.9):
        self.pack = pack
        # coulomb counting accumulators per cell (in coulombs)
        self.q_remain = [c.capacity_ah * 3600.0 * c.soc for c in pack.cells]
        self.correction_alpha = 0.02  # small drift correction using voltage

    def coulomb_count_step(self, pack_current, dt):
        # pack_current: positive discharge (A)
        Icell = pack_current / 2.0
        for i, cell in enumerate(self.pack.cells):
            # discharge reduces q_remain (I in A, dt in s -> coulombs)
            self.q_remain[i] -= Icell * dt
            soc = self.q_remain[i] / (cell.capacity_ah * 3600.0)
            cell.soc = max(0.0, min(1.0, soc))

    def voltage_correction(self):
        # a small correction nudging SOC towards voltage-based ocv mapping
        for c in self.pack.cells:
            # compute soc estimate from measured voltage (inverse of ocv_from_soc)
            soc_from_v = (c.voltage - 3.0) / (4.2 - 3.0)
            soc_from_v = max(0.0, min(1.0, soc_from_v))
            # blend
            c.soc = (1 - self.correction_alpha)*c.soc + self.correction_alpha * soc_from_v

    def step(self, pack_current, dt):
        self.coulomb_count_step(pack_current, dt)
        self.voltage_correction()
        return [c.soc for c in self.pack.cells]
