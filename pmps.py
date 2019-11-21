import json
from os import path

from pydm import Display


class PMPS(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(PMPS, self).__init__(parent=parent, args=args)
        # Read definitions from db file.
        db_path = path.join(path.dirname(path.realpath(__file__)), "db.json")
        ffs = []
        try:
            with open(db_path, 'r') as f:
                ffs = json.load(f)
        except:
            pass

        data = []
        for ff in ffs:
            prefix = ff.get('P', '')
            fid = ff.get('ID', '1')
            start = int(ff.get('START', 1))
            end = int(ff.get('END', 1))
            padding = len(str(end))+1
            for index in range(start, end+1):
                entry = dict()
                entry['P'] = prefix
                entry['ID'] = fid
                entry['INDEX'] = str(index).zfill(padding)
                data.append(entry)
        self.ui.repeater.data = data

    def ui_filename(self):
        return 'pmps.ui'
