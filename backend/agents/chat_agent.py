from langchain.agents import create_agent
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

config = {"configurable": {"thread_id": str(uuid7())}}

class AgentManager():
    def __init__(self, model, tools):
        self.config = config
        self.agent = create_agent(
            model=model,
            tools=tools,
            checkpointer=InMemorySaver(),
        )
        
    def run_agent_stream(self, user_input):
        try:
            stream = self.agent.stream_events(
                {"messages": [{"role": "user", "content": user_input}]},
                config=self.config,
                version="v3",
            )
        except Exception as e:
            print(f"Error invoking the model: {e}")
            
        # Process the stream events and print them in real-time
        for kind, item in stream.interleave("messages", "tool_calls"):  # interleave the messages and tool calls for real-time processing
            if kind == "messages":
                for token in item.text:
                    print(token, end="", flush=True)

            elif kind == "tool_calls":
                print(f"\nTool Execution: {item.tool_name}({item.input})")
                for delta in item.output_deltas:
                    print(delta, end="", flush=True)
                print(f"\nTool Result: {item.output}")

        final_state = stream.output

    def run_agent(self, user_input):
        """
        Run the agent with the given user input and return the response.
        It's meant to be used in the Gradio interface where the response is returned as a string.
        """
        try:
            response = self.agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=self.config,
                version="v3",
            )

            # get last message from the response
            last_message = response["messages"][-1]

            return last_message.content
        
        except Exception as e:
            print(f"Error invoking the model: {e}")
            return f"Error invoking the model: {e}"