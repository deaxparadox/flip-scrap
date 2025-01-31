import argparse
from importlib import import_module

module = 'sel.app'

def main():
    sel = import_module(module)
    # sel.catch_attr(sel)
    sel.main()
    
    
if __name__ == "__main__":
    main()