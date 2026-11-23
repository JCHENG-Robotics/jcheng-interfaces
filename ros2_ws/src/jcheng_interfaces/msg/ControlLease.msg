# Exclusive control lease for one or more scopes.
string lease_id
string holder

# arm | gripper | base | full
string scope

# exclusive
string mode

# 100 operator, 60 application, 40 teleop, 20 learning, 10 diagnostics.
uint8 priority
bool deadman_required

builtin_interfaces/Time issued_at
builtin_interfaces/Time expires_at
ContractVersion contract
