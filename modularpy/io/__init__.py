"""
This allows for importing the SerialWorker class directly 
from the io module. as so:

from modularpy.io import SerialWorker

rather than:

from modularpy.io.encoder import SerialWorker
"""
from .encoder import SerialWorker
