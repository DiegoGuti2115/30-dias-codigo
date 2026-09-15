import React from 'react';
import { usePomodoro, MODES_IN_SECONDS } from './hooks/usePomodoro';
import './index.css';

function App() {
  const { mode, isRunning, formattedTime, toggleTimer, resetTimer, changeMode, timeLeft } = usePomodoro();

  // Cálculo para el círculo de progreso SVG
  const RADIUS = 108;
  const CIRC = 2 * Math.PI * RADIUS;
  const totalSeconds = MODES_IN_SECONDS[mode];
  const progress = totalSeconds > 0 ? timeLeft / totalSeconds : 0;
  const strokeDashoffset = CIRC * (1 - progress);

  // Cálculo para la posición de la píldora selectora animada
  const thumbPositions = {
    work: 'translateX(0%)',
    shortBreak: 'translateX(104%)',
    longBreak: 'translateX(208%)'
  };

  return (
    <div className="stage" data-mode={mode}>
      {/* Orbes de fondo animadas */}
      <div className="orb orb-a"></div>
      <div className="orb orb-b"></div>
      <div className="orb orb-c"></div>

      <main className="panel">
        
        {/* Cabecera */}
        <div className="panel__head">
          <h1>Temporizador Pomodoro</h1>
          <p className="panel__sub">
            Parte de un reto de treinta proyectos diarios, pensado para bloques de foco profundo y descansos breves.
          </p>
        </div>

        {/* Selector de Modos (Píldoras) */}
        <div className="modes" role="tablist" aria-label="Modo del temporizador">
          <div 
            className="modes__thumb" 
            aria-hidden="true"
            style={{ transform: thumbPositions[mode] }}
          ></div>
          <button 
            onClick={() => changeMode('work')} 
            className={`mode-btn ${mode === 'work' ? 'is-active' : ''}`}
            role="tab"
            aria-selected={mode === 'work'}
          >
            Foco<span>90 min</span>
          </button>
          <button 
            onClick={() => changeMode('shortBreak')} 
            className={`mode-btn ${mode === 'shortBreak' ? 'is-active' : ''}`}
            role="tab"
            aria-selected={mode === 'shortBreak'}
          >
            Descanso corto<span>5 min</span>
          </button>
          <button 
            onClick={() => changeMode('longBreak')} 
            className={`mode-btn ${mode === 'longBreak' ? 'is-active' : ''}`}
            role="tab"
            aria-selected={mode === 'longBreak'}
          >
            Descanso largo<span>15 min</span>
          </button>
        </div>

        {/* Reloj SVG y Tiempo */}
        <div className="clock">
          <svg className="clock__ring" viewBox="0 0 240 240">
            <circle className="clock__track" cx="120" cy="120" r={RADIUS} />
            <circle 
              className="clock__progress" 
              cx="120" cy="120" r={RADIUS} 
              style={{ strokeDasharray: CIRC, strokeDashoffset: strokeDashoffset }}
            />
          </svg>
          <div className="clock__time">{formattedTime}</div>
          <div className="clock__state">
            {timeLeft === 0 ? 'Completado' : (isRunning ? 'En marcha' : 'En pausa')}
          </div>
        </div>

        {/* Controles Principales */}
        <div className="controls">
          <button 
            onClick={toggleTimer}
            className={`btn btn--primary ${isRunning ? 'is-running' : ''}`}
          >
            <span className="btn__icon">
              {isRunning ? (
                /* Icono de Pausa */
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>
              ) : (
                /* Icono de Play */
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
              )}
            </span>
            <span>{isRunning ? 'Pausar' : 'Iniciar'}</span>
          </button>
          
          <button 
            onClick={resetTimer}
            className="btn btn--ghost"
          >
            Reiniciar
          </button>
        </div>
        
      </main>
    </div>
  );
}

export default App;