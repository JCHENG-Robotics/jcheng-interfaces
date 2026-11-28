# Reserved high-rate teleoperation stream. Consumed by the motion arbiter only;
# still validated by the same safety path. Not a hardware command.
std_msgs/Header header
uint64 seq
string lease_id
string source

# Empty selects the default chain; otherwise one robot profile chains[].id.
string chain_id

ContractVersion contract

# JOINT_VELOCITY | CARTESIAN_VELOCITY
string mode
float64[] joint_velocity_rad_s
geometry_msgs/Twist cartesian_velocity
bool deadman
