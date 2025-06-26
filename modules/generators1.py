import os
import json
import logging
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
import networkx as nx
from config import Config
import time
import re

logger = logging.getLogger(__name__)