
async function loadData(){
  const res = await fetch('../data/metrics.json', {cache:'no-store'});
  const data = await res.json();
  const ga = data.ga4; const ad = data.adsense;

  const fmt = new Intl.NumberFormat('it-IT');
  const eur = new Intl.NumberFormat('it-IT',{style:'currency',currency:ad.currency||'EUR'});

  document.getElementById('users').textContent = fmt.format(ga.totals.users || 0);
  document.getElementById('sessions').textContent = fmt.format(ga.totals.sessions || 0);
  document.getElementById('pageviews').textContent = fmt.format(ga.totals.pageviews || 0);
  document.getElementById('revenue').textContent = eur.format(ad.total_revenue || 0);

  const ctx1 = document.getElementById('trafficChart').getContext('2d');
  new Chart(ctx1, {
    type: 'line',
    data: {
      labels: ga.days,
      datasets: [
        {label:'Utenti', data: ga.users},
        {label:'Sessioni', data: ga.sessions},
        {label:'Pageviews', data: ga.pageviews},
      ]
    },
    options: {responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom'}}}
  });

  const ctx2 = document.getElementById('revenueChart').getContext('2d');
  new Chart(ctx2, {
    type: 'bar',
    data: {labels: ad.days, datasets:[{label:'Ricavi', data: ad.revenue}]},
    options: {responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom'}}}
  });
}
loadData();
