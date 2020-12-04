# This file is part of VirtuFader.
#
# VirtuFader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# VirtuFader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VirtuFader.  If not, see <https://www.gnu.org/licenses/>.


import logging
import mido
logger = logging.getLogger(__name__)


class smenu:

    def __init__(self, parent, params):
        super().__init__()
        self.parent = parent
        self.params = params
        self.toggledBy = None

    def getParam(self, param):
        return self.params[param]

    def setParam(self, param, value):
        self.params[param] = value

    def toggle(self,message,faderset,button,vFader):
        # Return is submenu is already open
        if self.parent.params['smToggled'] and self.parent.params['smToggledBy'] != message.note: return
        # Open Submenu
        if not self.parent.params['smToggled']:
            # Set Triggering Button's State
            faderset.setButtonState(button,2)
            # Dim Non-Submenu Faders
            for vF in self.parent.vFaders:
                if vF != vFader:
                    vF.params['dimmed'] = 1
                    vF.fadersetSync('display')
            # Get Submenu Parameters
            if self.params['direction'] == 0: sMenuStart = faderset.params['fdrId'] - self.params['count']
            if self.params['direction'] == 1: sMenuStart = faderset.params['fdrId'] + 1
            # Display Submenus
            for i in range(self.params['count']):
                self.parent.sFaders[self.params['start'] + i].openSubmenu(self.parent.fadersets[sMenuStart + i])
            # Set Toggle Params
            self.toggledBy = vFader
            self.parent.params['smToggledBy'] = message.note
            self.parent.params['smToggled'] = True
            return
        # Close Submenu
        if self.parent.params['smToggled']:
            self.parent.params['smToggled'] = False
            # Set Triggering Button's State
            faderset.setButtonState(button,2)
            # UnDim Non-Submenu Faders
            for vF in self.parent.vFaders:
                vF.params['dimmed'] = 0
                vF.fadersetSync('all')
            return