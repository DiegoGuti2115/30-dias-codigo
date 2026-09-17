import { useMemo, useState } from 'react'
import seedNotes from '../data/notes.json'
import { useNotes } from './hooks/useNotes'
import { normalizeTags, validateNoteDraft } from './utils/noteRules'
import { searchNotes } from './utils/noteSearch'
import type { Note, NoteDraft, NoteQuery, NoteSortField } from './utils/types'

type EditorState = { mode: 'new' } | { mode: 'edit'; noteId: string } | null

const initialQuery: NoteQuery = {
  text: '',
  tag: null,
  sortBy: 'updatedAt',
  sortDirection: 'desc',
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function createNoteId(): string {
  return globalThis.crypto?.randomUUID() ?? `note-${Date.now()}`
}

function App() {
  const { notes, persistence, error, addNote, editNote, removeNote } = useNotes(seedNotes)
  const [query, setQuery] = useState<NoteQuery>(initialQuery)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [editor, setEditor] = useState<EditorState>(null)
  const [draftError, setDraftError] = useState<string | null>(null)

  const results = useMemo(() => searchNotes(notes, query), [notes, query])
  const selectedNote = results.find((note) => note.id === selectedId) ?? results[0] ?? null
  const tags = useMemo(
    () => [...new Set(notes.flatMap((note) => note.tags))].sort((left, right) => left.localeCompare(right, 'es')),
    [notes],
  )

  function openNote(note: Note) {
    setSelectedId(note.id)
    setEditor(null)
    setDraftError(null)
  }

  function openNewNote() {
    setEditor({ mode: 'new' })
    setDraftError(null)
  }

  function openEditNote() {
    if (selectedNote) {
      setEditor({ mode: 'edit', noteId: selectedNote.id })
      setDraftError(null)
    }
  }

  async function saveNote(draft: NoteDraft) {
    const errors = validateNoteDraft(draft)
    if (errors.length > 0) {
      setDraftError(errors[0])
      return
    }

    const now = new Date().toISOString()
    const normalizedDraft = {
      title: draft.title.trim(),
      content: draft.content.trim(),
      tags: normalizeTags(draft.tags),
    }

    if (editor?.mode === 'edit') {
      const currentNote = notes.find((note) => note.id === editor.noteId)
      if (!currentNote) {
        return
      }
      await editNote({ ...currentNote, ...normalizedDraft, updatedAt: now })
      setSelectedId(editor.noteId)
    } else {
      const newNote: Note = {
        id: createNoteId(),
        ...normalizedDraft,
        createdAt: now,
        updatedAt: now,
      }
      await addNote(newNote)
      setSelectedId(newNote.id)
    }

    setEditor(null)
    setDraftError(null)
  }

  async function deleteSelectedNote() {
    if (!selectedNote || !window.confirm(`¿Eliminar "${selectedNote.title}"?`)) {
      return
    }

    await removeNote(selectedNote.id)
    const nextNotes = notes.filter((note) => note.id !== selectedNote.id)
    setSelectedId(nextNotes[0]?.id ?? null)
    setEditor(null)
  }

  const editorNote = editor?.mode === 'edit'
    ? notes.find((note) => note.id === editor.noteId) ?? null
    : null

  if (persistence === 'loading') {
    return <main className="app-shell"><div className="loading-state"><span className="brand-mark">N</span><p>Cargando tus notas...</p></div></main>
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Inicio de Buscador de notas">
          <span className="brand-mark">N</span>
          <span>notario</span>
        </a>
        <div className="topbar-meta">
          <span className={`offline-dot ${persistence === 'memory' ? 'is-memory' : ''}`} aria-hidden="true" />
          <span>{persistence === 'memory' ? 'Modo memoria' : 'Guardado local'}</span>
        </div>
      </header>

      {error && <div className="storage-notice" role="status">{error}</div>}

      <section className="workspace" aria-labelledby="page-title">
        <div className="intro-row">
          <div>
            <p className="eyebrow">Biblioteca personal / 18</p>
            <h1 id="page-title">Tus notas,<br /><em>encontradas.</em></h1>
          </div>
          <button className="primary-button" type="button" onClick={openNewNote}>
            <span aria-hidden="true">+</span> Nueva nota
          </button>
        </div>

        <div className="search-row">
          <label className="search-box">
            <span className="search-icon" aria-hidden="true">⌕</span>
            <span className="sr-only">Buscar notas</span>
            <input
              type="search"
              value={query.text}
              onChange={(event) => setQuery((current) => ({ ...current, text: event.target.value }))}
              placeholder="Busca por título, contenido o etiqueta..."
            />
            {query.text && <button type="button" className="clear-search" onClick={() => setQuery((current) => ({ ...current, text: '' }))} aria-label="Limpiar búsqueda">×</button>}
          </label>
          <label className="select-wrap">
            <span className="sr-only">Filtrar por etiqueta</span>
            <select
              value={query.tag ?? ''}
              onChange={(event) => setQuery((current) => ({ ...current, tag: event.target.value || null }))}
            >
              <option value="">Todas las etiquetas</option>
              {tags.map((tag) => <option key={tag} value={tag}>#{tag}</option>)}
            </select>
          </label>
          <label className="select-wrap sort-select">
            <span className="sr-only">Ordenar notas</span>
            <select
              value={`${query.sortBy}-${query.sortDirection}`}
              onChange={(event) => {
                const [sortBy, sortDirection] = event.target.value.split('-') as [NoteSortField, NoteQuery['sortDirection']]
                setQuery((current) => ({ ...current, sortBy, sortDirection }))
              }}
            >
              <option value="updatedAt-desc">Más recientes</option>
              <option value="updatedAt-asc">Más antiguas</option>
              <option value="title-asc">Título A-Z</option>
              <option value="title-desc">Título Z-A</option>
            </select>
          </label>
        </div>

        <div className="content-grid">
          <section className="notes-column" aria-labelledby="results-title">
            <div className="section-heading">
              <div>
                <h2 id="results-title">Todas tus notas</h2>
                <p aria-live="polite">{results.length} {results.length === 1 ? 'resultado' : 'resultados'}</p>
              </div>
              <span className="result-count">{String(results.length).padStart(2, '0')}</span>
            </div>

            {results.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon" aria-hidden="true">⌁</span>
                <h3>No encontramos esa nota</h3>
                <p>Prueba con otra palabra o limpia los filtros de búsqueda.</p>
                <button type="button" className="text-button" onClick={() => setQuery(initialQuery)}>Limpiar filtros</button>
              </div>
            ) : (
              <div className="note-list">
                {results.map((note) => (
                  <button
                    className={`note-card ${selectedNote?.id === note.id ? 'is-selected' : ''}`}
                    type="button"
                    key={note.id}
                    onClick={() => openNote(note)}
                  >
                    <span className="note-card-top">
                      <span className="note-date">{formatDate(note.updatedAt)}</span>
                      <span className="arrow" aria-hidden="true">↗</span>
                    </span>
                    <strong>{note.title}</strong>
                    <span className="note-excerpt">{note.content}</span>
                    <span className="tag-row">{note.tags.map((tag) => <span className="tag" key={tag}>#{tag}</span>)}</span>
                  </button>
                ))}
              </div>
            )}
          </section>

          <aside className="detail-panel" aria-label="Detalle de la nota seleccionada">
            {editor ? (
              <NoteEditor
                note={editorNote}
                error={draftError}
                onCancel={() => setEditor(null)}
                onSave={saveNote}
              />
            ) : selectedNote ? (
              <article className="note-detail">
                <div className="detail-kicker"><span className="detail-line" /> NOTA SELECCIONADA</div>
                <h2>{selectedNote.title}</h2>
                <div className="detail-meta">
                  <span>Actualizada {formatDate(selectedNote.updatedAt)}</span>
                  <span className="detail-id">{selectedNote.id}</span>
                </div>
                <div className="detail-body">{selectedNote.content.split('\n').map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
                <div className="detail-tags">{selectedNote.tags.map((tag) => <span className="tag tag-filled" key={tag}>#{tag}</span>)}</div>
                <div className="detail-actions">
                  <button className="secondary-button" type="button" onClick={openEditNote}>Editar nota</button>
                  <button className="delete-button" type="button" onClick={deleteSelectedNote}>Eliminar</button>
                </div>
              </article>
            ) : (
              <div className="detail-placeholder">
                <span className="placeholder-mark" aria-hidden="true">N</span>
                <p>Selecciona una nota<br />para verla aquí.</p>
              </div>
            )}
          </aside>
        </div>
      </section>
    </main>
  )
}

type NoteEditorProps = {
  note: Note | null
  error: string | null
  onCancel: () => void
  onSave: (draft: NoteDraft) => void
}

function NoteEditor({ note, error, onCancel, onSave }: NoteEditorProps) {
  const [title, setTitle] = useState(note?.title ?? '')
  const [content, setContent] = useState(note?.content ?? '')
  const [tags, setTags] = useState(note?.tags.join(', ') ?? '')

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSave({ title, content, tags: tags.split(',') })
  }

  return (
    <form className="editor-form" onSubmit={submit}>
      <div className="detail-kicker"><span className="detail-line" /> {note ? 'EDITAR NOTA' : 'NUEVA NOTA'}</div>
      <div className="editor-heading">
        <h2>{note ? 'Dale otra forma.' : 'Una idea nueva.'}</h2>
        <button className="close-button" type="button" onClick={onCancel} aria-label="Cancelar edición">×</button>
      </div>
      <label>Título<input autoFocus value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Un título claro" /></label>
      <label>Contenido<textarea value={content} onChange={(event) => setContent(event.target.value)} placeholder="Escribe lo que quieras recordar..." rows={8} /></label>
      <label>Etiquetas <span className="field-hint">separadas por comas</span><input value={tags} onChange={(event) => setTags(event.target.value)} placeholder="proyecto, idea" /></label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="editor-actions">
        <button className="secondary-button" type="button" onClick={onCancel}>Cancelar</button>
        <button className="primary-button" type="submit">Guardar nota</button>
      </div>
    </form>
  )
}

export default App