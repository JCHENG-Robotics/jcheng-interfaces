# Runtime declaration published by a capability module at startup.
string schema_version
string name
string version
ContractVersion contract

# Allowed values: arm, gripper, base, full.
string[] scopes

# Must be false for capability modules. The privileged plane owns hardware access.
bool hardware_access

# Declared topics/services; the system validates them against a blacklist.
string[] publishes
string[] subscribes
string[] services

uint32 max_rate_hz
uint32 deadman_ms
