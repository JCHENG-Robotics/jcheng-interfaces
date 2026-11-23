# Structured safety validation report. The report is diagnostic; the
# authoritative decision is approved/reason_code on the response.
uint16 schema_version
bool approved
string reason_code
string[] check_ids
string[] violations
float64 duration_s
uint32 point_count
bool workspace_checked
bool table_checked
float64 max_velocity_rad_s
float64 max_acceleration_rad_s2
builtin_interfaces/Time checked_at
