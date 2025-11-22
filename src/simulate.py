# simulate.py
import os
import matplotlib.pyplot as plt
import numpy as np
from src.battery_model import Pack2s2p
from src.soc_estimator import SOC_Estimator
from src.bms_controller import BMSController
from src.can_simulator import CANLogger, encode_bms_message
from src.utils import now_str

def run_simulation(sim_time_s=600, dt=1.0, ambient_temp=25.0, out_dir='results'):
    os.makedirs(out_dir, exist_ok=True)
    pack = Pack2s2p()
    est = SOC_Estimator(pack)
    bms = BMSController(pack, est)
    can = CANLogger(out_file=f"{out_dir}/can_logs/can_{now_str()}.csv")

    times = []
    cell_voltages = [[] for _ in pack.cells]
    cell_temps = [[] for _ in pack.cells]
    cell_socs = [[] for _ in pack.cells]
    bms_states = []
    cooling_states = []

    # simulate a drive profile: 0-100s idle, 100-400 discharge at 5A, 400-500 heavy discharge 12A (overcurrent), 500-600 rest
    def drive_current(t):
        if t < 100: return 0.0
        if t < 400: return 5.0
        if t < 500: return 12.0
        return 0.0

    steps = int(sim_time_s/dt)
    for step in range(steps):
        t = step*dt
        I = drive_current(t)
        voltages = pack.step(I, dt, ambient_temp)
        socs = est.step(I, dt)
        ctrl = bms.step(I)

        # log CAN frame every 5 seconds
        if step % 5 == 0:
            states = pack.cell_states()
            payload = encode_bms_message(states)
            # add cell-wise telemetry compactly
            for idx, st in enumerate(states):
                payload[f'v{idx}'] = round(st['voltage'],3)
                payload[f'soc{idx}'] = round(st['soc'],3)
                payload[f't{idx}'] = round(st['temp'],2)
            can.log(msg_id='0x100', data_dict=payload)

        # record
        times.append(t)
        for i,c in enumerate(pack.cells):
            cell_voltages[i].append(c.voltage)
            cell_temps[i].append(c.temp)
            cell_socs[i].append(c.soc)
        bms_states.append(ctrl['state'])
        cooling_states.append(ctrl['cooling'])

    # plotting
    plot_dir = f"{out_dir}/plots"
    os.makedirs(plot_dir, exist_ok=True)

    # voltages
    plt.figure(figsize=(8,4))
    for i in range(len(pack.cells)):
        plt.plot(times, cell_voltages[i], label=f'cell{i}_V')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.title('Cell Voltages')
    plt.grid(True)
    plt.savefig(f"{plot_dir}/cell_voltages.png", dpi=150)
    plt.close()

    # temps
    plt.figure(figsize=(8,4))
    for i in range(len(pack.cells)):
        plt.plot(times, cell_temps[i], label=f'cell{i}_T')
    plt.xlabel('Time (s)')
    plt.ylabel('Temp (°C)')
    plt.legend()
    plt.title('Cell Temperatures')
    plt.grid(True)
    plt.savefig(f"{plot_dir}/cell_temps.png", dpi=150)
    plt.close()

    # socs
    plt.figure(figsize=(8,4))
    for i in range(len(pack.cells)):
        plt.plot(times, cell_socs[i], label=f'cell{i}_SOC')
    plt.xlabel('Time (s)')
    plt.ylabel('SOC')
    plt.legend()
    plt.title('Cell SOCs')
    plt.grid(True)
    plt.savefig(f"{plot_dir}/cell_socs.png", dpi=150)
    plt.close()

    print("Simulation complete. Plots saved in:", plot_dir)
    print("CAN logs saved in:", f"{out_dir}/can_logs")
    return {
        'times': times,
        'voltages': cell_voltages,
        'temps': cell_temps,
        'socs': cell_socs,
        'bms_states': bms_states
    }

if __name__ == '__main__':
    run_simulation()
