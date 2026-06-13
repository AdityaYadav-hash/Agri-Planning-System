// ---------- Recommendation ----------
const recForm = document.getElementById("recommend-form");
const recResult = document.getElementById("recommend-result");

recForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  recResult.innerHTML = "Analyzing...";
  const data = Object.fromEntries(new FormData(recForm).entries());
  try {
    const r = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const json = await r.json();
    if (!json.ok) throw new Error(json.error || "Failed");
    recResult.innerHTML = `
      <h3>Top recommendations</h3>
      <div class="rec-list">
        ${json.recommendations.map(x => `
          <div class="rec-item">
            <span class="crop">${x.crop}</span>
            <span class="conf">${x.confidence}% match</span>
          </div>`).join("")}
      </div>
      ${json.notes.length ? `<div class="notes"><strong>Notes:</strong><ul>${json.notes.map(n => `<li>${n}</li>`).join("")}</ul></div>` : ""}
    `;
  } catch (err) {
    recResult.innerHTML = `<div class="error">${err.message}</div>`;
  }
});

// ---------- Weather ----------
const wForm = document.getElementById("weather-form");
const wResult = document.getElementById("weather-result");

wForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const city = document.getElementById("city").value.trim();
  wResult.innerHTML = "Loading...";
  try {
    const r = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    const j = await r.json();
    if (!j.ok) throw new Error(j.error);
    wResult.innerHTML = `
      <div class="weather-card">
        <img src="https://openweathermap.org/img/wn/${j.icon}@2x.png" alt="">
        <div>
          <div class="temp">${Math.round(j.temp)}°C</div>
          <div class="meta">${j.city}, ${j.country} — ${j.description}</div>
          <div class="meta">Humidity: ${j.humidity}% · Wind: ${j.wind} m/s</div>
        </div>
      </div>`;
  } catch (err) {
    wResult.innerHTML = `<div class="error">${err.message}</div>`;
  }
});

// ---------- Forum ----------
const postForm = document.getElementById("post-form");
const postsEl = document.getElementById("posts");

async function loadPosts() {
  const r = await fetch("/api/posts");
  const j = await r.json();
  if (!j.ok) return;
  postsEl.innerHTML = j.posts.length
    ? j.posts.map(p => `
        <div class="post">
          <h4>${escapeHtml(p.title)}</h4>
          <div class="meta">by ${escapeHtml(p.author)} · ${new Date(p.created_at).toLocaleString()}</div>
          <p>${escapeHtml(p.content)}</p>
        </div>`).join("")
    : `<div class="meta">No posts yet — be the first!</div>`;
}

postForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(postForm).entries());
  const r = await fetch("/api/posts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const j = await r.json();
  if (j.ok) { postForm.reset(); loadPosts(); }
  else alert(j.error);
});

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

loadPosts();
