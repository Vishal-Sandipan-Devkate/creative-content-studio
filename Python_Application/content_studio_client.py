"""
Creative Content Studio AI Agent Client
========================================
An AI agent that autonomously uses the Content Studio MCP server to create multimedia content.

This client demonstrates:
- Dynamic tool discovery
- Multi-step reasoning with tools
- Context preservation across tool calls
- Intelligent decision-making about which tools to use
"""

import asyncio
import json
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
import sys

from numpy import rint
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

anthropic_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

if not anthropic_client.api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not found in .env")
class ContentStudioAgent:
    """AI Agent that manages creative content generation tasks"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.available_tools = []
        
    async def connect_to_server(self, server_script_path: str):
        from mcp.client.stdio import stdio_client
        from mcp import ClientSession, StdioServerParameters

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path],
            env=None,
        )

    # IMPORTANT: keep this context alive
        self._stdio_cm = stdio_client(server_params)
        self._read, self._write = await self._stdio_cm.__aenter__()

        self.session = ClientSession(self._read, self._write)
        await self.session.initialize()

        response = await self.session.list_tools()
        self.available_tools = response.tools

        print(f"✅ Connected to MCP server")
        print(f"📦 Tools discovered: {[t.name for t in self.available_tools]}")


    async def call_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool via MCP and return the result"""
        try:
            result = await self.session.call_tool(tool_name, arguments=tool_input)
            # Extract the text content from the result
            if hasattr(result, 'content') and len(result.content) > 0:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Tool execution failed: {str(e)}"
            })
    
    async def process_query(self, user_query: str, max_iterations: int = 10) -> str:
        """
        Process a user query using the AI agent loop.
        
        The agent will:
        1. Analyze the query
        2. Decide which tools to use
        3. Execute tools
        4. Reason about results
        5. Continue until task is complete
        
        Args:
            user_query: The user's creative content request
            max_iterations: Maximum number of agent reasoning loops
        
        Returns:
            Final response from the agent
        """
        messages = [
            {
                "role": "user",
                "content": user_query
            }
        ]
        
        # Agent reasoning loop
        for iteration in range(max_iterations):
            print(f"\n🤖 Agent Iteration {iteration + 1}/{max_iterations}")
            
            # Call Claude with available tools
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=self.format_tools_for_claude(),
                messages=messages
            )
            
            # Check if agent wants to use tools
            if response.stop_reason == "tool_use":
                # Add assistant response to message history
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Execute all requested tools
                tool_results = []
                
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        
                        print(f"   🔧 Calling tool: {tool_name}")
                        print(f"      Input: {json.dumps(tool_input, indent=2)[:100]}...")
                        
                        # Execute the tool
                        result = await self.call_tool(tool_name, tool_input)
                        
                        print(f"      ✅ Result: {result[:100]}...")
                        
                        # Add tool result to history
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                
                # Add tool results to message history
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            
            elif response.stop_reason == "end_turn":
                # Agent has finished - extract final response
                final_response = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_response += block.text
                
                print(f"\n✅ Agent completed task in {iteration + 1} iterations")
                return final_response
            
            else:
                # Unexpected stop reason
                return f"Agent stopped unexpectedly: {response.stop_reason}"
        
        return "Agent reached maximum iterations without completing task"
    
    async def cleanup(self):
        if self.session:
            await self.session.close()
            
        if hasattr(self, "_stdio_cm"):
            await self._stdio_cm.__aexit__(None, None, None)


    
    async def interactive_mode(self):
        """Run the agent in interactive chat mode"""
        print("=" * 70)
        print("🎨 CREATIVE CONTENT STUDIO - AI AGENT")
        print("=" * 70)
        print("\nWhat would you like to create today?")
        print("\nExamples:")
        print("  • 'Create a YouTube thumbnail for my AI tutorial'")
        print("  • 'Make a QR code for my website and a social card'")
        print("  • 'Generate a voiceover for this script: [your text]'")
        print("  • 'Create a video montage from these images: [paths]'")
        print("\nType 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Process the query
                response = await self.process_query(user_input)
                
                print(f"\n🎨 Agent: {response}\n")
                print("-" * 70)
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")

async def main():
    import sys

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    server_path = sys.argv[1] if len(sys.argv) > 1 else "content_studio_server.py"

    agent = ContentStudioAgent()

    server_params = StdioServerParameters(
        command="python",
        args=[server_path],
        env=None
    )

    async with stdio_client(server_params) as (stdio, write):
        session = ClientSession(stdio, write)
        await session.initialize()

        await agent.connect_to_server(session)
        await agent.interactive_mode()
