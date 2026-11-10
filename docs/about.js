// "About this project" overlay, shared by every page.
// Any element with [data-about] opens it; its href stays as a fallback without JavaScript.
(function () {
  const REPO = 'https://github.com/TheRealNepomuk/gtl-track-viewer';
  const dlg = document.createElement('dialog');
  dlg.className = 'about';
  dlg.setAttribute('aria-labelledby', 'about-title');
  dlg.innerHTML = `
    <div class="about-head">
      <h2 id="about-title">About this project</h2>
      <button type="button" class="about-close" aria-label="Close">×</button>
    </div>
    <div class="about-body">
      <p><b>GTL Track Viewer</b> lets you look at the tracks of the
      <a href="https://www.altbierbude.de" target="_blank" rel="noopener">Altbierbude</a> GT Legends track pack in 3D,
      without starting the game: shape, height profile, sectors, pit lane and grid, plus a drive-along view.</p>

      <h3>Where the data comes from</h3>
      <p>Each track ships with an AI line file (.AIW) describing the road centre, road width, pit lane and grid.
      The viewer is drawn from that, and names, locations and track types come from each track's .gdb file.
      Gradients are averaged over 100 m. Side roads the AI doesn't use don't appear.</p>
      <p><b>Track data pulled on <span data-about-date>–</span>.</b> It shows the Altbierbude track pack as it was
      on that day. Tracks Altbierbude adds or removes later only show up here once the data is pulled again.</p>

      <h3>The tracks</h3>
      <p>All tracks belong to their original builders and converters. Only the derived line data is published here,
      no 3D models, textures or other mod files. If you built one of these tracks and want it removed or credited
      differently, please <a href="${REPO}/issues" target="_blank" rel="noopener">open an issue</a>.</p>

      <h3>License</h3>
      <p>The code is <a href="${REPO}/blob/main/LICENSE" target="_blank" rel="noopener">MIT licensed</a>, © 2026 TheRealNepomuk.
      The track data is not covered by it. If you build on this, please credit
      <i>GTL Track Viewer by TheRealNepomuk</i> with a link.</p>

      <div class="about-links">
        <a class="btn" href="${REPO}" target="_blank" rel="noopener">Source on GitHub ↗</a>
        <a class="btn" href="https://github.com/TheRealNepomuk/gt-legends-altbierbude-linux" target="_blank" rel="noopener">GT Legends on Linux ↗</a>
        <a class="coffee" href="https://www.buymeacoffee.com/TheRealNepomuk" target="_blank" rel="noopener">☕ Buy me a coffee</a>
      </div>
    </div>`;
  document.body.appendChild(dlg);
  dlg.querySelector('.about-close').onclick = () => dlg.close();
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });   // click on the backdrop closes
  document.addEventListener('click', e => {
    const a = e.target.closest('[data-about]');
    if (!a || typeof dlg.showModal !== 'function') return;   // very old browsers just follow the link
    e.preventDefault();
    dlg.showModal();
  });

  // pages call this once they know the date of their data (ISO yyyy-mm-dd)
  window.setDataDate = iso => {
    const d = new Date(iso + 'T12:00:00');
    const txt = isNaN(d) ? iso : d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    document.querySelectorAll('[data-about-date]').forEach(el => { el.textContent = txt; });
    return txt;
  };
})();
