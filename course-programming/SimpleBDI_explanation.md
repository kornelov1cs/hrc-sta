# SimpleBDI Notebook Explanation

## Overview of `SimpleBDI.ipynb`

This notebook implements a **BDI (Belief-Desire-Intention) Agent** for a home assistant robot. It's a classic AI architecture that models how autonomous agents make decisions and act.

---

## What It Does:

### **The Environment** (WorldState class)
A simple simulated home with:
- **3 rooms**: kitchen, living_room, hallway
- **2 objects**: coffee_mug (starts in kitchen), book (starts in living_room)
- **User**: starts in living_room, randomly walks around (20% chance per tick)
- **Robot**: starts in hallway with 100% battery
- **Charging dock**: located in hallway

### **The BDI Agent** (BDI_Agent class)

The robot operates on a **BDI cycle** each tick:

#### 1. **BELIEFS** (Perception)
- Updates its mental model of the world
- Tracks: robot location, user location, object locations, battery level

#### 2. **DESIRES** (Goals)
The robot has 3 desires with different priorities:
- **Priority 3** (Highest): Deliver morning coffee to user
- **Priority 2** (Medium): Tidy the living room (put book on shelf in hallway)
- **Priority 1** (Lowest): Recharge when battery ≤ 20%

#### 3. **INTENTIONS** (Plans)
- Selects the highest-priority unfulfilled desire
- Creates a simple plan (sequence of actions) to achieve it
- Example plans:
  - **Deliver coffee**: move to kitchen → pick up mug → move to user → give mug
  - **Tidy book**: move to living room → pick up book → move to hallway → put down book
  - **Recharge**: move to hallway → dock

#### 4. **ACTIONS** (Execution)
- Executes one step of the plan per tick
- Actions: move, pick, put, give, dock

---

## Example Run (from output):

```
TICK 0-5: Robot delivers coffee
  - Moves to kitchen, picks up mug
  - User walks to kitchen (random)
  - Robot tries to give mug in living_room (fails - user not there!)
  - Robot adapts: moves back to kitchen where user is
  - Successfully hands over coffee ✓

TICK 6-9: Robot tidies book
  - Moves to living_room, picks up book
  - Moves to hallway, puts down book ✓

TICK 10+: Robot idles
  - No active desires (coffee delivered, book tidied, battery still OK)
  - User randomly walks around
```

---

## Key Features:

### **Reactive Behavior**
- The robot re-evaluates its beliefs after each action
- If the world changes (e.g., user moves), the robot adapts its plan

### **Priority-Based Decision Making**
- Battery is lowest priority (only triggers at 20%)
- Coffee delivery is highest priority
- Robot always pursues the most important unfulfilled goal

### **Simple Planning**
- Hand-coded plans for each desire
- Sequential execution (one action at a time)

---

## Limitations (Acknowledged in Code):

The notebook explicitly states this is a **"toy" implementation** that ignores:
- Uncertainty
- Concurrency (doing multiple things at once)
- Complex planning
- Real-world complications

---

## Suggested Extensions (Cell 3):

1. **More objects & desires**: Add water glass, vacuum cleaning
2. **Belief persistence**: Track when beliefs become "stale"
3. **Path-finding**: Use A* or BFS for navigation through a room graph
4. **Dynamic priorities**: Calculate priority based on deadline, user mood, battery urgency

---

## Real-World Relevance:

BDI architectures are used in:
- **Autonomous robots** (service robots, drones)
- **Multi-agent systems** (traffic management, swarm robotics)
- **Game AI** (NPC behavior)
- **Decision support systems**

The key idea: agents should model their goals (desires), reason about how to achieve them (intentions), and maintain a consistent world model (beliefs).

