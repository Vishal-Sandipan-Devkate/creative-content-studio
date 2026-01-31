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
import sys
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


class ContentStudioAgent:
    """AI Agent that manages creative content generation tasks"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.available_tools = []
    
    def format_tools_for_claude(self) -> list[dict]:
        """Convert MCP tools to Claude API format"""
        claude_tools = []
        
        for tool in self.available_tools:
            claude_tool = {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            claude_tools.append(claude_tool)
        
        return claude_tools
    
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
            print(f"\n��� Agent Iteration {iteration + 1}/{max_iterations}")
            
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
                        
                        print(f"   ��� Calling tool: {tool_name}")
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
    
    async def interactive_mode(self):
        """Run the agent in interactive chat mode"""
        print("=" * 70)
        print("��� CREATIVE CONTENT STUDIO - AI AGENT")
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
                    print("\n��� Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Process the query
                response = await self.process_query(user_input)
                
                print(f"\n🤖 Agent: {response}\n")
                print("-" * 70)
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")


async def main():
    """Main entry point"""
    import sys
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Determine server script path
    if len(sys.argv) > 1:
        server_path = sys.argv[1]
    else:
        server_path = "content_studio_server.py"
    
    # Create and run agent
    agent = ContentStudioAgent()
    
    await agent.connect_to_server(server_path)
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

