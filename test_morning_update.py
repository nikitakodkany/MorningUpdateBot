import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.morning_update import main

if __name__ == "__main__":
    print("Starting morning update test...")
    main()
    print("Morning update test completed.") 