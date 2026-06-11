// ============================================================
//  SmartGrocery — main.js
//  Vanilla JS: calls POST /api/classify, renders tagged list
// ============================================================

'use strict';

// ── Config ──────────────────────────────────────────────────
const API_URL = '/api/classify';

// ── Aisle metadata ──────────────────────────────────────────
const AISLE_META = {
  measured:   { icon: '⚖️',  label: 'Measured'   },
  staple:     { icon: '🧂',  label: 'Staple'      },
  produce:    { icon: '🌿',  label: 'Produce'     },
  dairy:      { icon: '🥛',  label: 'Dairy'       },
  bakery:     { icon: '🍞',  label: 'Bakery'      },
  frozen:     { icon: '❄️',  label: 'Frozen'      },
  household:  { icon: '🏠',  label: 'Household'   },
};

// ── State ───────────────────────────────────────────────────
let items = [];   // Array of API response objects

// ── DOM refs ────────────────────────────────────────────────
const form        = document.getElementById('grocery-form');
const itemInput   = document.getElementById('item-input');
const addBtn      = document.getElementById('add-btn');
const btnLabel    = document.getElementById('btn-label');
const btnSpinner  = document.getElementById('btn-spinner');
const errorBanner = document.getElementById('error-banner');
const errorText   = document.getElementById('error-text');
const groceryList = document.getElementById('grocery-list');
const emptyState  = document.getElementById('empty-state');
const listHeader  = document.getElementById('list-header');
const itemCount   = document.getElementById('item-count');

// ── Event listeners ─────────────────────────────────────────
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const value = itemInput.value.trim();
  if (!value) {
    shake(itemInput);
    return;
  }
  await classifyItem(value);
});

// ── Quick fill hint chips ───────────────────────────────────
function quickFill(value) {
  itemInput.value = value;
  itemInput.focus();
}

// ── API call ────────────────────────────────────────────────
async function classifyItem(item) {
  hideError();
  setLoading(true);

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item }),
    });

    if (res.status === 400) {
      const data = await res.json();
      showError(data.detail || 'This item is not a grocery item.');
      return;
    }

    if (!res.ok) {
      showError(`Server error (${res.status}). Please try again.`);
      return;
    }

    const data = await res.json();
    addItem(data);
    itemInput.value = '';
    itemInput.focus();

  } catch (err) {
    console.error('Fetch error:', err);
    showError('Cannot reach the server. Is the backend running?');
  } finally {
    setLoading(false);
  }
}

// ── Add item to state & re-render ───────────────────────────
function addItem(data) {
  items.unshift(data);    // newest first
  render();
}

// ── Clear all ───────────────────────────────────────────────
function clearAll() {
  items = [];
  render();
}

// ── Render list ─────────────────────────────────────────────
function render() {
  const hasItems = items.length > 0;

  emptyState.classList.toggle('hidden', hasItems);
  listHeader.classList.toggle('hidden', !hasItems);

  if (hasItems) {
    itemCount.textContent = items.length === 1 ? '1 item' : `${items.length} items`;
  }

  groceryList.innerHTML = items.map((item, index) => buildItemHTML(item, index)).join('');
}

// ── Build single item HTML ───────────────────────────────────
function buildItemHTML(data, index) {
  const meta   = AISLE_META[data.tag_type] || { icon: '🛒', label: data.tag_type };
  const detail = buildDetailText(data);

  // For 'measured' items the API returns a shade-based background
  // color AND a contrast-safe text_color.  For all other tags the
  // color is used as the text/border colour on a transparent bg.
  let badgeStyle;
  if (data.tag_type === 'measured' && data.text_color) {
    badgeStyle = `background:${escHtml(data.color)};`
               + `color:${escHtml(data.text_color)};`
               + `border-color:${escHtml(data.color)}`;
  } else {
    badgeStyle = `background:${escHtml(data.color)}20;`
               + `color:${escHtml(data.color)};`
               + `border-color:${escHtml(data.color)}50`;
  }

  return `
    <li class="grocery-item"
        style="--item-color: ${escHtml(data.color)}; animation-delay: ${index * 0.04}s"
        role="listitem">

      <div class="item-left">
        <span class="item-icon" aria-hidden="true">${meta.icon}</span>
        <div class="item-info">
          <span class="item-name">${escHtml(data.item)}</span>
          ${detail ? `<span class="item-meta">${escHtml(detail)}</span>` : ''}
        </div>
      </div>

      <div class="item-right">
        <span class="aisle-badge"
              style="${badgeStyle}">
          ${meta.label}
        </span>
        <button class="remove-btn"
                onclick="removeItem(${index})"
                aria-label="Remove ${escHtml(data.item)}">×</button>
      </div>
    </li>
  `;
}

// ── Detail text below item name ──────────────────────────────
function buildDetailText(data) {
  if (data.tag_type === 'measured' && data.metadata) {
    const { amount, unit, base_amount } = data.metadata;
    return `${amount} ${unit} — ${base_amount}${unit === 'l' || unit === 'ml' || unit === 'cl' ? ' ml' : ' g'} base`;
  }
  if (data.tag_type === 'staple') {
    return 'Pantry staple';
  }
  if (data.metadata && data.metadata.aisle) {
    return `${capitalise(data.metadata.aisle)} aisle`;
  }
  return '';
}

// ── Remove single item ───────────────────────────────────────
function removeItem(index) {
  items.splice(index, 1);
  render();
}

// ── Loading state ────────────────────────────────────────────
function setLoading(on) {
  addBtn.disabled = on;
  btnLabel.textContent = on ? 'Adding…' : 'Add';
  btnSpinner.classList.toggle('hidden', !on);
}

// ── Error helpers ────────────────────────────────────────────
function showError(msg) {
  errorText.textContent = msg;
  errorBanner.classList.remove('hidden');
}

function hideError() {
  errorBanner.classList.add('hidden');
}

// ── Shake animation on empty submit ─────────────────────────
function shake(el) {
  el.style.animation = 'none';
  el.getBoundingClientRect();            // force reflow
  el.style.animation = 'shakeX 0.4s ease';
  setTimeout(() => (el.style.animation = ''), 450);
}

// Add shakeX keyframes dynamically
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
@keyframes shakeX {
  0%,100% { transform: translateX(0); }
  20%,60% { transform: translateX(-6px); }
  40%,80% { transform: translateX(6px); }
}`;
document.head.appendChild(shakeStyle);

// ── Utilities ────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function capitalise(str) {
  return str ? str[0].toUpperCase() + str.slice(1) : str;
}

// ── Initial render ───────────────────────────────────────────
render();
