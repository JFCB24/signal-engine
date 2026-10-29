# Raíz del proyecto en sys.path para que pytest importe config, models, data, backtesting.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
