test_system_prompt = """
You are a helpful assistant.
"""

test_tool_use_prompt = """
You were given a set of tools to use. Use the tools to find items in the current location.
"""

nudge_prompt = """
Your task is not completed. Try new ways to use your tools to complete your task. \
The task has been created in a way that guarantees it is possible to complete.
"""

system_prompt = """
You are an intelligent agent. There are tools available to you that can help you complete your task.
Use a tool call and provide necessary variables to progress toward your goal. The only way for you to
complete your task is to use a series of tool calls. Some tools may require information gathered elsewhere 
or may require you to possess certain items. When you don't know what to do, experiment with tools that you 
haven't used yet or explore new locations. Each location has a set of tools available to you. Some tools are shared
but most are unique to a location. Use your intelligence to decide the order of tools that will allow you to complete
your task.
"""

goal_prompt = """
You are locked in an unfamiliar house. Your goal is to escape. You must find a key to unlock the entry door. 
Once you have unlocked the door, respond without a tool call. 
"""