import { DashboardShell } from '../components/DashboardShell'
import { loadDashboard } from '../lib/dataSource'

export default async function DashboardPage() {
  const dashboard = await loadDashboard()

  return <DashboardShell dashboard={dashboard} />
}