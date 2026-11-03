# Bridge change summary

This is a redacted description of a locally deployed script, not a patch against an upstream Git commit. Host executable paths, runtime identity data and deployment configuration bodies are omitted.

- Base script SHA256: `6c46529e63de8e5af8fa98112f04aea828f32882a3605742620209d896e31ac6`; bytes: `16185`.
- Deployed script SHA256: `93351eb3166fcfa2921a4220b5488cecfa778214c153103c84ad4962bb5fb88c`; bytes: `16541`.
- Runtime configuration: model `gpt-6.1-sol`; provider `openai`; desktop bundled executable; recall mode `server`.
- Global Codex and plugin configuration unchanged.

The generic changes are:

```javascript
if (CFG.modelProvider) {
  args.splice(1, 0, '-c', `model_provider=${JSON.stringify(CFG.modelProvider)}`);
}

const codexEnv = { ...process.env, CODEX_INTERNAL_ORIGINATOR_OVERRIDE: 'WeComBot' };
if (CFG.codexPath) {
  codexEnv.PATH = path.dirname(CFG.codexPath) + path.delimiter + (codexEnv.PATH || '');
}
if (CFG.recallCompression) {
  codexEnv.OPENVIKING_RECALL_COMPRESS = CFG.recallCompression;
}
const child = spawn(CFG.codexPath || 'codex', args, {
  cwd: CFG.workspace,
  env: codexEnv,
  stdio: ['ignore', 'pipe', 'pipe'],
});
```

The provider override applies to new and resumed sessions. The explicit executable and its directory in child PATH make main model calls and hook child calls use the same bundled runtime. Recall mode is scoped to this bridge process.

Before deploying, preserve a script/configuration backup. Six legacy conversation mappings were separately backed up, existing conversation files preserved, and the active mapping atomically replaced with an empty object to start fresh GPT conversations. That migration avoids the observed incompatible legacy-history compaction; it does not repair that historical payload.
