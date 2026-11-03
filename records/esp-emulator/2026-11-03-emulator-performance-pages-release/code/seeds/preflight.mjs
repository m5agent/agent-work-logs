// Explicit remote artifact validation only; never creates a browser or guest.
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {expectedRelease,prepareRemoteRelease,adapterIdentity} from './pages_remote_release.mjs';
const repo=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
assert.ok(process.env.M5_PAGES_PREFLIGHT_OUT,'A fresh ignored preflight output is required');
const out=resolve(process.env.M5_PAGES_PREFLIGHT_OUT);assert.ok(out.startsWith(repo+'/.work/'));await mkdir(out,{recursive:false});
const expected=expectedRelease(process.env,'M5_PUBLIC_URL'),identity=await adapterIdentity();
const release=await prepareRemoteRelease({repo,out,expected,testScript:'.work/pages-remote-tools/preflight.mjs'});
await writeFile(resolve(out,'report.json'),JSON.stringify({result:'PASS',scope:'remote artifact/source validation only',guest_execution:'NOT RUN',adapter_identity:identity,proof:release.proof},null,2)+'\n');
console.log('Remote artifact/source preflight PASS; guest validation NOT RUN');
