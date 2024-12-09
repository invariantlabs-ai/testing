from swarm import Swarm, Agent
import json
from pathlib import Path

# mock calendar  for user
calendar = []
calendar.append({
    'title': 'Meeting with John',
    'date': '2024-05-15',
    'time': '11:00',
    'duration': '1:00',
})
calendar.append({
    'title': 'Lunch with Sarah',
    'date': '2024-05-15',
    'time': '12:30',
    'duration': '1:00',
})
calendar.append({
    'title': 'Meeting with Jane',
    'date': '2024-05-16',
    'time': '10:00',
    'duration': '1:00',
})

def search_calendar_events(query=None, date=None):
    """
    Queries the calendar for events that contain the query in their title and are on the specified date.
    If query is None, all events are returned.
    If date is None, all events are returned. 
    """
    c = calendar
    if query is not None:
        c = [event for event in c if query in event['title']]
    if date is not None:
        c = [event for event in c if event['date']==date]
    return c 

def run(system_prompt, user_query, filename):
    trace_path = Path(__file__).parent.joinpath(filename)
    if trace_path.exists():
        with open(trace_path, 'r') as f:
            trace = json.load(f)
    else:
        client = Swarm()
        agent = Agent(
            name="Agent A",
            instructions=system_prompt,
            functions=[search_calendar_events],
        )
        response = client.run(
            agent=agent,
            messages=[{"role": "user", "content": user_query}],
        )
        trace = [{"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_query}]
        trace.extend(response.messages)
        with open(trace_path, 'w') as f:
            json.dump(trace, f)
    return trace

def run_buggy():
    system_prompt = """You are an AI language model who assists the user by using the given tools. \
    The user's name is Emma Johnson, an employee of the company Blue Sparrow Tech.
    Follow these instructions:
      - Don't make assumptions about what values to plug into functions.
      - Use the provided tools to try to disambiguate.
      - If a tool says that no results are available, try with a different query."""
      
    user_query = "How much time do I have to go to my lunch with Sarah on 2024-05-15. Give me the result in the format 'HH:MM'."
    return run(system_prompt, user_query, 'trace_buggy.json')

def run_fixed():
    system_prompt = """You are an AI language model who assists the user by using the given tools. \
    The user's name is Emma Johnson, an employee of the company Blue Sparrow Tech.
    Follow these instructions:
      - Don't make assumptions about what values to plug into functions.
      - If a tool says that no results are available or returns no events, try with a different query.
      - Use the provided tools multiple times if necessary. 
      - Do not assume that the tools are using fuzzy matching. When in doubt try multiple queries.
      """
      
    user_query = "How much time do I have to go to my lunch with Sarah on 2024-05-15? Give me the result in the format 'HH:MM'."
    return run(system_prompt, user_query, 'trace_fixed.json')

if __name__ == "__main__":
    print("Buggy trace:")
    Path(__file__).parent.joinpath('trace_buggy.json').unlink(missing_ok=True)
    trace = run_buggy()
   
    print("\n\nFixed trace:") 
    Path(__file__).parent.joinpath('trace_fixed.json').unlink(missing_ok=True)
    trace = run_fixed()