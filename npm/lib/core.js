'use strict';

/**
 * Pure decision logic for the `open-seja` installer wrapper.
 *
 * Nothing in this module touches the filesystem, the network, or child
 * processes: every environment signal arrives as an argument. That keeps the
 * wrapper's decisions unit-testable without mocking the process boundary --
 * the I/O itself lives in `lib/bootstrap.js`.
 */

const REPO_URL = 'https://github.com/PUC-Behring-AI/open-seja';

const USAGE = `open-seja -- install or upgrade the open-seja Claude Code harness

Usage:
  npx open-seja <target>             Clone the harness into <target> and run /seja-setup
  npx open-seja <target> --upgrade   Reuse an existing checkout and run /seja-setup --upgrade
  npx open-seja --help               Show this message

Requirements: git, and the \`claude\` CLI installed and authenticated.

The wrapper only bootstraps: it clones (or recognises) the checkout and hands
the terminal over to an interactive Claude Code session. The setup questionnaire
and scaffolding run inside that session, not here.`;

/**
 * Parse command-line arguments (argv without the node/script prefix).
 *
 * @param {string[]} argv
 * @returns {{target: string|null, upgrade: boolean, help: boolean}}
 * @throws {Error} when the required positional `target` is missing or an
 *   unrecognised flag is passed -- a silently ignored flag would let the user
 *   believe it took effect.
 */
function parseArgs(argv) {
  let target = null;
  let upgrade = false;
  let help = false;

  for (const arg of argv) {
    if (arg === '--help' || arg === '-h') {
      help = true;
    } else if (arg === '--upgrade') {
      upgrade = true;
    } else if (arg.startsWith('-')) {
      throw new Error(`Unknown option: ${arg}\n\n${USAGE}`);
    } else if (target === null) {
      target = arg;
    } else {
      throw new Error(`Unexpected extra argument: ${arg}\n\n${USAGE}`);
    }
  }

  if (!help && target === null) {
    throw new Error(`Missing required argument: target (the directory to install the harness into)\n\n${USAGE}`);
  }

  return { target, upgrade, help };
}

/**
 * Decide what to do with the target path, given signals resolved by the caller.
 *
 * @param {string} target Path the user asked for.
 * @param {boolean} targetExists Whether that path already exists on disk.
 * @param {boolean} hasSejaVersion Whether it contains a `.seja-version` file.
 * @returns {{action: 'clone'|'reuse'|'abort', reason?: string}}
 */
function resolveTarget(target, targetExists, hasSejaVersion) {
  if (!targetExists) {
    return { action: 'clone' };
  }
  if (hasSejaVersion) {
    return { action: 'reuse' };
  }
  return {
    action: 'abort',
    reason: `Path "${target}" already exists but does not look like an open-seja checkout (no .seja-version file). Remove it, or pick a different target.`,
  };
}

module.exports = { REPO_URL, USAGE, parseArgs, resolveTarget };
