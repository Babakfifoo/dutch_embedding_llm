import os
import sys

# Workaround for the KMP Duplicate Lib error if it exists
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def check_environment():
    print("--- Environment Check ---")
    print(f"Python Version: {sys.version}")
    
    try:
        import torch
        print(f"PyTorch Version: {torch.__version__}")
        
        # Test basic tensor operation (this triggers DLL loading)
        x = torch.rand(5, 3)
        print("Successfully created a tensor (shm.dll loaded correctly).")
        
        # Check GPU availability
        if torch.cuda.is_available():
            print(f"GPU Detected: {torch.cuda.get_device_name(0)}")
        else:
            print("No GPU detected. PyTorch will run on CPU.")
            
    except ImportError as e:
        print(f"ERROR: PyTorch is not installed correctly: {e}")
    except OSError as e:
        print(f"ERROR: DLL loading failed: {e}")
        print("\nTip: Reinstall the MSVC C++ Redistributable (x64).")

    try:
        import marker
        print("Marker library found and imported successfully.")
    except ImportError:
        print("ERROR: 'marker' module not found. Run 'pip install marker-pdf'.")

if __name__ == "__main__":
    check_environment()