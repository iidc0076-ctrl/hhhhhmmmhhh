#!/usr/bin/env python3
"""
Quick test script to verify signal generation with debug output
"""
import asyncio
import sys

# Run a single signal generation to see the debug output
async def main():
    # Import main functions
    from main import generate_signal_for_pair
    
    pair = "EURUSD"
    expiry = "5m"
    mode = "realtime"
    
    print("Testing signal generation with debug output...\n")
    
    try:
        result = await generate_signal_for_pair(pair, expiry, mode)
        
        print("\n✅ Signal generated successfully!")
        print(f"Signal: {result.get('signal', 'UNKNOWN')}")
        print(f"Confidence: {result.get('confidence', 0)}%")
        
    except Exception as e:
        print(f"❌ Error during signal generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
