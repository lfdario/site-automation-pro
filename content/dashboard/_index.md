---
title: "Dashboard"
description: "Traffico e ricavi (aggiornato ogni 3 ore)"
---

<div id="dash" style="display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));margin-top:1rem">
  <div style="border:1px solid #eee;border-radius:12px;padding:16px">
    <div style="font-size:14px;opacity:.7">Utenti (30 giorni)</div>
    <div id="mUsers" style="font-size:28px;font-weight:700">—</div>
  </div>
  <div style="border:1px solid #eee;border-radius:12px;padding:16px">
    <div style="font-size:14px;opacity:.7">Sessioni</div>
    <div id="mSess" style="font-size:28px;font-weight:700">—</div>
  </div>
  <div style="border:1px solid #eee;border-radius:12px;padding:16px">
    <div style="font-size:14px;opacity:.7">Pageviews</div>
    <div id="mPv" style="font-size:28px;font-weight:700">—</div>
  </div>
  <div style="border:1px solid #eee;border-radius:12px;padding:16px">
    <div style="font-size:14px;opacity:.7">Ricavi stimati</div>
    <div id="mRev" style="font-size:28px;font-weight:700">—</div>
  </div>
</div>

<script>
(async function(){
  try{
    const r = await fetch("/site-automation-pro/data/metrics.json", {cache:"no-store"});
    if(!r.ok) throw new Error("metrics not found");
    const m = await r.json();
    const n = x => (x==null? "—" : Intl.NumberFormat("it-IT").format(Math.round(x)));
    const e = x => (x==null? "—" : "€ " + (Math.round(x*100)/100).toFixed(2).replace(".",","));
    document.getElementById("mUsers").textContent = n(m.ga4?.users);
    document.getElementById("mSess").textContent = n(m.ga4?.sessions);
    document.getElementById("mPv").textContent   = n(m.ga4?.pageviews);
    document.getElementById("mRev").textContent  = e(m.adsense?.estimated_earnings);
  }catch(e){ /* mostra placeholder */ }
})();
</script>

> Se vedi “—”, attendi il prossimo aggiornamento automatico della metrica.
