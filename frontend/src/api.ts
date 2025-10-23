export async function health() {
  const res = await fetch('/api/health');
  if (!res.ok) throw new Error('Health failed');
  return res.json();
}
