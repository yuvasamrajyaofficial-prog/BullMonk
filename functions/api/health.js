export async function onRequestGet() {
  const data = {
    status: "online",
    service: "BullMonk Quantitative Engine (Cloudflare Edge)",
    version: "1.0.0",
    edge_location: "Cloudflare Pages Functions",
    indicators_count: 29,
    timestamp: new Date().toISOString()
  };

  return new Response(JSON.stringify(data), {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-cache"
    }
  });
}
