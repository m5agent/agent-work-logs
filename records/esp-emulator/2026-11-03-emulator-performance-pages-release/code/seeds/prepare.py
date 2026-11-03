"""Copy frozen test sources and apply only a remote transport/provenance delta."""
import difflib,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2];OUT=pathlib.Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
parents={}
for name in ['emulator_performance_summary.mjs','public_qemu_worker_targets.mjs','public_qemu_performance.mjs','public_qemu_artifacts.mjs']:
 p=ROOT/'platform/tests'/name;b=p.read_bytes();(OUT/name).write_bytes(b);parents[name]={'path':str(p.relative_to(ROOT)),'sha256':sha(b),'copied_unchanged':True}
def replace(text,before,after):
 assert text.count(before)==1,before[:120]
 return text.replace(before,after)
base=(ROOT/'platform/tests/benchmark_emulator_firmware.mjs').read_text();s=base
s=replace(s,"import {createServer} from 'node:http';\n",'')
s=replace(s,"import {DEMO_FIRMWARE} from '../web/public-demo-firmware.js';","import {DEMO_FIRMWARE} from '../../platform/web/public-demo-firmware.js';\nimport {expectedRelease,prepareRemoteRelease,assertReleaseReceipt,adapterIdentity} from './pages_remote_release.mjs';")
s=replace(s,"const firmwareSource=process.env.M5_BENCH_SOURCE||'local';","const firmwareSource=process.env.M5_BENCH_SOURCE||'local';\nassert.equal(engine,'qemu','This ignored runner is the real HTTPS QEMU lane only');\nassert.equal(device,'stackchan');assert.equal(firmwareSource,'local');\nconst remoteExpected=expectedRelease(process.env,'M5_BENCH_URL');")
s=replace(s,"if(firmwareSource==='default-compose')assert.equal(firmwareSHA,DEMO_FIRMWARE.firmwareSHA256,'Default composition must keep the stock fixture identity');","if(firmwareSource==='default-compose')assert.equal(firmwareSHA,DEMO_FIRMWARE.firmwareSHA256,'Default composition must keep the stock fixture identity');\nassert.equal(firmwareSHA,'c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542');")
s=replace(s,"const report={schema_version:1", "assert.equal(candidateClock,null);assert.equal(profileMs,0);assert.equal(stopDiagnostic,null);\nassert.equal(process.env.M5_BENCH_READY_MARKER,undefined);\nassert.ok(requireRenderedMotion,'Real model rendering is required');\nassert.ok((sampleMs===20000&&runs===2&&!knownInput)||(sampleMs===8000&&runs===1&&knownInput),'Only the unchanged cold/repeated20s and independent8s input protocols are accepted');\nconst report={schema_version:1")
s=replace(s,"report.summary_algorithm_sha256=", "report.deployment='remote-static-host';report.adapter_identity=await adapterIdentity();\nreport.summary_algorithm_sha256=")
a=s.index('try{\n  let url;\n');b=s.index('  report.url=url;',a)
s=s[:a]+'''try{
  const remoteRelease=await prepareRemoteRelease({repo,out,expected:remoteExpected,testScript:'.work/pages-remote-tools/benchmark.mjs'});
  const url=remoteRelease.url;
  report.provenance={site_manifest_sha256:remoteRelease.provenance.site_manifest_sha256,base_path:remoteRelease.manifest.base_path,
    assets:remoteRelease.assets,executed_source_provenance:remoteRelease.provenance};
  report.runtime_manifest=remoteRelease.runtime;report.remote_release=remoteRelease.proof;
  report.configuration.site_publication_eligible=true;
''' +s[b:]
s=replace(s,"const row=await page.evaluate(()=>emulatorPerf.snapshot());row.run=i+1;", "const row=await page.evaluate(()=>emulatorPerf.snapshot());assertReleaseReceipt(row.receipt,remoteRelease);row.run=i+1;")
assert 'createServer' not in s and '.listen(' not in s
(OUT/'benchmark.mjs').write_text(s)
parents['benchmark.mjs']={'path':'platform/tests/benchmark_emulator_firmware.mjs','sha256':sha(base.encode()),'copied_unchanged':False}
(OUT/'benchmark-remote-only.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),s.splitlines(True),fromfile='platform/tests/benchmark_emulator_firmware.mjs',tofile='.work/pages-remote-tools/benchmark.mjs')))
# Keep the complete real guest/UI/input/texture/pause/CDP oracles unchanged.
base=(ROOT/'platform/tests/test_public_qemu_board_guest.mjs').read_text();s=base
s=replace(s,"import {createServer} from 'node:http';\n",'')
s=replace(s,"import {observeWorkerTargets} from './public_qemu_worker_targets.mjs';","import {observeWorkerTargets} from './public_qemu_worker_targets.mjs';\nimport {expectedRelease,prepareRemoteRelease,assertReleaseReceipt,adapterIdentity} from './pages_remote_release.mjs';")
s=replace(s,"const site = process.env.M5_PUBLIC_SITE && resolve(process.env.M5_PUBLIC_SITE);\nif (!site) { console.log('SKIP: explicit M5_PUBLIC_SITE candidate export required'); process.exit(0); }", "const site=null; // This ignored adapter never opens a local site or server.\nconst remoteExpected=expectedRelease(process.env,'M5_PUBLIC_URL');")
s=replace(s,"const hardwareGPU = process.env.M5_WASM_GPU === 'hardware';", "const hardwareGPU = process.env.M5_WASM_GPU === 'hardware';\nassert.equal(device,'stackchan');assert.equal(publicUI,true);assert.equal(hardwareGPU,true);assert.equal(clockDivisor,undefined);assert.equal(diagnostic,false);")
s=replace(s,"const epdOraclePath=", "report.deployment='remote-static-host';report.adapter_identity=await adapterIdentity();\nconst epdOraclePath=")
a=s.index("  report.provenance = await capturePublicQemuProvenance(");b=s.index('  browser = await chromium.launch(',a)
s=s[:a]+'''  const remoteRelease=await prepareRemoteRelease({repo,out:output,expected:remoteExpected,testScript:'.work/pages-remote-tools/board_guest.mjs'});
  report.provenance=remoteRelease.provenance;report.remote_release=remoteRelease.proof;
  const origin=remoteRelease.url;report.url=origin;
''' +s[b:]
s=replace(s,"  const first = await page.evaluate(() => boardRun.runtime.evidence());", "  const first = await page.evaluate(() => boardRun.runtime.evidence());assertReleaseReceipt(first.receipt,remoteRelease);")
assert 'createServer' not in s and '.listen(' not in s
(OUT/'board_guest.mjs').write_text(s)
parents['board_guest.mjs']={'path':'platform/tests/test_public_qemu_board_guest.mjs','sha256':sha(base.encode()),'copied_unchanged':False}
(OUT/'board-remote-only.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),s.splitlines(True),fromfile='platform/tests/test_public_qemu_board_guest.mjs',tofile='.work/pages-remote-tools/board_guest.mjs')))
identity={'kind':'ignored-HTTPS-test-adapter-source-identity',
 'artifact_provenance':'prepared-preview-export','runtime_origin':'fresh-full-source-build-public-path-policy-v1',
 'source_commit':'1b86ed6f7edcc36deafc4834b45a28c6a6017c79','parents':parents,'actual_files':{}}
for p in sorted(OUT.iterdir()):
 if p.is_file() and (p.suffix in ['.mjs','.py','.patch']):identity['actual_files'][p.name]={'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
(OUT/'adapter-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
print(json.dumps(identity,indent=2))
