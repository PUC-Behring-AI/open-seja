'use strict';

/**
 * I/O boundary for the `open-seja` installer wrapper.
 *
 * Every child-process call lives here; no decisions are made in this module
 * (those belong to `lib/core.js`). Nothing here is unit-tested -- the surface
 * is entirely `git`/`claude` invocation, verified manually.
 */

const { execFileSync, spawnSync } = require('node:child_process');

const IS_WINDOWS = process.platform === 'win32';

/**
 * Invoke the `claude` CLI.
 *
 * On Windows an `npm install -g` CLI is a `claude.cmd` shim. Node resolves
 * executables through CreateProcess, which -- unlike cmd.exe -- does not apply
 * PATHEXT, so spawning `claude` without a shell fails with ENOENT even when it
 * is correctly installed and on PATH; and since the CVE-2024-27980 fix Node
 * refuses to spawn a `.cmd` directly at all. A shell is therefore the only way
 * in on Windows. The command is passed as a single pre-composed string rather
 * than as a shell + args array, because the latter is deprecated as of Node 22
 * (DEP0190) for concatenating unescaped arguments. Both forms are safe here for
 * the same reason: every argument below is a fixed literal. `clone()` -- the one
 * call carrying user-controlled input -- never touches a shell.
 *
 * @param {string[]} args Fixed literal arguments. Never user input.
 * @param {object} options Extra spawnSync options (cwd, stdio).
 * @returns {import('node:child_process').SpawnSyncReturns<Buffer>}
 */
function runClaude(args, options) {
  if (IS_WINDOWS) {
    const command = ['claude', ...args.map((arg) => `"${arg}"`)].join(' ');
    return spawnSync(command, { ...options, shell: true });
  }
  return spawnSync('claude', args, options);
}

/**
 * Clone the harness repository into `target`.
 *
 * @param {string} repoUrl
 * @param {string} target User-supplied path -- never passed through a shell.
 * @returns {void}
 */
function clone(repoUrl, target) {
  execFileSync('git', ['clone', repoUrl, target], { stdio: 'inherit' });
}

/**
 * Report whether the `claude` CLI is callable. Does not throw when it is
 * missing -- the caller decides how to surface that.
 *
 * @returns {boolean}
 */
function checkClaudeAvailable() {
  const result = runClaude(['--version'], { stdio: 'ignore' });
  return result.error === undefined && result.status === 0;
}

/**
 * Hand the terminal over to an interactive Claude Code session seeded with
 * `initialPrompt`. `stdio: 'inherit'` keeps the handoff transparent -- the
 * wrapper does no buffering in between.
 *
 * @param {string} cwd
 * @param {string} initialPrompt
 * @returns {void}
 */
function launchClaude(cwd, initialPrompt) {
  runClaude([initialPrompt], { cwd, stdio: 'inherit' });
}

module.exports = { clone, checkClaudeAvailable, launchClaude };
