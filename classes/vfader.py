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
import textwrap
logger = logging.getLogger(__name__)


class vfader:

    def __init__(self,parent,params,vfType):
        self.parent = parent
        self.params = params
        self.mapTarget = None
        self.params['fdrValue'] = self.parent.params['fdrMin']
        self.params['dimmed'] = 0
        self.params['displayPercent'] = 0
        self.params['type'] = vfType
        self.btnToggle = [False]*len(self.params['buttons'])
        logger.debug(locals())

    def setDisplayName(self,string,split):
        displayText0 = ''
        displayText1 = ''
        if len(string) > split:
            strSplit = textwrap.wrap(string, split)
            displayText0 = strSplit[0]
            if len(strSplit[1]) > 0:
                displayText1 = strSplit[1]
        else:
            displayText0 = string
        self.params['displayText0'] = displayText0
        self.params['displayText1'] = displayText1

    def mapValue(self, i, xMin, xMax, yMin, yMax):
        """ Map value from one range to another

        Args:
            i: Input
            xMin: Input range minimum
            xMax: Input range maximum
            yMin: Output range minimum
            yMan: Output range maximum
        """
        xSpan = int(xMax) - int(xMin)
        ySpan = int(yMax) - int(yMin)
        iScaled = (float(i) - int(xMin)) / xSpan
        return int(yMin) + (iScaled * ySpan)

    def registerOscFilters(self):
        if isinstance(self.params['fdrAddress'], str) and len(self.params['fdrAddress']) > 0:
            self.parent.osc.registerFilter(self.params['fdrAddress'], self.inputOsc)
        if isinstance(self.params['displayTextAddress'], str) and len(self.params['displayTextAddress']) > 0 and self.params['displayTextMode'] == 1:
            self.parent.osc.registerFilter(self.params['displayTextAddress'], self.inputOsc)
        for i in range(len(self.params['buttons'])):
            if isinstance(self.params['buttons'][i]['address'], str) and len(self.params['buttons'][i]['address']) > 0:
                self.parent.osc.registerFilter(self.params['buttons'][i]['address'], self.inputOsc)

    def inputOsc(self, address, *args):
        # Fader Input
        if address == self.params['fdrAddress']:
            # Set Fader Value and Sync
            self.params['fdrValue'] = int(self.mapValue(args[0], self.params['fdrMin'], self.params['fdrMax'], self.parent.params['fdrMin'], self.parent.params['fdrMax']))
            self.fadersetSync('fader')
            # Set Display Percent and Sync
            self.params['displayPercent'] = round(self.mapValue(args[0], self.params['fdrMin'], self.params['fdrMax'], 0, 100))
            self.fadersetSync('display')
            return
        # Dynamic Display Text
        if address == self.params['displayTextAddress']:
            # Set Display Name and Sync
            self.setDisplayName(args[0], self.parent.params['displaySplit'])
            self.fadersetSync('display')
            return

    def inputFader(self, message):
        self.params['fdrValue'] = message.pitch
        self.parent.osc.outputs[self.params['fdrOutput']].send(self.params['fdrAddress'], self.mapValue(message.pitch, self.parent.params['fdrMin'], self.parent.params['fdrMax'], self.params['fdrMin'], self.params['fdrMax']))
        self.params['displayPercent'] = round(self.mapValue(message.pitch, self.parent.params['fdrMin'],  self.parent.params['fdrMax'], 0, 100))
        self.fadersetSync('display')

    def inputButton(self,message,button,faderset):
        """ Processes button input

        Args:

            value: int midi noteon value 0-127

        """

        btnType = self.params['buttons'][button]['type']
        btnAddress = self.params['buttons'][button]['address']
        btnOutput = self.params['buttons'][button]['output']

        if message.velocity == self.parent.params['btnMin']:
            value = self.params['buttons'][button]['min']
        if message.velocity == self.parent.params['btnMax']:
            value = self.params['buttons'][button]['max']

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
        if btnType == 3:
            if not self.btnToggle[button]:
                self.parent.osc.outputs[btnOutput].send(btnAddress, self.params['max'])
                self.btnToggle[button] = True
                return
            if self.btnToggle[button]:
                self.parent.osc.outputs[btnOutput].send(btnAddress, self.params['min'])
                self.btnToggle[button] = False
                return
        # 4 = Submenu
        if btnType == 4 and message.velocity == self.parent.params['btnMax'] and not self.parent.params['scrollToggled']:
            if isinstance(btnAddress, int):
                self.parent.sMenus[btnAddress].toggle(message,faderset,button,self)
        # 5 = Reset Fader Button
        if btnType == 5 and message.velocity == self.parent.params['btnMax'] :
            self.params['fdrValue'] = int(self.mapValue(btnAddress, 0, 100, self.parent.params['fdrMin'], self.parent.params['fdrMax']))
            self.parent.osc.outputs[self.params['fdrOutput']].send(self.params['fdrAddress'], self.mapValue(self.params['fdrValue'], self.parent.params['fdrMin'], self.parent.params['fdrMax'], self.params['fdrMin'], self.params['fdrMax']))

    def openSubmenu(self, faderset):
        self.mapTarget = faderset
        self.fadersetSync('all')

    def closeSubmenu(self, faderset, vfId):
        self.parent.vFaders[vfId].fadersetSync('all')

    # Sync to faderset
    def fadersetSync(self,element):
        # Map Target
        if element == 'mapTarget' or element == 'all' or element == 'scroll':
            if self.mapTarget is not None:
                self.mapTarget.mapTarget = self
        # Everything else
        if self.mapTarget is not None and self.mapTarget.mapTarget == self:
            # Fader
            if element == 'fader' or element == 'all' or element == 'scroll':
                #if not self.parent.params['smToggled']:
                self.mapTarget.setFaderPosition(self.params['fdrValue'])
            # Select Button
            if element == 'buttons' or element == 'all' or element == 'scroll':
                for i in range(len(self.params['buttons'])):
                    if not element == 'scroll':
                        self.mapTarget.setButtonState(i,self.params['buttons'][i]['state'])
                    if self.params['buttons'][i]['r'] is not None and self.params['buttons'][i]['g'] is not None and self.params['buttons'][i]['b'] is not None:
                        if self.params['state'] == 0:
                            self.mapTarget.setButtonColor(i,10,10,10)
                        else: 
                            self.mapTarget.setButtonColor(i,self.params['buttons'][i]['r'],self.params['buttons'][i]['g'],self.params['buttons'][i]['b'])
            # Display
            if element == 'display' or element == 'all' or element == 'scroll':
                # Set highlight
                if self.params['dimmed'] == 1: highlight = 0
                if self.params['dimmed'] == 0: highlight = 1
                # Set Order
                if self.params['type'] == 0: order = [0,1,2]
                if self.params['type'] == 1: order = [1,2,0]
                # State = Disabled
                if self.params['state'] == 0:
                    self.mapTarget.setDisplay(order[0], 0, '', 0)
                    self.mapTarget.setDisplay(order[1], 0, '', 0)
                    self.mapTarget.setDisplay(order[2], 0, '', 0)
                # State = Enabled
                if self.params['state'] == 1:
                        # Static Mode
                        if self.params['displayTextMode'] == 0:
                            if self.params['displayText0'] is not None:
                                self.mapTarget.setDisplay(order[0],highlight,self.params['displayText0'],self.params['type'])
                            if self.params['displayText1'] is not None:
                                self.mapTarget.setDisplay(order[1],highlight,self.params['displayText1'],self.params['type'])
                            if self.params['displayPercent'] is not None:
                                self.mapTarget.setDisplay(order[2],0,str(self.params['displayPercent'])+'%',self.params['type'])
                        # Dynamic Mode
                        if self.params['displayTextMode'] == 1:
                            # Without Value
                            if len(self.params['displayText0']) == 0:
                                self.mapTarget.setDisplay(order[0],0,'',self.params['type'])
                                self.mapTarget.setDisplay(order[1],0,'(dynamic)',self.params['type'])
                                self.mapTarget.setDisplay(order[2],0,'',self.params['type'])
                            # With Value
                            if len(self.params['displayText0']) > 0:
                                self.mapTarget.setDisplay(order[0],highlight,self.params['displayText0'],self.params['type'])
                                self.mapTarget.setDisplay(order[1],highlight,self.params['displayText1'],self.params['type'])
                                self.mapTarget.setDisplay(order[2],0,str(self.params['displayPercent'])+'%',self.params['type'])