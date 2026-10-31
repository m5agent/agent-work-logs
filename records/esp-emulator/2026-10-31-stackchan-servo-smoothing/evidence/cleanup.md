# Worker cleanup evidence

The owner first terminates the engine Worker handle on acknowledgement and again
in a fresh task. The runtime waits 250 ms after close acknowledgement before
removing the iframe.

```text
StackChan run 1: PASS
  minimum observed targets: 6
  live before context close: 0

StackChan run 2: PASS
  minimum observed targets: 6
  live before context close: 0

public CoreS3 acceptance: PASS
  first instance: engine + 5 pthread targets closed before iframe finalization
  reopened instance: 12 total targets closed before context close
```

The target lifetime source is Chrome DevTools `Target.getTargets`, not a forced
browser-context teardown.
