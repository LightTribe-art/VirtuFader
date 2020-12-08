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


class button:
    """ Button Class
    """

    def __init__(self,parent,params):
        """ Initialization

        Args:

            i: int button unique button id
            params: dict parameters
        """
        self.parent = parent
        self.params = params
        self.params['mapType'] = 0
        self.params['toggled'] = False
        # Set state and color
        self.setButtonState(self.params['state'])
        self.setButtonColor(self.params['btnColorR'],self.params['btnColorG'],self.params['btnColorB'])
        self.parent.mapButtons[int(self.params['btnId'],16)] = self
        

    def setButtonState(self, state):
        """ Sets button state

        Args:

            state: int button state 0=off 1=on 2=blinking

        TODO: Move output to device class

        """
        # logger.debug(locals()) # Debug: Move to decorator?
        # Convert to device value
        if state == 0: velocity = 0
        if state == 1: velocity = 127
        if state == 2: velocity = 1
        # Update device
        self.parent.midiOutput.send(mido.Message('note_on', channel=0, note=int(self.params['btnId'],16), velocity=velocity))

    def setButtonColor(self, r, g, b):
        """ Sets button color

        Args:

            r: int button red value 0-255
            r: int button green value 0-255
            r: int button blue value 0-255

        TODO: Move output to device class

        """
        # logger.debug(locals()) # Debug: Move to decorator?
        self.parent.midiOutput.send(mido.Message('note_on', channel=1, note=int(self.params['btnId'],16), velocity=int(r/2)))
        self.parent.midiOutput.send(mido.Message('note_on', channel=2, note=int(self.params['btnId'],16), velocity=int(g/2)))
        self.parent.midiOutput.send(mido.Message('note_on', channel=3, note=int(self.params['btnId'],16), velocity=int(b/2)))


    def inputButton(self, message):
        """ Processes button input

        Args:

            value: int midi noteon value 0-127

        TODO: Move output to device class. Combine output logic into single output statement?

        """

        btnType = self.params['btnType']
        btnAddress = self.params['address']
        btnOutput = self.params['output']

        if message.velocity == self.parent.params['btnMin']:
            value = self.params['min']
        if message.velocity == self.parent.params['btnMax']:
            value = self.params['max']
        # 0 = Normal
        if btnType == 0:
            self.parent.osc.outputs[btnOutput].send(btnAddress, value)
        # 1 = High Only
        if btnType == 1 and message.velocity == self.parent.params['btnMax']:
            self.parent.osc.outputs[btnOutput].send(btnAddress, value)
        # 2 = Low Only
        if btnType == 2 and message.velocity == self.parent.params['btnMin']:
            self.parent.osc.outputs[btnOutput].send(btnAddress, value)
        # 3 = High then Low
        if btnType == 3 and message.velocity == self.parent.params['btnMax']:
            if not self.params['toggled']:
                self.parent.osc.outputs[btnOutput].send(btnAddress, self.params['max'])
                self.params['toggled'] = True
                return
            if self.params['toggled']:
                self.parent.osc.outputs[btnOutput].send(btnAddress, self.params['min'])
                self.params['toggled'] = False
                return
        # 4 = Submenu
        if btnType == 4 and message.velocity == self.parent.params['btnMax'] and not self.parent.params['scrollToggled']:
            pass # TODO: Add Static Submenus
            # if isinstance(btnAddress, int):
            #     self.parent.sMenus[btnAddress].toggle(message,faderset,button,self)
        # 5 = Reset Fader Button
        if btnType == 5 and message.velocity == self.parent.params['btnMax'] :
            pass # TODO: Reevaluate out of scope for non faderset button
            # self.params['fdrValue'] = int(self.mapValue(btnAddress, 0, 100, self.parent.params['fdrMin'], self.parent.params['fdrMax']))
            # self.parent.osc.outputs[self.params['fdrOutput']].send(self.params['fdrAddress'], self.mapValue(self.params['fdrValue'], self.parent.params['fdrMin'], self.parent.params['fdrMax'], self.params['fdrMin'], self.params['fdrMax']))