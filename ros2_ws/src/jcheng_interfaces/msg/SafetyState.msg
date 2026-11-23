# Fail-closed safety state. A missing or stale state is treated as STOP_LATCHED.
std_msgs/Header header
uint32 seq

# DISARMED | ARMED_IDLE | MOTION_ACTIVE | STOP_LATCHED | FAULT
string state
bool stop_latched

string[] violation_codes
string[] violations

# Hashes of the safety configuration and robot profile used by this state.
string config_hash
string profile_hash

builtin_interfaces/Time last_valid_state_at
