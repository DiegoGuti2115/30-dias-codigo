import assert from 'node:assert/strict';
import test from 'node:test';

// Simulamos la importación de la función para el test
function formatTime(seconds) {
  if (seconds < 0) return '00:00';
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

test('Formatea correctamente los segundos a MM:SS', () => {
  assert.equal(formatTime(5400), '90:00'); // 90 minutos de foco
  assert.equal(formatTime(300), '05:00');  // 5 minutos de descanso
  assert.equal(formatTime(45), '00:45');   // Menos de 1 minuto
  assert.equal(formatTime(0), '00:00');    // Cero
  assert.equal(formatTime(-10), '00:00');  // Casos negativos controlados
});