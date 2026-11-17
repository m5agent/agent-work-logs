# Native STA fixture validation

Device Service now accepts an exact binary UDP request/reply fixture and an
explicit controlled HTTP peer for the generic native Wi-Fi profile. Both use the
existing lab-only or allowlist Linux namespace. The private worker binds the
UDP endpoint to its loopback. On allowlist jobs, only the configured UDP port
is implicitly authorized. The fixture records response counts and configured
payload hashes. An application assertion still checks the received payload.

## Native virtual-device validation

The same merged ESP-IDF v5.5.4 S3 probe ran on Cardputer and Cardputer ADV using
native binary `cbc0ea74c5763a9d989562b7061516fb3489fdc4056ddce4e016d555c1b86bb2`.
A bounded macOS workbench ran the actual guests with only three outbound
loopback fixture ports allowed. Both guests completed DHCP DORA and verified a
fixed HTTP body, an exact DNS A answer, NXDOMAIN for a second name, and a
binary UDP payload containing a NUL. The Ethernet capture included four
directional DNS flows and two directional UDP fixture flows for each guest.
The host UDP peer returned a different payload in the negative control. The
guest's comparison failed while both transport directions and the host's sent
count were still present. All three cases verified ZIP CRC before stopping and
released their lease, process and peer listeners.

The controller exercises the same guest network stack and QEMU NIC used by
Device Service. The local qualification invokes the same HTTP, DNS and UDP
peer classes in a bounded test topology. The production Linux namespace path
was unavailable on this host, and requesting it at the actual Device Service
was rejected before lease allocation. The negative controls for namespace
admission, packet delivery, and application mismatch remain distinct.

## Separate SoftAP control

The same native binary ran a distinct SDK probe configured as an open access
point on ADV. The guest logged startup and a listening HTTP socket. The
controller trace observed 144 AP beacons, one guest probe response and one
emulated authentication request reaching the guest RX DMA. The guest emitted
no authentication response and no application station-joined or assigned-IP
event. Ethernet capture had zero packets. The portal remained unverified.
The negative was taken through a dedicated native session with the same
capture and cleanup procedure. [Probe source](code/softap_probe.c)

## Reproduction

Build the fixed SDK probe for the native fixture recipe and create a dedicated
`qemu-wifi` session with the chosen board. Use the saved original source and
runtime digests where a byte-for-byte comparison is required and retain a ZIP
before stopping. Compare fixture response bytes to the guest's required marker
and compare packet directions to the finalized capture. For the AP control,
build the separate probe with the same 8 MiB SDK configuration, wait for the
portal-ready serial marker and check management-frame RX and TX separately.
Source, levels and guest build options are documented with the candidate
fixture. No resident process or Burner job was changed.

No browser, physical RF, or actual Linux namespace peer-positive result is
claimed. The controlled test evidence omits local endpoints, identifiers,
captured payload contents and runtime paths.
