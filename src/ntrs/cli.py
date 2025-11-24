import argparse
import sys
import os
from .core import NTRS

def main():
    parser = argparse.ArgumentParser(description="NTRS Nebula: Zero-Point Optical Encryption Tool")
    parser.add_argument('mode', choices=['encrypt', 'decrypt'], help="Mode: Encrypt or Decrypt")
    parser.add_argument('--text', help="Text to encrypt")
    parser.add_argument('--image', required=True, help="Path to input/output image file")
    parser.add_argument('--password', required=True, help="Password for Zero-Point Map Encryption")
    
    args = parser.parse_args()
    engine = NTRS(password=args.password)
    
    if args.mode == 'encrypt':
        if not args.text:
            print("Error: --text is required.")
            sys.exit(1)
        print(f"--- ENCRYPTING: Creating NTRS Dot ---")
        engine.encode(args.text, args.image)
        print(f"SUCCESS: Saved to {args.image}")
        
    elif args.mode == 'decrypt':
        print(f"--- DECRYPTING: Reading NTRS Dot ---")
        if not os.path.exists(args.image):
            print(f"Error: File {args.image} not found.")
            sys.exit(1)
        result = engine.decode(args.image)
        print("\n" + "="*40)
        print(f"DECRYPTED MESSAGE: {result}")
        print("="*40 + "\n")

if __name__ == "__main__":
    main()