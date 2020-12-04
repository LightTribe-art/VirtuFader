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
''' Device Module

Main device module
'''

import logging
import mido
import time
logger = logging.getLogger(__name__)


class device:

    def __init__(self,params):
        super().__init__()
        # Init Logging
        logger.debug(locals())
        # Load Params
        self.params = params
        self.params['smToggled'] = False
        self.params['smToggledBy'] = None
        self.params['scrollToggled'] = False
        self.params['scrollPressedTime'] = None
        # Load Config Object Shells
        self.fadersets = [None]*128
        self.buttons = [None]*128
        self.encoders = [None]*128
        self.vFaders = []
        self.sFaders = []
        self.sMenus = []
        self.oscOutputs = [None]
        self.osc = None
        # Connect to MIDI
        self.midiInput = mido.open_input(self.params['midiInput'], callback=self.inputMidi)
        self.midiOutput = mido.open_output(self.params['midiOutput'])
        self.mapButtons = [None]*128

    def loadOsc(self,osc):
        self.osc = osc
    
    def loadFaderset(self,i,faderset):
        self.fadersets[i] = faderset

    def loadButton(self,i,button):
        self.buttons[i] = button
    
    def loadEncoder(self,i,encoder):
        self.encoders[i] = encoder

    def loadVFader(self,vFader):
        self.vFaders.append(vFader)

    def loadSFader(self,sFader):
        self.sFaders.append(sFader)

    def loadSMenu(self,sMenu):
        self.sMenus.append(sMenu)

    def scrollButton(self,message):
        if self.params['smToggled']: return  # Don't scroll if submenu is open
        if message.velocity == 127:
            self.params['scrollPressedTime'] = time.time()
        if message.velocity == 0:
            self.params['scrollPressedTime'] = None

    def scrollToggle(self):
        if not self.params['scrollToggled']:
            for i in range(self.params['fadersetCount']):
                for button in self.fadersets[i].params['btnIds']:
                    self.midiOutput.send(mido.Message('note_on', channel=0, note=int(button,16), velocity=1))
            self.params['scrollToggled'] = True
            return
        if self.params['scrollToggled']:
            self.params['scrollToggled'] = False
            for vFader in self.vFaders:
                vFader.fadersetSync('all')
            return
            
    def scrollCc(self, value):
        if self.params['scrollToggled']:
            offset = 0
            if value >= 65 and vFaders[len(vFaders)-1].getParam('pfMap') > len(fadersets)-1:
                offset = -1
            if value <= 64 and vFaders[0].getParam('pfMap') < 0:
                offset = 1
            for vFader in vFaders:
                vFader.setParam('pfMap', vFader.getParam('pfMap') + offset)
                vFader.pfSync('route')
                vFader.pfSync('all')
            return

    def inputMidi(self, message):
        ''' Input Handler from MIDO

        Args:
        message (mido.message): Message object from MIDO
        '''
        # Prioritize Fader Input
        if message.type == "pitchwheel":
            self.fadersets[message.channel].inputFader(message)
        # Scroll Button Override
        if message.type == "note_on" and message.note == int(self.params['scrollBtnId'],16):
            self.scrollButton(message)
        # Button
        if message.type == "note_on" and self.mapButtons[message.note] is not None:
            self.mapButtons[message.note].inputButton(message)
        # Encoder
        if message.type == "control_change":
            self.encoders[message.control].inputEncoder(message)