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


class encoder:
    
    def __init__(self,parent,params):
        self.parent = parent
        self.params = params

    def inputEncoder(self, message):
        # vFader Scrolling
        if self.parent.params['scrollToggled'] and message.control == int(self.parent.params['scrollCcId'],16):
            # Left
            if message.value >= 65:
                # End Stop
                try:
                    if self.parent.vFaders[len(self.parent.vFaders)-1].mapTarget.params['fdrId'] == self.parent.params['fadersetCount']-1: return
                except:
                    pass
                # Remainder
                for i in range(len(self.parent.vFaders)):
                    if self.parent.vFaders[i].mapTarget is not None:
                        mapTarget = self.parent.vFaders[i].mapTarget.params['fdrId']
                        if mapTarget == 0:
                            self.parent.vFaders[i].mapTarget = None
                        if 1 <= mapTarget <= self.parent.params['fadersetCount']-1:
                            self.parent.vFaders[i].mapTarget = self.parent.fadersets[mapTarget-1]
                            self.parent.vFaders[i].fadersetSync('scroll')
                        if mapTarget == self.parent.params['fadersetCount']-1:
                            self.parent.vFaders[i+1].mapTarget = self.parent.fadersets[self.parent.params['fadersetCount']-1]
                            self.parent.vFaders[i+1].fadersetSync('scroll')
                            return
            # Right
            if message.value <= 64:
                # End Stop
                try:
                    if self.parent.vFaders[0].mapTarget.params['fdrId'] == 0: return
                except:
                    pass
                # Remainder
                for i in range(len(self.parent.vFaders)):
                    if self.parent.vFaders[i].mapTarget is not None:
                        mapTarget = self.parent.vFaders[i].mapTarget.params['fdrId']
                        if mapTarget == 0:
                            self.parent.vFaders[i-1].mapTarget = self.parent.fadersets[0]
                            self.parent.vFaders[i-1].fadersetSync('scroll')
                        if 0 <= mapTarget <= self.parent.params['fadersetCount']-2:
                            self.parent.vFaders[i].mapTarget = self.parent.fadersets[mapTarget+1]
                            self.parent.vFaders[i].fadersetSync('scroll')
                        if mapTarget == self.parent.params['fadersetCount']-1:
                            self.parent.vFaders[i].mapTarget = None
                            

        # Regular Encoder
        else:
            if message.value >= 65:
                if self.params['overrideDownValue'] is not None:
                    value = self.params['overrideDownValue']
                else:
                    value = message.value
                self.parent.osc.outputs[self.params['output']].send(self.params['addressDown'], value)
            # Up
            if message.value <= 64:
                if self.params['overrideUpValue'] is not None:
                    value = self.params['overrideUpValue']
                else:
                    value = message.value
                self.parent.osc.outputs[self.params['output']].send(self.params['addressUp'], value)