# Progress feedback from the motion executor.
string intent_id

# VALIDATING | QUEUED | EXECUTING | SETTLING | VERIFYING
string phase
float32 progress

float64[] measured_positions
bool bus_verified
builtin_interfaces/Time stamp
