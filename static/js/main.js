// main.js
function copyPiAddress(){
  const text = document.getElementById('piAddress') ? document.getElementById('piAddress').innerText
             : (document.getElementById('piAddressSmall') ? document.getElementById('piAddressSmall').innerText : '');
  navigator.clipboard.writeText(text).then(()=> {
    alert('Pi address copied to clipboard');
  });
}

// Modal handling
function openModal(mode){
  const modal = document.getElementById('piModal');
  document.getElementById('modalTitle').innerText = (mode === 'provide') ? 'Provide Donation (PI)' : 'Request Donation (PI)';
  document.getElementById('formType').value = (mode === 'provide') ? 'provided' : 'requested';
  document.getElementById('amountInput').value = '';
  document.getElementById('phpVal').innerText = '—';
  modal.classList.add('show');
}
function closeModal(){
  document.getElementById('piModal').classList.remove('show');
}

// live price conversion for modal amount field
document.addEventListener('DOMContentLoaded', ()=> {
  const amountInput = document.getElementById('amountInput');
  if(amountInput){
    amountInput.addEventListener('input', ()=> {
      const val = parseFloat(amountInput.value || 0);
      if(isNaN(val) || val <= 0){ document.getElementById('phpVal').innerText = '—'; return; }
      fetch('/price').then(r=>r.json()).then(data=>{
        const php = parseFloat(data.php || 0);
        const phpVal = (val * php).toFixed(2);
        document.getElementById('phpVal').innerText = phpVal + ' PHP';
      }).catch(()=> document.getElementById('phpVal').innerText = 'N/A');
    });
  }
});
