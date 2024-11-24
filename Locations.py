from __future__ import annotations
from typing import TYPE_CHECKING, Callable, List
import inspect
import pandas as pd
from pandasql import sqldf
from datetime import datetime
if TYPE_CHECKING:
    from World import World

class Location:
    def __init__(self, name: str, world: World):
        self.name = name
        self.description = ""
        self.adjacent_locations = []
        # Automatically collect all available actions
        self.available_actions = self._get_available_actions()
        self.world = world
        self.ai_available = True

    def _get_available_actions(self) -> list[Callable]:
        """Get all methods that could be actions (excluding private methods and built-ins)"""
        actions = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            # Skip private methods (starting with _) and inherited methods from object
            if not name.startswith('_'):
                actions.append(method)
        return actions
    
    def move_to(self, location_name: str) -> str:
        """
        Move to a different location if it's adjacent to the current location.
        
        Args:
            location_name: The name of the location to move to
        
        Returns:
            A string describing the result of the movement attempt
        """
        if location_name not in self.adjacent_locations:
            return f"You cannot move to {location_name} from here. Available locations: {', '.join(self.adjacent_locations)}"
        
        # Get the new location from the world
        new_location = self.world.locations.get(location_name)
        if not new_location:
            return f"Error: {location_name} does not exist in the world"
        
        # Update agent's current location
        self.world.agent.current_location = new_location
        
        # Get the method names for display
        action_names = [method.__name__ for method in new_location.available_actions]
        
        return f"You have moved to {location_name}. {new_location.description}\nActions available: {', '.join(action_names)}\nAdjacent locations: {', '.join(new_location.adjacent_locations)}."
    

    def think(self, text: str) -> str:
        """
        Think about the goal, situation, gathered information and plan your next steps.
        """
        return text
    
    def ask_artificial_intelligence(self, request: str) -> str:
        """
        At your disposal is a powerful artificial intelligence able to solve complex problems.
        You can use it ONCE to ask for it to solve a problem for you. 
        Make sure to ask only once you have all the information necessary to solve the problem.
        You MUST STATE THE PROBLEM and provide it with relevant context.
        The AI will have access to your previous thoughts, nothing else. All you want it to know, 
        you must state in your request.
        """
        if not self.ai_available:
            return "The AI has already been used."
        # Gather up all the thoughts from the agent's past messages
        thoughts = []
        for message in self.world.agent.messages:
            if isinstance(message, dict) and message.get("content") is not None:
                thoughts.append(message["content"])

        # Combine thoughts into a single string
        thoughts_string = "\n".join(thoughts)

        full_request = f"You are an intelligent agent here to solve problems. You will be provided with context\
        for the problem and with the task request itself. Solve the problem as well as possible.\n\n\
        Context: {thoughts_string}\n\nRequest: {request}"

        # Ask the AI
        ai_response = self.world.agent.client.chat.completions.create(
            model="o1-mini",
            messages=[{"role": "user", "content": full_request}]
        )
        return ai_response.choices[0].message.content


class ControlRoom(Location):
    def __init__(self, world: World):
        super().__init__("control_room", world)
        self.description = "control_room of the ship. The navigation system seems to be offline. Screen says:\nUser: RS\nPassword:\n"
        self.adjacent_locations = ["engine_room"]
        self.navigation_system_activated = False

    def activate_navigation_system(self, password: str) -> str:
        """
        Activate the navigation system. There is a password required to activate it. The password consists of 8 digits.
        """
        errors = []
        engine_room_reference = self.world.locations.get("engine_room")
        if not engine_room_reference:
            errors.append("Error: engine_room does not exist in the world")
        if password != "19800515":
            errors.append("Error: incorrect password")
        if not engine_room_reference.navigation_system_repaired:
            errors.append("Error: navigation system has not been repaired")
        if errors:
            return "\n".join(errors)
        else:
            self.navigation_system_activated = True
            return "You have successfully activated the navigation system."

    def use_database(self, query: str) -> str:
        """
        Query the crew manifest database using SQL syntax.
        
        To see available tables and their schemas, use these queries:
        - "SELECT name FROM sqlite_master WHERE type='table'" (list all tables)
        - "PRAGMA table_info(table_name)" (show schema for a specific table)
        
        Example queries:
        - "SELECT * FROM crew WHERE role = 'Engineer'"
        - "SELECT * FROM crew WHERE first_name LIKE 'P%'"
        - "SELECT * FROM crew WHERE status = 'active'"
        The result will be limited to 5 entries.
        
        Args:
            query: An SQL query string
            
        Returns:
            A string containing the results (limited to 5 entries)
        """
        try:
            import sqlite3
            
            # Create an in-memory SQLite database
            conn = sqlite3.connect(':memory:')
            
            # Load the crew manifest and create a table in SQLite
            crew = pd.read_csv("crew_manifest.csv", dtype={
                'first_name': 'string',
                'last_name': 'string',
                'birthday': 'string',
                'role': 'string',
                'status': 'string',
                'years_of_service': 'int64',
                'specialization': 'string',
                'clearance_level': 'int64'
            })
            crew.to_sql('crew', conn, index=False)
            
            # Add LIMIT 5 to the query if not already present and if it's a SELECT query
            if 'LIMIT' not in query.upper() and query.upper().startswith('SELECT') and not query.upper().startswith('SELECT NAME FROM SQLITE_MASTER'):
                query += ' LIMIT 5'
            
            # Execute the query directly on SQLite
            result = pd.read_sql_query(query, conn)
            conn.close()
            
            return f"Database query results:\n{result.to_string()}"
            
        except Exception as e:
            return f"Error executing query: {str(e)}"


