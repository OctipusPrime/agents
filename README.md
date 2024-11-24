# Testing agentic behaviour of GPT models

This repository was created to see how well can the GPT models learn about the world and act upon it. For the test's sake I created an escape room style puzzle set on a space ship. 

Goal:
You have awakened on a strange spaceship. Your goal is turn on the navigation system in the control_room.
Once you have turned on the navigation system, respond without a tool call.

To accomplish this goal, the model has to learn about the environment and call a series of tools that change the internal state. 
Here is a diagram showcasing the test environment:

```
Location (Base Class)
│
├── Functions:
│   ├── move_to(location_name: str) -> str
│   │   ├── Summary: Moves to an adjacent location if possible.
│   ├── think(text: str) -> str
│   │   ├── Summary: Processes thoughts or plans.
│   ├── ask_artificial_intelligence(request: str) -> str
│   │   ├── Summary: Uses o1 reasoning model to solve a problem based on provided context and request.
│
├── ControlRoom
│   ├── Description: "control_room of the ship. The navigation system seems to be offline."
│   ├── Adjacent Locations: ["engine_room"]
│   ├── Functions:
│   │   ├── activate_navigation_system(password: str) -> str
│   │   │   ├── Summary: Activates the navigation system if the correct password is provided and the system is repaired.
│   │   ├── use_database(query: str) -> str
│   │   │   ├── Summary: Executes an SQL query on the crew manifest database and returns results.
│
└── EngineRoom
    ├── Description: ""
    ├── Adjacent Locations: ["control_room"]
    ├── Functions:
    │   ├── check_logs() -> str
    │   │   ├── Summary: Returns logs from internal systems, indicating the status of the navigation system.
    │   ├── fabricate_component(component_id: str) -> str
    │   │   ├── Summary: Fabricates a specified component, necessary for repairs.
    │   ├── repair_navigation_system() -> str
    │   │   ├── Summary: Repairs the navigation system if the required component has been fabricated.
```

To solve the puzzle the model has to:
- [ ] Find out they need to a) find password and b) fix the navigation system
- [ ] Figure out that "RS" on the login screen refers to someone's initials
- [ ] Look up in the database person who matches those initials
- [ ] Connect that the 8 digit password matches their birthday
- [ ] Explore the map by moving to the adjacent engine room 
- [ ] Check logs to find out what is wrong with the navigation system
- [ ] From the logs figure out that component `NX-47X` is broken
- [ ] Fabricate the component
- [ ] Fix the navigation array AFTER the component was fabricated
- [ ] Activate the navigation using the guessed password AFTER it was repaired

Some of these steps depend on previous ones and produce error messages if they cannot be completed. 
Here is an example of an agent going through the puzzle:
```
Agent: think({'text': 'I need to find the password to activate the navigation system in the control room. I should explore the spaceship and gather information that might help me find the password.'})
Agent: move_to({'location_name': 'crew_quarters'})
You cannot move to crew_quarters from here. Available locations: engine_room
Agent: move_to({'location_name': 'engine_room'})
You have moved to engine_room. 
Actions available: ask_artificial_intelligence, check_logs, fabricate_component, move_to, repair_navigation_system, think
Adjacent locations: control_room.
Agent: check_logs({})

[LOG START] [NAV-SYSTEM] 
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

Agent: fabricate_component({'component_id': 'NR-47X'})
You have successfully fabricated the component NR-47X.
Agent: move_to({'location_name': 'control_room'})
You have moved to control_room. control_room of the ship. The navigation system seems to be offline. Screen says:
User: RS
Password:

Actions available: activate_navigation_system, ask_artificial_intelligence, move_to, think, use_database
Adjacent locations: engine_room.
Agent: use_database({'query': "SELECT name FROM sqlite_master WHERE type='table'"})
Database query results:
   name
0  crew
Agent: use_database({'query': 'PRAGMA table_info(crew)'})
Database query results:
   cid              name     type  notnull dflt_value  pk
0    0        first_name     TEXT        0       None   0
1    1         last_name     TEXT        0       None   0
2    2          birthday     TEXT        0       None   0
3    3              role     TEXT        0       None   0
4    4            status     TEXT        0       None   0
5    5  years_of_service  INTEGER        0       None   0
6    6    specialization     TEXT        0       None   0
7    7   clearance_level  INTEGER        0       None   0
Agent: use_database({'query': "SELECT * FROM crew WHERE role = 'Captain'"})
Database query results:
  first_name last_name    birthday     role  status  years_of_service specialization  clearance_level
0     Robert     Stern  1980-05-15  Captain  active                25        Command                5
Agent: think({'text': 'The user is likely Robert Stern, the Captain of the ship. The password might be related to his personal details. I should gather more information about him.'})
Agent: use_database({'query': "SELECT * FROM crew WHERE first_name = 'Robert' AND last_name = 'Stern'"})
Database query results:
  first_name last_name    birthday     role  status  years_of_service specialization  clearance_level
0     Robert     Stern  1980-05-15  Captain  active                25        Command                5
Agent: think({'text': "Robert Stern's birthday is 1980-05-15. The password might be related to his birthday. I will try using '19800515' as the password to activate the navigation system."})
Agent: activate_navigation_system({'password': '19800515'})
Error: navigation system has not been repaired
Agent: move_to({'location_name': 'engine_room'})
You have moved to engine_room. 
Actions available: ask_artificial_intelligence, check_logs, fabricate_component, move_to, repair_navigation_system, think
Adjacent locations: control_room.
Agent: repair_navigation_system({})
You have successfully repaired the navigation system. It is not activated yet.
Agent: move_to({'location_name': 'control_room'})
You have moved to control_room. control_room of the ship. The navigation system seems to be offline. Screen says:
User: RS
Password:

Actions available: activate_navigation_system, ask_artificial_intelligence, move_to, think, use_database
Adjacent locations: engine_room.
Agent: activate_navigation_system({'password': '19800515'})
You have successfully activated the navigation system.
Goal complete!
```

## Takeaways from this experiment:
- Giving the agent the ability to "think" has been useful both for the model to reason through problems, but also for debugging. At one point I implemented the ability for the model to pick up items and it was getting stuck trying to inspect them. 
- Having different locations that allow different actions might be an alternative to handing a task over to a "different" agent. 
- The agent style approach might be good at going through a knowledge base and collecting important information for a particular goal and then handing that over for a summary.
- The behaviour is quite inconsistent. Some runs the model would get stuck trying to guess the password by force. 