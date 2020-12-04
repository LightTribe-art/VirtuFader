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


# Configure Logging
import logging
from logging.handlers import RotatingFileHandler
# Init Root Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # TODO: Set level based on options.
# Init Handlers
fh = logging.handlers.RotatingFileHandler('logs/virtufader.log',maxBytes=1000000, backupCount=2)
ch = logging.StreamHandler()
# Init Formatter
formatter = logging.Formatter('[%(asctime)s] [%(filename)s:%(lineno)s:%(funcName)s:%(levelname)s] %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# Add Handlers
logger.addHandler(fh)
logger.addHandler(ch)

# Standard Imports
import asyncio
import yaml
import time

# Main Init
async def mainInit():

    # Extended Imports
    from classes.option import option
    from classes.osc import osc, output
    from classes.device import device
    from classes.faderset import faderset
    from classes.button import button
    from classes.encoder import encoder
    from classes.vfader import vfader
    from classes.smenu import smenu

    # Load Options
    with open('conf/options.yaml') as file:
        options = yaml.load(file, Loader=yaml.FullLoader)
    
    # Load Device Objects
    devices = []
    with open('conf/devices.yaml') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        for d in range(len(config)):

            # Append Device
            devices.append(device(config[d]))

            # Load OSC Object
            devices[d].loadOsc(osc(devices[d],options['oscServerIp'],options['oscServerPort']))
            with open('conf/outputs.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                for i in range(len(config)):
                    devices[d].osc.loadOutput(output(devices[d].osc,config[i]))

            # Load Faderset Objects
            with open('conf/fadersets.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                for i in range(len(config)):
                    devices[d].loadFaderset(i,faderset(devices[d],config[i]))

            # Load Button Objects
            with open('conf/buttons.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                for i in range(len(config)):
                    devices[d].loadButton(int(config[i]['btnId'],16),button(devices[d],config[i]))

            # Load Encoder Objects
            with open('conf/encoders.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                for i in range(len(config)):
                    devices[d].loadEncoder(int(config[i]['encId'],16),encoder(devices[d],config[i]))

            # Load vFader Objects
            with open('conf/vfaders.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                for i in range(len(config)):
                    devices[d].loadVFader(vfader(devices[d],config[i],0))
                    devices[d].vFaders[i].registerOscFilters()

            # Load sFader Objects
            with open('conf/sfaders.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                for i in range(len(config)):
                    devices[d].loadSFader(vfader(devices[d],config[i],1))
                    devices[d].sFaders[i].registerOscFilters()

            # Load sMenu Objects
            with open('conf/smenus.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                for i in range(len(config)):
                    devices[d].loadSMenu(smenu(devices[d],config[i]))

            # Sync vFader to Fadersets
            for i in range(len(devices[d].vFaders)):
                devices[d].vFaders[i].mapTarget = devices[d].fadersets[i]
                devices[d].vFaders[i].fadersetSync('all')

            # Start OSC Server
            transport, protocol = await devices[d].osc.server.create_serve_endpoint()
    
    # Debug Available MIDI In/Out Ports
    #if options['dbgMidiPort']: printMidiInfo()
    await mainLoop(devices)
    transport.close()


# Main Loop
async def mainLoop(devices):
    # Non call
    while True:
        # vFader Scroll Long Press Handler
        if devices[0].params['scrollPressedTime'] is not None:
            if time.time() - devices[0].params['scrollPressedTime'] > 1:
                devices[0].scrollToggle()
                devices[0].params['scrollPressedTime'] = None
        await asyncio.sleep(1)

asyncio.run(mainInit())