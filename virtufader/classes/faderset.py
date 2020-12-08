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


class faderset:

    def __init__(self,parent,params):
        self.parent = parent
        self.params = params
        self.mapTarget = None
        self.mapButtons = [None]*128
        for i in range(len(self.params['btnIds'])):
            # Update Parrent Button Map
            self.parent.mapButtons[int(self.params['btnIds'][i],16)] = self
            # Update Local Button Submap
            self.mapButtons[int(self.params['btnIds'][i],16)] = i

    def setFaderPosition(self, value):
        self.parent.midiOutput.send(mido.Message('pitchwheel', channel=self.params['fdrId'], pitch=value))

    def setButtonState(self,button,state):
        if state == 0: velocity = 0
        if state == 1: velocity = 127
        if state == 2: velocity = 1
        self.parent.midiOutput.send(mido.Message('note_on', channel=0, note=int(self.params['btnIds'][button],16), velocity=velocity))

    def setButtonColor(self,button,r,g,b):
        self.parent.midiOutput.send(mido.Message('note_on', channel=1, note=int(self.params['btnIds'][button],16), velocity=int(r/2)))
        self.parent.midiOutput.send(mido.Message('note_on', channel=2, note=int(self.params['btnIds'][button],16), velocity=int(g/2)))
        self.parent.midiOutput.send(mido.Message('note_on', channel=3, note=int(self.params['btnIds'][button],16), velocity=int(b/2)))

    def setDisplay(self, line, invert, content, mode):
        logger.debug(locals())
        if invert == 1: invert = 4
        # Set Display Mode
        if mode == 0:
            midiOutMsg = mido.Message('sysex', data=[0, 1, 6, 22, 19, self.params['fdrId'], 0]) # TODO: Remove hard reference to SYSEX header
            self.parent.midiOutput.send(midiOutMsg)
        if mode == 1:
            midiOutMsg = mido.Message('sysex', data=[0, 1, 6, 22, 19, self.params['fdrId'], 1]) # TODO: Remove hard reference to SYSEX header
            self.parent.midiOutput.send(midiOutMsg)
        # Set Text
        midiOutMsg = mido.Message('sysex', data=[0, 1, 6, 22, 18, self.params['fdrId'], line, invert])
        midiOutMsg.data += bytearray(content, 'utf8')
        self.parent.midiOutput.send(midiOutMsg)

    def inputFader(self,message):
        self.mapTarget.inputFader(message)

    def inputButton(self,message):
        self.mapTarget.inputButton(message,self.mapButtons[message.note],self)