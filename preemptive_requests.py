import json
from qtpy import QtWidgets
from pydm import Display
from pydm.widgets import PyDMEmbeddedDisplay


class PreemptiveRequests(Display):
    def __init__(self, parent=None, args=None, macros=None):
        super(PreemptiveRequests, self).__init__(parent=parent, args=args, macros=macros)
        self.config = macros
        self.setup_ui()

    def setup_ui(self):
        self.setup_requests()

    def setup_requests(self):
        if not self.config:
            return
        reqs = self.config.get('preemptive_requests')
        if not reqs:
            return
        reqs_container = self.ui.reqs_content
        if reqs_container is None:
            return
        count = 0
        for req in reqs:
            prefix = req.get('prefix')
            arbiter = req.get('arbiter_instance')
            pool_start = req.get('assertion_pool_start')
            pool_end = req.get('assertion_pool_end')

            pool_zfill = len(str(pool_end)) + 1

            template = 'templates/preemptive_requests_entry.ui'
            for pool_id in range(pool_start, pool_end+1):
                pool = str(pool_id).zfill(pool_zfill)
                macros = dict(index=count, P=prefix, ARBITER=arbiter, POOL=pool)
                widget = PyDMEmbeddedDisplay(parent=reqs_container)
                widget.macros = json.dumps(macros)
                widget.filename = template
                widget.disconnectWhenHidden = False
                reqs_container.layout().addWidget(widget)
                count += 1

        print(f'Added {count} preemptive requests')

    def ui_filename(self):
        return 'preemptive_requests.ui'
