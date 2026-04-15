import os
import asyncio
import argparse
from browser_use import Agent, ChatGoogle, Browser
from dotenv import load_dotenv

load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="IT Support AI Agent")
    parser.add_argument("task", type=str, help="Natural language description of the IT task.")
    args = parser.parse_args()

    # Verify API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY environment variable is not set. Please set it in a .env file or environment.")
        return

    print(f"Task: {args.task}")
    print("Initializing Gemini...")
    
    # Initialize the heavily optimized native browser-use LLM completely untouched
    llm = ChatGoogle(model="gemini-3-flash-preview")
    
    # Prepend the task with instructions to go to the local app
    full_task = (
        f"Go to http://localhost:5000 and complete this task: {args.task}. "
        f"If the task requires adding a user, navigate to the Add User page, fill out the form, and submit it. "
        f"If the task requires resetting a password or disabling an account, find the user in the Dashboard table and click the corresponding action button."
    )

    print("Initializing Browser-Use agent...")
    # By default, Browser-Use runs in headed mode so we can watch it.
    # Set wait_between_actions so it visually slows down clicking and typing
    browser = Browser(wait_between_actions=2.0)
    agent = Agent(
        task=full_task,
        llm=llm,
        browser=browser,
    )

    print("Running agent...")
    result = await agent.run()
    
    print("\n--- Agent Execution Complete ---")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
