#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const { REPO_URL, USAGE, parseArgs, resolveTarget } = require('../lib/core.js');
const bootstrap = require('../lib/bootstrap.js');

const CLAUDE_MISSING_MESSAGE =
  'The `claude` CLI was not found on your PATH.\n' +
  'Install it (see https://claude.com/claude-code), authenticate, then re-run this command.';

const DEFAULT_DEPS = {
  parseArgs,
  resolveTarget,
  bootstrap,
  fs,
  exit: process.exit,
  log: console.log,
  error: console.error,
};

/**
 * Dispatch one wrapper invocation: parse, decide, bootstrap, hand off.
 *
 * Dependencies are injectable so the abort / clone / claude-unavailable
 * branches can be asserted without touching real `git` or `claude`.
 *
 * @param {string[]} argv argv without the node/script prefix.
 * @param {object} [deps]
 * @returns {void}
 */
function run(argv, deps = {}) {
  const d = { ...DEFAULT_DEPS, ...deps };

  let parsed;
  try {
    parsed = d.parseArgs(argv);
  } catch (err) {
    d.error(err.message);
    return d.exit(1);
  }

  if (parsed.help) {
    d.log(USAGE);
    return d.exit(0);
  }

  const targetExists = d.fs.existsSync(parsed.target);
  const hasSejaVersion =
    targetExists && d.fs.existsSync(path.join(parsed.target, '.seja-version'));
  const decision = d.resolveTarget(parsed.target, targetExists, hasSejaVersion);

  if (decision.action === 'abort') {
    d.error(decision.reason);
    return d.exit(1);
  }

  if (decision.action === 'clone') {
    try {
      d.bootstrap.clone(REPO_URL, parsed.target);
    } catch (err) {
      // git has already printed its own diagnostics to stderr; add the context
      // it cannot know (which repo, which target) instead of a Node stack trace.
      d.error(
        `Failed to clone ${REPO_URL} into "${parsed.target}".\n` +
          'Check that git is installed, the path is writable, and you can reach the repository.'
      );
      return d.exit(1);
    }
  }

  // Checked after the clone so a fresh checkout is not thrown away, but before
  // the handoff -- launching a missing binary would fail with a bare ENOENT.
  if (!d.bootstrap.checkClaudeAvailable()) {
    d.error(CLAUDE_MISSING_MESSAGE);
    return d.exit(1);
  }

  d.bootstrap.launchClaude(
    parsed.target,
    parsed.upgrade ? '/seja-setup --upgrade' : '/seja-setup'
  );
}

if (require.main === module) {
  run(process.argv.slice(2));
}

module.exports = { run, CLAUDE_MISSING_MESSAGE };
