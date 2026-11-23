# Read-only robot state. Completion must not be inferred from a commanded state.
std_msgs/Header header
uint32 seq
string source
bool fresh

string[] joint_names
float64[] positions
float64[] velocities
float64 gripper_position
float64[] base_duty
float32 battery_voltage

string profile_hash

# measured | commanded
string truth

# bus | timed | open_loop
string verification
