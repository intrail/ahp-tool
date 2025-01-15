import os
import sys

current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

from main import main

if __name__ == "__main__":
    main()
