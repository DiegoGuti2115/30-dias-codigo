import { useState } from 'react'
import { Board } from './components/Board'
import { TaskForm } from './components/TaskForm'
import { useBoard } from './hooks/useBoard'
import type { Card, CardDraft, ColumnId } from './utils/types'

export function App() {
  const { board, error, pendingDeletion, storageMode, storageNotice, actions } = useBoard()
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingCard, setEditingCard] = useState<Card | null>(null)
  const [formColumn, setFormColumn] = useState<ColumnId>('todo')
  const pendingCard = board.cards.find((card) => card.id === pendingDeletion)

  function openCreateForm(columnId: ColumnId) {
    setFormColumn(columnId)
    setEditingCard(null)
    setIsFormOpen(true)
  }

  function openEditForm(card: Card) {
    setEditingCard(card)
    setFormColumn(card.columnId)
    setIsFormOpen(true)
  }

  function closeForm() {
    setIsFormOpen(false)
    setEditingCard(null)
  }

  function handleSubmit(draft: CardDraft) {
    if (editingCard) {
      actions.updateCard(editingCard.id, draft)
    } else {
      actions.addCard(draft, formColumn)
    }
    closeForm()
  }

  function handleDelete(cardId: string) {
    actions.requestDelete(cardId)
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">K</span>
          <span className="brand-name">KANBAN / 19</span>
        </div>
        <div className="header-meta">
          <span className="status-pulse" aria-hidden="true" />
          <span>{storageMode === 'indexeddb' ? 'Guardado en este navegador' : storageMode === 'memory' ? 'Modo memoria' : 'Cargando tablero'}</span>
        </div>
      </header>

      <section className="hero" aria-labelledby="page-title">
        <div>
          <span className="eyebrow">Tablero personal · Septiembre 2026</span>
          <h1 id="page-title">Haz visible<br /><em>el siguiente paso.</em></h1>
          <p className="hero-copy">Un espacio tranquilo para mover el trabajo desde la intención hasta lo terminado.</p>
        </div>
        <div className="hero-stats" aria-label="Resumen del tablero">
          <div><strong>{board.cards.length}</strong><span>tareas totales</span></div>
          <div><strong>{board.cards.filter((card) => card.columnId === 'done').length}</strong><span>completadas</span></div>
        </div>
      </section>

      {error && <div className="notice notice-error" role="alert"><span>{error}</span><button type="button" onClick={actions.clearError} aria-label="Cerrar aviso">×</button></div>}
      {storageNotice && <div className="notice notice-storage" role="status"><span>{storageNotice}</span></div>}

      <section className="board-section" aria-label="Tablero Kanban">
        <div className="board-toolbar">
          <div><span className="eyebrow">Flujo de trabajo</span><p>Actualizado ahora</p></div>
          <button className="button button-primary" type="button" onClick={() => openCreateForm('todo')}><span aria-hidden="true">+</span> Nueva tarea</button>
        </div>
        <Board board={board} onAdd={openCreateForm} onEdit={openEditForm} onDelete={handleDelete} onMove={actions.moveCard} />
      </section>

      <footer className="app-footer"><span>DAY 19 / 30</span><span>Offline by design</span></footer>

      {isFormOpen && (
        <div className="modal-backdrop" role="presentation">
          <div className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="form-title" onKeyDown={(event) => event.key === 'Escape' && closeForm()}>
            <TaskForm initialDraft={editingCard ?? undefined} isEditing={Boolean(editingCard)} onSubmit={handleSubmit} onCancel={closeForm} />
          </div>
        </div>
      )}

      {pendingCard && (
        <div className="modal-backdrop" role="presentation">
          <div className="confirm-panel" role="alertdialog" aria-modal="true" aria-labelledby="delete-title" aria-describedby="delete-description" onKeyDown={(event) => event.key === 'Escape' && actions.cancelDelete()}>
            <span className="confirm-kicker">Eliminar tarjeta</span>
            <h2 id="delete-title">¿Retirar “{pendingCard.title}”?</h2>
            <p id="delete-description">Esta acción quitará la tarjeta del tablero y no se puede deshacer.</p>
            <div className="form-actions"><button className="button button-quiet" type="button" onClick={actions.cancelDelete}>Cancelar</button><button className="button button-danger" type="button" onClick={actions.confirmDelete}>Eliminar tarjeta</button></div>
          </div>
        </div>
      )}
    </main>
  )
}
