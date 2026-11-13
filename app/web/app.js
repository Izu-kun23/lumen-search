async function refresh() {
  const d = await api("/stats");
  stats([
    ["Indexed documents", d.documents, "Persistent local collection"],
    ["Unique terms", d.terms, "Position-aware inverted index"],
    ["Searches", d.queries, "Recorded query events"],
    [
      "Average latency",
      d.average_latency_ms + " ms",
      "Retrieval time, excluding network",
    ],
  ]);
  $("popular").innerHTML =
    d.popular
      .map(
        (p) =>
          `<div class="feature"><span>${esc(p.query)}</span><span>${p.searches}</span></div>`,
      )
      .join("") || "No queries yet.";
}
$("search").onsubmit = (e) => {
  e.preventDefault();
  busy(e.submitter, async () => {
    const d = await api(
      "/search?q=" +
        encodeURIComponent($("query").value) +
        "&algorithm=" +
        $("algorithm").value,
    );
    $("timing").textContent = d.count + " results · " + d.latency_ms + " ms";
    $("results").className = "";
    $("results").innerHTML =
      d.results
        .map(
          (r) =>
            `<article class="result"><small>${esc(r.url)}</small><h3><a href="${/^https?:\/\//.test(r.url) ? esc(r.url) : "#"}" target="_blank" rel="noopener noreferrer">${esc(r.title)} ↗</a></h3><p>${esc(r.content)}</p><small>Relevance score ${r.score}</small></article>`,
        )
        .join("") ||
      '<div class="empty">No matching documents. Try a broader query.</div>';
    message("Search complete");
    await refresh();
  });
};
let debounce;
$("query").oninput = () => {
  clearTimeout(debounce);
  debounce = setTimeout(async () => {
    try {
      const words = $("query").value.trim().split(/\s+/);
      const d = await api("/suggest?q=" + encodeURIComponent(words.at(-1)));
      $("suggestions").innerHTML = d
        .map((s) => `<button type="button">${esc(s)}</button>`)
        .join("");
      $("suggestions")
        .querySelectorAll("button")
        .forEach(
          (b) =>
            (b.onclick = () => {
              words[words.length - 1] = b.textContent;
              $("query").value = words.join(" ");
              $("search").requestSubmit();
            }),
        );
    } catch (e) {
      message(e.message, true);
    }
  }, 180);
};
$("crawl").onsubmit = (e) => {
  e.preventDefault();
  busy(e.submitter, async () => {
    message("Crawling approved pages…");
    const d = await api("/crawl", {
      method: "POST",
      body: JSON.stringify({ url: $("url").value, max_pages: 5 }),
    });
    message(
      d.indexed + " pages indexed. " + d.errors.map((e) => e.error).join("; "),
    );
    await refresh();
  });
};
refresh().catch((e) => message(e.message, true));
