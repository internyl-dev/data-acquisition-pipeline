
import subprocess
import platform

BAT_SETUP_PATH = "setup\setup.bat"
SH_SETUP_PATH = "setup\setup.sh"

operating_system = platform.system()

if operating_system == "Windows":
    try:
        result = subprocess.run(BAT_SETUP_PATH, capture_output=True, text=True, check=True)
        print("Batch file executed successfully.")
        print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error executing batch file: {e}")
        print("Output:", e.stdout)
        print("Errors:", e.stderr)
    except FileNotFoundError:
        print(f"Batch file not found at: {BAT_SETUP_PATH}")
    
elif operating_system == "Linux" or operating_system == "Darwin":
    try:
        result = subprocess.run([SH_SETUP_PATH], capture_output=True, text=True, check=True)
        print("Shell file executed successfully.")
        print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error executing shell file: {e}")
        print("Output:", e.stdout)
        print("Errors:", e.stderr)
    except FileNotFoundError:
        print(f"Shell file not found at: {SH_SETUP_PATH}")
    except PermissionError:
        print(f"Permission denied. Try running 'source {SH_SETUP_PATH}' at the root directory instead\n"
              f"or change the permissions of this file using 'chmod +x setup.py' at the root directory.")

else:
    print(f"Unknown operating system: {operating_system}")
