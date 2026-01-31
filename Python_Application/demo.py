"""
Demo Script for Creative Content Studio
========================================
Pre-configured demo queries for quick hackathon presentations.

Run this to see the agent in action without typing!
"""

import asyncio
import sys
from content_studio_client import ContentStudioAgent


DEMO_QUERIES = [
    {
        "title": "Simple Thumbnail Generation",
        "query": "Create a bold YouTube thumbnail with the text 'AI Agents Explained' on a blue background",
        "expected_tools": ["generate_thumbnail"],
        "description": "Demonstrates basic tool usage with custom styling"
    },
    {
        "title": "QR Code for Website",
        "query": "Generate a QR code for https://github.com with red color",
        "expected_tools": ["generate_qr_code"],
        "description": "Shows QR code generation with custom colors"
    },
    {
        "title": "Social Media Package",
        "query": "Create a Twitter social card with title 'Join Our Hackathon' and subtitle '24 hours of innovation' in colorful theme",
        "expected_tools": ["create_social_card"],
        "description": "Platform-specific social media content"
    },
    {
        "title": "Multi-Tool Workflow",
        "query": "Create a complete branding package: a thumbnail saying 'Tech Conference 2025', a QR code for https://techconf.com, and a LinkedIn social card announcing the event",
        "expected_tools": ["generate_thumbnail", "generate_qr_code", "create_social_card"],
        "description": "Agent autonomously chains multiple tools"
    },
    {
        "title": "Text-to-Speech Demo",
        "query": "Convert this to speech: 'Welcome to the future of AI-powered content creation. This demo showcases autonomous agents working with creative tools.'",
        "expected_tools": ["text_to_speech"],
        "description": "Audio generation capabilities"
    }
]


async def run_demo():
    """Run automated demo of all capabilities"""
    print("=" * 80)
    print("🎬 CREATIVE CONTENT STUDIO - AUTOMATED DEMO")
    print("=" * 80)
    print("\nThis demo will showcase all 5 tools through pre-configured queries.\n")
    
    # Initialize agent
    agent = ContentStudioAgent()
    
    try:
        # Connect to server
        server_path = sys.argv[1] if len(sys.argv) > 1 else "content_studio_server.py"
        await agent.connect_to_server(server_path)
        
        # Run each demo
        for i, demo in enumerate(DEMO_QUERIES, 1):
            print("\n" + "=" * 80)
            print(f"📌 DEMO {i}/{len(DEMO_QUERIES)}: {demo['title']}")
            print("=" * 80)
            print(f"Description: {demo['description']}")
            print(f"Expected Tools: {', '.join(demo['expected_tools'])}")
            print(f"\nQuery: {demo['query']}")
            print("\n" + "-" * 80)
            
            # Process query
            response = await agent.process_query(demo['query'])
            
            print(f"\n🎨 Final Response:\n{response}")
            
            # Pause between demos
            if i < len(DEMO_QUERIES):
                print("\n⏸️  Press Enter to continue to next demo...")
                input()
        
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETE!")
        print("=" * 80)
        print("\nCheck the 'content_outputs/' directory for all generated files.")
        print("All tools have been demonstrated successfully! 🎉\n")
    
    finally:
        await agent.cleanup()


async def run_custom_demo():
    """Run interactive demo mode"""
    print("=" * 80)
    print("🎨 CREATIVE CONTENT STUDIO - CUSTOM DEMO MODE")
    print("=" * 80)
    print("\nQuick Examples:")
    for demo in DEMO_QUERIES[:3]:
        print(f"  • {demo['query']}")
    print()
    
    agent = ContentStudioAgent()
    
    try:
        server_path = sys.argv[1] if len(sys.argv) > 1 else "content_studio_server.py"
        await agent.connect_to_server(server_path)
        await agent.interactive_mode()
    finally:
        await agent.cleanup()


def print_usage():
    """Print usage instructions"""
    print("""
🎬 Creative Content Studio Demo Script

Usage:
  python demo.py [mode] [server_path]

Modes:
  auto     - Run automated demo with pre-configured queries (default)
  custom   - Interactive mode where you type your own queries

Examples:
  python demo.py                              # Run automated demo
  python demo.py auto                         # Run automated demo
  python demo.py custom                       # Interactive mode
  python demo.py auto content_studio_server.py  # Specify server path

For hackathon presentations, we recommend 'auto' mode!
""")


async def main():
    """Main entry point"""
    import os
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Parse command line arguments
    mode = "auto"
    if len(sys.argv) > 1 and sys.argv[1] in ["auto", "custom", "help", "-h", "--help"]:
        mode = sys.argv[1]
    
    if mode in ["help", "-h", "--help"]:
        print_usage()
        return
    
    # Run appropriate mode
    if mode == "custom":
        await run_custom_demo()
    else:
        await run_demo()


if __name__ == "__main__":
    asyncio.run(main())
