# Structured motion intent. This is not a servo/register command.
std_msgs/Header header

string intent_id
string idempotency_key
string lease_id
string source

# JOINT_TRAJECTORY | JOINT_STEP | POSE | HOME | BASE_PULSE | GRIPPER
string kind

# moveit | step | pose | fast | base | gripper
string profile

ContractVersion contract

# kind=JOINT_TRAJECTORY
JointTrajectory trajectory

# kind=JOINT_STEP | HOME
string[] joint_names
float64[] target_positions
float64 max_velocity_rad_s
float64 max_acceleration_rad_s2
float64 duration_s

# kind=POSE
geometry_msgs/Pose target_pose
string tip_link
string frame_id

# kind=BASE_PULSE
BasePulse base_pulse

# kind=GRIPPER
GripperCommand gripper

# Execution and verification requirements.
bool verify_bus
bool require_measured_state
string expected_profile_hash
