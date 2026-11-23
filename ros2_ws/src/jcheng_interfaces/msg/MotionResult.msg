# Terminal motion result.
string intent_id

# COMPLETED | REJECTED | ABORTED | TIMEOUT | UNKNOWN
string outcome
string reason_code
string message

SafetyState safety
float64[] measured_positions
bool bus_verified
bool calibration_invalidated
builtin_interfaces/Time completed_at
string evidence_id
