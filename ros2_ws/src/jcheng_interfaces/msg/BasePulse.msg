# Open-loop base pulse. duty is normalized to [-1.0, 1.0]; the hardware adapter
# maps it to the vendor raw duty scale. Any base motion invalidates table calibration.
float64[] duty
float64 duration_s
bool require_stopped_after
