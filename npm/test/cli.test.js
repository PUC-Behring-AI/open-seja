'use strict';

const test = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const { run } = require('../bin/cli.js');
const { REPO_URL } = require('../lib/core.js');

const CLI_PATH = path.join(__dirname, '..', 'bin', 'cli.js');

/**
 * Build injectable deps with recording stubs, so no test touches real
 * `git`, `claude`, or the filesystem.
 */
function makeDeps({ targetExists = false, hasSejaVersion = false, claudeAvailable = true } = {}) {
  const calls = { clone: [], launchClaude: [], exit: [], error: [], log: [] };
  const deps = {
    fs: {
      existsSync: (p) => (p.endsWith('.seja-version') ? hasSejaVersion : targetExists),
    },
    bootstrap: {
      clone: (...args) => calls.clone.push(args),
      checkClaudeAvailable: () => claudeAvailable,
      launchClaude: (...args) => calls.launchClaude.push(args),
    },
    exit: (code) => calls.exit.push(code),
    error: (msg) => calls.error.push(msg),
    log: (msg) => calls.log.push(msg),
  };
  return { deps, calls };
}

test('--help prints usage and exits 0 without invoking git or claude', () => {
  const stdout = execFileSync(process.execPath, [CLI_PATH, '--help'], { encoding: 'utf8' });
  assert.match(stdout, /Usage:/);
  assert.match(stdout, /npx open-seja <target>/);
});

test('missing target exits non-zero with a clear error', () => {
  assert.throws(
    () => execFileSync(process.execPath, [CLI_PATH], { encoding: 'utf8', stdio: 'pipe' }),
    (err) => {
      assert.notStrictEqual(err.status, 0);
      assert.match(err.stderr, /target/);
      return true;
    }
  );
});

test('abort: existing non-seja target exits non-zero, reason on stderr, no bootstrap', () => {
  const { deps, calls } = makeDeps({ targetExists: true, hasSejaVersion: false });
  run(['existing-dir'], deps);

  assert.deepStrictEqual(calls.exit, [1]);
  assert.strictEqual(calls.error.length, 1);
  assert.match(calls.error[0], /already exists/);
  assert.deepStrictEqual(calls.clone, []);
  assert.deepStrictEqual(calls.launchClaude, []);
});

test('clone: absent target clones then hands off with /seja-setup', () => {
  const { deps, calls } = makeDeps({ targetExists: false });
  run(['my-project'], deps);

  assert.deepStrictEqual(calls.clone, [[REPO_URL, 'my-project']]);
  assert.deepStrictEqual(calls.launchClaude, [['my-project', '/seja-setup']]);
  assert.deepStrictEqual(calls.exit, []);
});

test('reuse + --upgrade: existing checkout is not re-cloned, upgrade prompt is used', () => {
  const { deps, calls } = makeDeps({ targetExists: true, hasSejaVersion: true });
  run(['my-project', '--upgrade'], deps);

  assert.deepStrictEqual(calls.clone, []);
  assert.deepStrictEqual(calls.launchClaude, [['my-project', '/seja-setup --upgrade']]);
});

test('claude unavailable: exits non-zero before handing off', () => {
  const { deps, calls } = makeDeps({ targetExists: false, claudeAvailable: false });
  run(['my-project'], deps);

  assert.deepStrictEqual(calls.exit, [1]);
  assert.match(calls.error[0], /claude/i);
  assert.deepStrictEqual(calls.launchClaude, []);
});

test('clone failure: exits non-zero with context, never hands off', () => {
  const { deps, calls } = makeDeps({ targetExists: false });
  deps.bootstrap.clone = () => {
    throw new Error('git exited with 128');
  };
  run(['my-project'], deps);

  assert.deepStrictEqual(calls.exit, [1]);
  assert.match(calls.error[0], /Failed to clone/);
  assert.deepStrictEqual(calls.launchClaude, []);
});
