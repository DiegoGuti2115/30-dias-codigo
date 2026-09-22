import { NextResponse } from 'next/server'

export function GET() {
  return NextResponse.json({ error: 'Error simulado para la demo' }, { status: 503 })
}