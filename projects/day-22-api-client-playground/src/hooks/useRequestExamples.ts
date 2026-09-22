// src/hooks/useRequestExamples.ts
'use client'

import useSWR from 'swr'
import { fetchExamples, EXAMPLES_ENDPOINT } from '../lib/examples'
import type { ApiRequestDraft } from '../lib/types'
import { apiRequestDraftSchema } from '../lib/schema'
import examplesJson from '../../data/request-examples.json'

// Fallback local: si la red falla, la demo sigue funcionando
const localFallback: ApiRequestDraft[] = (examplesJson as unknown[]).map(
  (item) => apiRequestDraftSchema.parse(item),
)

export type UseRequestExamplesResult = {
  examples: ApiRequestDraft[]
  isLoading: boolean
  isError: boolean
  reload: () => void
}

export const useRequestExamples = (): UseRequestExamplesResult => {
  const { data, error, isLoading, mutate } = useSWR<ApiRequestDraft[]>(
    EXAMPLES_ENDPOINT,
    fetchExamples,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60_000,
      fallbackData: localFallback,
    },
  )

  return {
    examples: data ?? localFallback,
    isLoading,
    isError: Boolean(error),
    reload: () => { void mutate() },
  }
}