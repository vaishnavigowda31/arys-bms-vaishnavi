# can_simulator.py
import csv, os
from datetime import datetime

class CANLogger:
    def __init__(self, out_file='results/can_logs/can_log.csv'):
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        self.out_file = out_file
        self._header_written = False

    def log(self, msg_id, data_dict):
        now = datetime.now().isoformat()
        row = {'timestamp': now, 'id': msg_id}
        # flatten values to strings or numbers
        for k,v in data_dict.items():
            row[k] = v
        write_header = not self._header_written
        with open(self.out_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            if write_header:
                writer.writeheader()
                self._header_written = True
            writer.writerow(row)

def encode_bms_message(cell_states):
    # cell_states: list of dicts with keys 'voltage','soc','temp'
    pack = {}
    # compute pack voltage as series of two parallel legs
    v_legA = (cell_states[0]['voltage'] + cell_states[1]['voltage']) / 2.0
    v_legB = (cell_states[2]['voltage'] + cell_states[3]['voltage']) / 2.0
    pack['pack_voltage'] = round(v_legA + v_legB,3)
    pack['avg_soc'] = round(sum(c['soc'] for c in cell_states)/len(cell_states),3)
    pack['max_temp'] = round(max(c['temp'] for c in cell_states),2)
    return pack
