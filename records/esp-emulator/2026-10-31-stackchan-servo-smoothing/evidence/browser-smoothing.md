# Browser smoothing evidence

```text
firmware SHA256: c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542
WASM SHA256:     5d6c36bdafc1129c2652b5ba9422f3deb5ab170475748cea96fdc4cf9520a993
GPU backend:     ANGLE Metal

run 1:
  result: PASS
  checks: 12/12
  raw states: 23
  frames: 615
  SCS packets: 30
  intermediate 3D poses in 2 s: 15
  max single visual step: 9.0253 degrees

run 2:
  result: PASS
  checks: 12/12
  raw states: 23
  frames: 546
  SCS packets: 30
  intermediate 3D poses in 2 s: 14
  max single visual step: 9.3412 degrees
```

Both runs preserved raw yaw `307..613`, pitch `677..850`, DOM ticks, packet
counts and angle-label values.
