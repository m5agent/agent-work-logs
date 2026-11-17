import os
import M5

M5.begin()
root = "/flash" if "flash" in os.listdir("/") else ""
seed_path = root + "/fixture/seed.txt"
with open(seed_path, "rb") as seed:
    body = seed.read()
if body != b"fixture-from-session-overlay\n":
    raise RuntimeError("fixture contents differ")
assert "seed.txt" in os.listdir(root + "/fixture")
witness = root + "/fixture/witness.txt"
if "witness.txt" in os.listdir(root + "/fixture"):
    with open(witness, "rb") as file:
        assert file.read() == b"guest-persisted\n"
    print("M5_FS_REBOOT_READBACK")
else:
    with open(witness, "wb") as file:
        assert file.write(b"guest-persisted\n") == 16
    os.sync()
    with open(witness, "rb") as file:
        assert file.read() == b"guest-persisted\n"
    print("M5_FS_PRESEED_AND_WRITE")
