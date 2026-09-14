import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const projectDirectory = fileURLToPath(new URL('..', import.meta.url));
const syntheticSecret = 'synthetic-regression-token';

function readProjectFile(...segments) {
  return readFileSync(join(projectDirectory, ...segments), 'utf8');
}

test('keeps the Phase 7 local guide, demo and README aligned with the delivered CLI', () => {
  const readme = readProjectFile('README.md');
  const roadmap = readProjectFile('ROADMAP.md');
  const usage = readProjectFile('docs', 'USO_LOCAL.md');
  const demo = readProjectFile('assets', 'DEMO_15S.md');

  assert.equal(existsSync(join(projectDirectory, 'docs', 'USO_LOCAL.md')), true);
  assert.equal(existsSync(join(projectDirectory, 'assets', 'DEMO_15S.md')), true);

  assert.match(readme, /Fases 0 a 7 están completadas/u);
  assert.match(readme, /docs\/USO_LOCAL\.md/u);
  assert.match(readme, /assets\/DEMO_15S\.md/u);
  assert.match(roadmap, /Fase 7 — Guía de uso, demostración y entrega:.*completada/u);

  for (const document of [usage, demo]) {
    assert.match(document, /node \.\/dist\/cli\.js/u);
    assert.match(document, /valid-configuration\.env/u);
    assert.match(document, /valid-schema\.json/u);
    assert.equal(document.includes(syntheticSecret), false);
  }

  assert.match(usage, /npm ci/u);
  assert.match(usage, /npm test/u);
  assert.match(usage, /Código `5`/u);
  assert.match(demo, /invalid-configuration\.env/u);
  assert.match(demo, /código `5`/u);
});
