import { NextResponse } from 'next/server'

export function GET(request: Request) {
  const { searchParams } = new URL(request.url)

  return NextResponse.json({
    id: 'demo-user',
    name: 'Ada Lovelace',
    include: searchParams.get('include') ?? null,
  })
}