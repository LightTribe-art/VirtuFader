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
logger = logging.getLogger(__name__)


import asyncio
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient


class osc:

    def __init__(self, parent,oscServerIp,oscServerPort):
        super().__init__()
        self.parent = parent
        self.outputs = []
        self.inputDispatcher = Dispatcher()
        self.server = AsyncIOOSCUDPServer((oscServerIp,oscServerPort),self.inputDispatcher,asyncio.get_event_loop())
        logger.debug(locals())

    def loadOutput(self,output):
        self.outputs.append(output)

    def registerFilter(self, address, path):
        logger.debug(locals())
        self.inputDispatcher.map(address,path)


class output:
    
    def __init__(self,parent,params):
        super().__init__()
        self.parent = parent
        self.params = params
        self.client = SimpleUDPClient(self.params['ip'], self.params['port'])

    def send(self,address,value):
        if isinstance(address, str) and len(address) > 0:
            self.client.send_message(address,value)