'use strict';

const test = require('node:test');
const assert = require('node:assert');

const { parseArgs, resolveTarget } = require('../lib/core.js');

test('parseArgs: bare target', () => {
  assert.deepStrictEqual(parseArgs(['my-project']), {
    target: 'my-project',
    upgrade: false,
    help: false,
  });
});

test('parseArgs: --upgrade sets the upgrade flag', () => {
  assert.strictEqual(parseArgs(['my-project', '--upgrade']).upgrade, true);
});

test('parseArgs: --help does not require a target', () => {
  const parsed = parseArgs(['--help']);
  assert.strictEqual(parsed.help, true);
  assert.strictEqual(parsed.target, null);
  assert.strictEqual(parsed.upgrade, false);
});

test('parseArgs: missing target throws, naming the argument', () => {
  assert.throws(() => parseArgs([]), /target/);
});

test('parseArgs: unknown option throws instead of being silently ignored', () => {
  assert.throws(() => parseArgs(['my-project', '--version']), /Unknown option/);
});

test('resolveTarget: absent path clones', () => {
  assert.deepStrictEqual(resolveTarget('x', false, false), { action: 'clone' });
});

test('resolveTarget: existing seja checkout is reused', () => {
  assert.deepStrictEqual(resolveTarget('x', true, true), { action: 'reuse' });
});

test('resolveTarget: existing non-seja path aborts with a reason', () => {
  const result = resolveTarget('x', true, false);
  assert.strictEqual(result.action, 'abort');
  assert.match(result.reason, /already exists/);
  assert.match(result.reason, /open-seja checkout/);
});
