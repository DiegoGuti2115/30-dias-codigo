// src/hooks/useRequestComposer.ts
'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

import { executeRequest } from '../lib/client'
import { appendHistoryEntry, readHistory, writeHistory } from '../lib/history'
import { getDraftErrors, type DraftErrors } from '../lib/request-draft'
import { apiRequestDraftSchema } from '../lib/schema'
import type {
  ApiExecutionResult,
  ApiRequestDraft,
  BodyFormat,
  HttpMethod,
  KeyValuePair,
  RequestHistoryEntry,
} from '../lib/types'
import { useRequestExamples } from './useRequestExamples'

type PairSection = 'query' | 'headers'

const createPair = (): KeyValuePair => ({ key: '', value: '', enabled: true })

export const useRequestComposer = () => {
  const { examples: requestExamples, isLoading: examplesLoading, isError: examplesError, reload: reloadExamples } = useRequestExamples()

  const [draft, setDraft] = useState<ApiRequestDraft>(() =>
    apiRequestDraftSchema.parse(requestExamples[0]),
  )
  const [errors, setErrors] = useState<DraftErrors>({})
  const [isSending, setIsSending] = useState(false)
  const [result, setResult] = useState<ApiExecutionResult | null>(null)
  const [history, setHistory] = useState<RequestHistoryEntry[]>([])
  const controllerRef = useRef<AbortController | null>(null)

  // Cuando los ejemplos carguen desde SWR, actualizar el draft inicial
  // solo si el usuario no ha modificado nada aún
  const initializedRef = useRef(false)
  useEffect(() => {
    if (!examplesLoading && requestExamples.length > 0 && !initializedRef.current) {
      initializedRef.current = true
      setDraft(structuredClone(requestExamples[0]))
    }
  }, [examplesLoading, requestExamples])

  useEffect(() => {
    setHistory(readHistory(window.localStorage))
  }, [])

  const persistHistory = useCallback((entries: RequestHistoryEntry[]) => {
    setHistory(entries)
    writeHistory(window.localStorage, entries)
  }, [])

  const setMethod = useCallback((method: HttpMethod) => {
    setDraft((current) =>
      method === 'GET'
        ? { ...current, method, bodyFormat: 'none', body: '' }
        : { ...current, method },
    )
    setErrors({})
  }, [])

  const setUrl = useCallback((url: string) => {
    setDraft((current) => ({ ...current, url }))
    setErrors((current) => ({ ...current, url: '' }))
  }, [])

  const setBody = useCallback((body: string) => {
    setDraft((current) => ({ ...current, body }))
    setErrors((current) => ({ ...current, body: '' }))
  }, [])

  const setBodyFormat = useCallback((bodyFormat: BodyFormat) => {
    setDraft((current) => ({
      ...current,
      bodyFormat,
      body: bodyFormat === 'none' ? '' : current.body,
    }))
    setErrors((current) => ({ ...current, body: '' }))
  }, [])

  const updatePair = useCallback(
    (section: PairSection, index: number, patch: Partial<KeyValuePair>) => {
      setDraft((current) => ({
        ...current,
        [section]: current[section].map((pair, pairIndex) =>
          pairIndex === index ? { ...pair, ...patch } : pair,
        ),
      }))
      setErrors((current) => ({ ...current, [`${section}.${index}.key`]: '' }))
    },
    [],
  )

  const addPair = useCallback((section: PairSection) => {
    setDraft((current) => ({ ...current, [section]: [...current[section], createPair()] }))
  }, [])

  const removePair = useCallback((section: PairSection, index: number) => {
    setDraft((current) => ({
      ...current,
      [section]: current[section].filter((_, pairIndex) => pairIndex !== index),
    }))
  }, [])

  const loadExample = useCallback(
    (index: number) => {
      const example = requestExamples[index]
      if (!example) return
      setDraft(structuredClone(example))
      setErrors({})
      setResult(null)
    },
    [requestExamples],
  )

  const restoreHistoryEntry = useCallback((entry: RequestHistoryEntry) => {
    setDraft(structuredClone(entry.request))
    setErrors({})
    setResult(null)
  }, [])

  const removeHistoryEntry = useCallback(
    (id: string) => {
      persistHistory(history.filter((entry) => entry.id !== id))
    },
    [history, persistHistory],
  )

  const clearHistory = useCallback(() => persistHistory([]), [persistHistory])

  const send = useCallback(async () => {
    const validationErrors = getDraftErrors(draft)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    const controller = new AbortController()
    const nextHistory = appendHistoryEntry(
      history,
      draft,
      crypto.randomUUID(),
      new Date().toISOString(),
    )
    persistHistory(nextHistory)
    controllerRef.current = controller
    setIsSending(true)
    setResult(null)

    try {
      setResult(await executeRequest(draft, { signal: controller.signal }))
    } finally {
      if (controllerRef.current === controller) controllerRef.current = null
      setIsSending(false)
    }
  }, [draft, history, persistHistory])

  const cancel = useCallback(() => controllerRef.current?.abort(), [])

  return {
    draft,
    errors,
    isSending,
    result,
    history,
    requestExamples,
    examplesLoading,
    examplesError,
    reloadExamples,
    setMethod,
    setUrl,
    setBody,
    setBodyFormat,
    updatePair,
    addPair,
    removePair,
    loadExample,
    restoreHistoryEntry,
    removeHistoryEntry,
    clearHistory,
    send,
    cancel,
  }
}