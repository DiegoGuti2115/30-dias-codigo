// src/app/api/mock/examples/route.ts
import { NextResponse } from 'next/server'
import examples from '../../../../../data/request-examples.json'

export const dynamic = 'force-static'

export function GET() {
  return NextResponse.json(examples)
}