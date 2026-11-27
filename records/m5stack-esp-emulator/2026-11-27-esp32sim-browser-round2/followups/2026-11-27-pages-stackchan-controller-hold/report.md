# StackChan browser publication gate

The serial hosted gate failed the zone 2 guest-down marker even though the same QEMU VM confirmed Si12T mask 12 and release mask 0. The recorded interval between controller reads was 238 ms. The previous timer started at browser input dispatch while the controller write was still asynchronous.

The updated probe starts the same fixed 250 ms timer after the confirmed down mask. It verifies controller timestamps, both guest levels in each of the three zones, the real model events, and normal Worker teardown. The probe keeps its existing one-attempt keyboard and pointer sequence and fails when the original guest driver misses an edge. This is a test scheduling correction. The fixed guest and QEMU engine are identical.

Two isolated Chrome replays passed 41/41 assertions each. Measured controller intervals were 274–299 ms. Both ended with zero live Workers. The first failed hosted receipt is retained separately.

The official retry pins the exact Xtensa and C61 artifacts from the original run's successful source jobs. Existing importer checks still bind producer metadata, artifact hashes, runtime assets and unchanged source inputs. A subsequent full hosted guest gate remains the requirement for deployment.
