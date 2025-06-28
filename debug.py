#!/usr/bin/env python3
"""
Debug script to test Tosu websocket connection and data format
Run this script to see what data Tosu is actually sending
"""

import asyncio
import websockets
import json
import sys

WEBSOCKET_URI = "ws://localhost:24050/ws"


async def debug_tosu():
    print("🔍 Debugging Tosu connection...")
    print(f"Connecting to: {WEBSOCKET_URI}")

    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            print("✅ Connected successfully!")
            print("📡 Listening for data... (Press Ctrl+C to stop)")
            print("-" * 60)

            message_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    message_count += 1

                    try:
                        data = json.loads(message)
                        print(f"\n📨 Message #{message_count}:")
                        print(f"Data type: {type(data)}")

                        if isinstance(data, dict):
                            print("📊 Available keys:", list(data.keys()))

                            # Check gameplay data
                            if "gameplay" in data:
                                gameplay = data["gameplay"]
                                print(f"🎮 Gameplay type: {type(gameplay)}")
                                if isinstance(gameplay, dict):
                                    print(f"🎮 Gameplay keys: {list(gameplay.keys())}")

                                    # Check combo data
                                    if "combo" in gameplay:
                                        combo = gameplay["combo"]
                                        print(f"🔢 Combo data: {combo} (type: {type(combo)})")

                                    # Check accuracy
                                    if "accuracy" in gameplay:
                                        acc = gameplay["accuracy"]
                                        print(f"🎯 Accuracy: {acc} (type: {type(acc)})")

                                    # Check HP
                                    if "hp" in gameplay:
                                        hp = gameplay["hp"]
                                        print(f"❤️ HP data: {hp} (type: {type(hp)})")

                                    # Check hits
                                    if "hits" in gameplay:
                                        hits = gameplay["hits"]
                                        print(f"👊 Hits data: {hits} (type: {type(hits)})")

                            # Check menu data
                            if "menu" in data:
                                menu = data["menu"]
                                print(f"📋 Menu type: {type(menu)}")
                                if isinstance(menu, dict):
                                    print(f"📋 Menu keys: {list(menu.keys())}")

                                    # Check state
                                    if "state" in menu:
                                        state = menu["state"]
                                        print(f"🎲 State data: {state} (type: {type(state)})")
                                        if isinstance(state, dict) and "name" in state:
                                            print(f"🎲 State name: {state['name']}")

                                    # Check beatmap data
                                    if "bm" in menu:
                                        bm = menu["bm"]
                                        print(f"🗺️ Beatmap type: {type(bm)}")
                                        if isinstance(bm, dict) and "metadata" in bm:
                                            metadata = bm["metadata"]
                                            print(f"📝 Metadata: {metadata} (type: {type(metadata)})")
                        else:
                            print(f"⚠️ Data is not a dict: {data}")

                        # Show first few messages in detail
                        if message_count <= 3:
                            print("📜 Full message content:")
                            print(
                                json.dumps(data, indent=2)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data,
                                                                                                                   indent=2))

                        print("-" * 60)

                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        print(f"Raw message: {message[:200]}...")

                except asyncio.TimeoutError:
                    print("⏰ No data received in 10 seconds, sending ping...")
                    await websocket.ping()

    except ConnectionRefusedError:
        print("❌ Connection refused! Make sure Tosu is running.")
        print("   Download Tosu from: https://github.com/tosuapp/tosu")
        print("   Default port should be 24050")
        return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

    return True


def main():
    print("🚀 Tosu Debug Tool")
    print("This tool will help identify issues with the Tosu connection")
    print()

    try:
        asyncio.run(debug_tosu())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()