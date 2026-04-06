import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent import create_agent

load_dotenv()


def save_trip(content: str):
    """Save itinerary to a markdown file."""
    filename = "trip_itinerary.md"
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"\n💾 Itinerary saved to {filepath}\n")

def main():
    """Run the trip planner agent."""
    
    print("\n🌍 Smart Trip Planner")
    print("=" * 50)
    
    # Create the agent
    print("Setting up your travel agent...")
    agent = create_agent()
    
    # # Save the graph visualization
    # try:
    #     mermaid_text = agent.get_graph(xray=True).draw_mermaid()
    #     print("\n📊 Agent graph structure:")
    #     print(mermaid_text)
        
    #     png_data = agent.get_graph(xray=True).draw_mermaid_png()
    #     with open("agent_graph.png", "wb") as f:
    #         f.write(png_data)
    #     print("(Graph image saved to agent_graph.png)\n")
    # except Exception as e:
    #     print(f"(Could not generate graph image: {e})\n")
        
    print("=" * 50)
    print("Tell me about your dream trip! I'll help you plan it.")
    print("Type 'quit' to exit.\n")
    
    # Initialize state
    state = {
        "messages": [],
        "preferences": {},
        "planning_stage": "gathering",
        "research_count": 0,
        "itinerary_draft": "",
    }
    
    while True:
        # Multiline input support
        print("You: (press Enter twice to send)")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        user_input = " ".join(lines).strip()

        if not user_input:
            continue        

        # Handle save command
        if user_input.lower() in ["save", "save it", "yes save", "save to file"]:
            draft = state.get("itinerary_draft", "")
            if draft:
                save_trip(draft)
            else:
                print("\n⚠️ No itinerary to save yet.\n")
            continue
        
        # Handle quit
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Happy travels! 👋")
            break
        
        # Input validation
        if len(user_input) > 5000:
            print("\n⚠️ Message too long. Please keep it under 5000 characters.\n")
            continue
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_input))
        
        try:
            print("\n🤖 Agent: ", end="", flush=True)
            final_content = ""

            for event in agent.stream(state, stream_mode="updates"):
                for node_name, node_output in event.items():
                    # Show progress for each node
                    if node_name == "extract":
                        print("\n📋 Got your preferences! Researching...", flush=True)
                        print("🤖 Agent: ", end="", flush=True)

                    if node_name == "research":
                        print("\n🔍 Researching your trip...", flush=True)
                        print("🤖 Agent: ", end="", flush=True)

                    if node_name == "tools":
                        print("🛠️  Using search tools...", flush=True)
                        print("🤖 Agent: ", end="", flush=True)

                    if node_name == "build":
                        print("\n🏗️  Building your itinerary...", flush=True)
                        print("🤖 Agent: ", end="", flush=True)

                    if node_name == "reflect":
                        print("\n🔎 Reviewing the plan...", flush=True)
                        print("🤖 Agent: ", end="", flush=True)

                    # Capture messages from this node
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if hasattr(msg, "content") and msg.content:
                                # Skip internal routing keywords
                                if "PLANNING_READY" in msg.content:
                                    continue
                                if "PLAN_APPROVED" in msg.content:
                                    continue
                                final_content = msg.content

                    # Update itinerary draft if present
                    if "itinerary_draft" in node_output:
                        state["itinerary_draft"] = node_output["itinerary_draft"]

                    # Update preferences if present
                    if "preferences" in node_output:
                        state["preferences"] = node_output["preferences"]

                    # Update research count
                    if "research_count" in node_output:
                        state["research_count"] = node_output["research_count"]

            # Print final response
            if final_content:
                print(final_content, flush=True)
            print()

            # Update messages in state from the last event
            if "messages" in node_output:
                state["messages"] = state.get("messages", [])
                for msg in node_output["messages"]:
                    if msg not in state["messages"]:
                        state["messages"].append(msg)
                        
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted. Type 'quit' to exit or continue chatting.\n")
            continue
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower():
                print(f"\n⚠️ Rate limited by API. Wait a moment and try again.\n")
            elif "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                print(f"\n❌ API key error. Check your .env file.\n")
            elif "timeout" in error_msg.lower():
                print(f"\n⚠️ Request timed out. Please try again.\n")
            else:
                print(f"\n❌ Error: {e}")
                print("Something went wrong. Please try again.\n")
            continue
            
if __name__ == "__main__":
    main()