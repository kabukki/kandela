import { env } from "cloudflare:workers";
import { similarity } from "ml-distance";

export default {
  async fetch(request) {
    const secret = 'shoe';

    const url = new URL(request.url);

    if (url.pathname === "/test") {
      const file = await env.SOURCES.get("Cardiovasculaire R2C.pdf");
      const markdown = await env.AI.toMarkdown({
        name: "Humanités médicales.pdf",
        blob: await file!.blob(),
      });
      return new Response(markdown.format === 'markdown' ? markdown.data : markdown.error, { headers: { "content-type": "text/html; charset=utf-8" } });
    }

    if (url.pathname === "/guess") {
      const text = url.searchParams.get("q") ?? "";

      if (text) {
        if (text === secret) {
          return new Response(JSON.stringify({ score: 100 }), { headers: { "content-type": "application/json" } });
        }

        // await env.AI.toMarkdown({})
        const [secretEmbedding, guessEmbedding] = await env.VECTORIZE.getByIds([secret, text]);

        if (!guessEmbedding) {
          return new Response(JSON.stringify({ error: "Unknown werfdsord" }), { status: 404, headers: { "content-type": "application/json" } });
        }

        const sim = similarity.cosine(guessEmbedding.values, secretEmbedding.values);
        const score = Math.round(sim * 100);

        // console.log(await env.VECTORIZE.query(secretEmbedding.values, { topK: 100 }));

        return new Response(JSON.stringify({ score }), { headers: { "content-type": "application/json" } });
      }

      return new Response(JSON.stringify({ score: 0 }), { headers: { "content-type": "application/json" } });
    }

		return new Response(null, { status: 404 });
  },
} satisfies ExportedHandler<Env>;
