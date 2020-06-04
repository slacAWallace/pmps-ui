import yaml
import json
import itertools
from os import path
from qtpy import QtWidgets
from pydm import Display
from pydm.widgets import PyDMEmbeddedDisplay


class PMPS(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(PMPS, self).__init__(parent=parent, args=args, macros=macros)
        # Read definitions from db file.
        cfg = path.join(path.dirname(path.realpath(__file__)), "config.yml")
        self.config = {}
        with open(cfg, 'r') as f:
            self.config = yaml.safe_load(f)
        self.setup_ui()

    def setup_ui(self):
        self.setup_tabs()
        splitter = self.findChild(QtWidgets.QSplitter, "main_splitter")
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def setup_tabs(self):
        # We will do crazy things at this screen... avoid painting
        self.setUpdatesEnabled(False)

        self.setup_fastfaults()

        # We are done... re-enable painting
        self.setUpdatesEnabled(True)

    def setup_fastfaults(self):
        ffs = self.config.get('fastfaults')
        if not ffs:
            return
        ff_container = self.findChild(QtWidgets.QWidget, "fastfaults_content")
        if ff_container is None:
            return
        count = 0
        for ff in ffs:
            prefix = ff.get('prefix')
            ffo_start = ff.get('ffo_start')
            ffo_end = ff.get('ffo_end')
            ff_start = ff.get('ff_start')
            ff_end = ff.get('ff_end')

            ffos_zfill = len(str(ffo_end)) + 1
            ffs_zfill = len(str(ff_end)) + 1

            entries = itertools.product(
                range(ffo_start, ffo_end+1),
                range(ff_start, ff_end+1)
            )
            template = 'templates/fastfaults_entry.ui'
            for _ffo, _ff in entries:
                s_ffo = str(_ffo).zfill(ffos_zfill)
                s_ff = str(_ff).zfill(ffs_zfill)
                macros = dict(index=count, P=prefix, FFO=s_ffo, FF=s_ff)
                widget = PyDMEmbeddedDisplay(parent=ff_container)
                widget.macros = json.dumps(macros)
                widget.filename = template
                widget.disconnectWhenHidden = False
                ff_container.layout().addWidget(widget)
                count += 1
        verticalSpacer = QtWidgets.QSpacerItem(20, 40,
                                               QtWidgets.QSizePolicy.Minimum,
                                               QtWidgets.QSizePolicy.Expanding)
        ff_container.layout().addItem(verticalSpacer)
        print(f'Added {count} fast faults')

    def ui_filename(self):
        return 'main.ui'