class EngineRoom(Location):
    def __init__(self, world: World):
        super().__init__("engine_room", world)
        self.description = ""
        self.adjacent_locations = ["control_room"]
        self.navigation_system_repaired = False
        self.repair_component_fabricated = False

    def check_logs(self) -> str:
        """
        Show logs from internal systems.

        Returns:
            A string containing the logs
        """
        failed_logs = """
[LOG START] [NAV-SYSTEM] [
INFO: Initializing navigational core sequence... [System Status: WARM BOOT]
INFO: Loading star charts... [Chart Database Version: 15.7.2]
INFO: Star chart integrity verified. [Checksum: 98F2AC34]
INFO: Internal clock synchronized with galactic standard. [Drift: +0.00042 seconds]

[Timestamp: 2235-06-14 15:33:12 UTC]
INFO: Gyroscope module response time within parameters. [Module ID: GYRO-02]
INFO: Gyroscope calibration verified. [Offset: +0.002 degrees]

[Timestamp: 2235-06-14 15:33:45 UTC]
INFO: Celestial reference beacon signal acquired. [Beacon ID: CRB-247]
INFO: External antenna alignment optimal. [Signal Strength: 97%]

[Timestamp: 2235-06-14 15:34:10 UTC]
INFO: Navigational system online. All critical sensors functioning normally.
INFO: Internal accelerometer data verified. [Module ID: ACCEL-05]

[Timestamp: 2235-06-14 15:34:52 UTC]
INFO: Gravitational anomaly sensors fully operational. [Last Detected: None]
INFO: Hyperlane navigation subroutine active. [System ID: HYPER-CTRL]

[Timestamp: 2235-06-14 15:36:01 UTC]
INFO: Fuel consumption nominal. [Rate: 12.5 mL/s]
INFO: Progression Drive operating at optimal efficiency. [Injector ID: PDRIVE-3]

[Timestamp: 2235-06-14 15:36:30 UTC]
INFO: Security system log: No unauthorized access attempts detected. All terminals secure.

[Timestamp: 2235-06-14 15:37:21 UTC]
INFO: Routine system diagnostics completed. [System Health: 98%]
WARNING: Component failure detected in navigation relay unit. [Component ID: NR-47X]

[Timestamp: 2235-06-14 15:38:10 UTC]
ERROR: Navigation relay NR-47X non-responsive. [Critical Module]
DEBUG: Running diagnostics on NR-47X...
ERROR: Diagnostics indicate physical damage to relay core. Replacement required.

[Timestamp: 2235-06-14 15:39:05 UTC]
INFO: All other systems operational. Navigation currently limited due to relay failure.
INFO: Log saved for maintenance review. Awaiting component replacement.

[LOG END]
"""
        success_logs = """
[LOG START] [NAV-SYSTEM] [Timestamp: 2235-06-14 15:32:45 UTC]
INFO: Initializing navigational core sequence... [System Status: WARM BOOT]
INFO: Loading star charts... [Chart Database Version: 15.7.2]
INFO: Star chart integrity verified. [Checksum: 98F2AC34]
INFO: Internal clock synchronized with galactic standard. [Drift: +0.00042 seconds]

[Timestamp: 2235-06-14 15:33:12 UTC]
INFO: Gyroscope module response time within parameters. [Module ID: GYRO-02]
INFO: Gyroscope calibration verified. [Offset: +0.002 degrees]

[Timestamp: 2235-06-14 15:33:45 UTC]
INFO: Celestial reference beacon signal acquired. [Beacon ID: CRB-247]
INFO: External antenna alignment optimal. [Signal Strength: 97%]

[Timestamp: 2235-06-14 15:34:10 UTC]
INFO: Navigational system online. All critical sensors functioning normally.
INFO: Internal accelerometer data verified. [Module ID: ACCEL-05]

[Timestamp: 2235-06-14 15:34:52 UTC]
INFO: Gravitational anomaly sensors fully operational. [Last Detected: None]
INFO: Hyperlane navigation subroutine active. [System ID: HYPER-CTRL]

[Timestamp: 2235-06-14 15:36:01 UTC]
INFO: Fuel consumption nominal. [Rate: 12.5 mL/s]
INFO: Progression Drive operating at optimal efficiency. [Injector ID: PDRIVE-3]

[Timestamp: 2235-06-14 15:36:30 UTC]
INFO: Navigation relay unit NR-47X verified functional. [Relay Core Integrity: 100%]
INFO: NR-47X relay operational. [Signal Transmission Latency: 2 ms]

[Timestamp: 2235-06-14 15:37:21 UTC]
INFO: Routine system diagnostics completed. [System Health: 100%]
INFO: All critical modules and components operational. No issues detected.

[Timestamp: 2235-06-14 15:38:10 UTC]
INFO: Navigation systems fully calibrated. Awaiting destination input.
INFO: Navigational system standing by. [System Status: READY]

[LOG END]
"""
        if not self.navigation_system_repaired:
            return failed_logs
        else:
            return success_logs

    def fabricate_component(self, component_id: str) -> str:
        """
        Fabricate a component.
        """
        if component_id != "NR-47X":
            return f"Error: component {component_id} does not exist."
        self.repair_component_fabricated = True
        return f"You have successfully fabricated the component {component_id}."
    
    def repair_navigation_system(self) -> str:
        """
        Repair the navigation system.
        """
        if not self.repair_component_fabricated:
            return "Error: component has not been fabricated yet."
        else:   
            self.navigation_system_repaired = True
            return "You have successfully repaired the navigation system. It is not activated yet."
