# battery_model.py
"""
Simple 2s2p pack model.
Each cell is modelled as: Vocv(SOC) - R_internal * I
Also includes temperature rise model (lumped thermal capacitance + convective cooling)
"""
import numpy as np

class Cell:
    def __init__(self, capacity_ah=2.5, r_internal=0.05, nominal_voltage=3.7, c_th=200.0, r_th=0.5):
        self.capacity_ah = capacity_ah
        self.r_internal = r_internal
        self.nominal_voltage = nominal_voltage
        self.c_th = c_th    # thermal capacitance J/°C
        self.r_th = r_th    # thermal resistance to ambient
        self.soc = 0.9
        self.temp = 25.0    # Celsius
        self.voltage = self.ocv_from_soc(self.soc)

    def ocv_from_soc(self, soc):
        # simple linear approx between 3.0 and 4.2 V
        return 3.0 + soc * (4.2 - 3.0)

    def step(self, current, dt, ambient_temp=25.0):
        # current positive = discharge
        dv = - self.r_internal * current
        self.voltage = self.ocv_from_soc(self.soc) + dv
        dq = - current * dt / 3600.0  # Ah change
        self.soc = max(0.0, min(1.0, self.soc + dq / self.capacity_ah))
        # thermal: Joule heating I^2 R, convection to ambient
        p_heat = (current**2) * self.r_internal  # watts
        dtemp = (p_heat - (self.temp - ambient_temp)/self.r_th) * (dt / self.c_th)
        self.temp += dtemp
        return self.voltage

class Pack2s2p:
    def __init__(self):
        # construct 4 cells: arranged as two parallel groups in series (2s2p)
        self.cells = [Cell() for _ in range(4)]
        # mapping: group0 = cells[0], cells[1] -> series leg A
        #           group1 = cells[2], cells[3] -> series leg B

    def pack_voltage(self):
        # average voltage of parallel groups then sum series legs
        v_legA = (self.cells[0].voltage + self.cells[1].voltage) / 2.0
        v_legB = (self.cells[2].voltage + self.cells[3].voltage) / 2.0
        return v_legA + v_legB

    def step(self, pack_current, dt, ambient_temp=25.0):
        # pack_current positive = discharge
        # each parallel cell sees half the pack current
        Icell = pack_current / 2.0
        voltages = []
        for i, cell in enumerate(self.cells):
            v = cell.step(Icell, dt, ambient_temp)
            voltages.append(v)
        return voltages

    def cell_states(self):
        return [{
            'voltage': c.voltage,
            'soc': c.soc,
            'temp': c.temp
        } for c in self.cells]
