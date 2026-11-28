# Gripper position in the profile's unit: rad for a bus-servo gripper,
# metres for a parallel prismatic gripper. The adapter maps it to the vendor
# register range and URDF sign.
float64 position_rad

# rad | m. Empty means the runtime robot profile's gripper.unit.
string unit

float64 max_velocity_rad_s
float64 duration_s
bool verify_bus
