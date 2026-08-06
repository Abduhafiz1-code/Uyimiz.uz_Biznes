<!-- Dizayn taxtasidagi ikonka to'plami — bir marta DOMga qo'yiladi. -->
<template>
  <svg width="0" height="0" style="position: absolute" aria-hidden="true">
    <symbol id="star" viewBox="0 0 100 100">
      <rect x="21" y="21" width="58" height="58" rx="4" fill="none" stroke="currentColor" stroke-width="7" />
      <rect
        x="21"
        y="21"
        width="58"
        height="58"
        rx="4"
        fill="none"
        stroke="currentColor"
        stroke-width="7"
        transform="rotate(45 50 50)"
      />
    </symbol>
    <symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></symbol>
    <symbol id="i-pin" viewBox="0 0 24 24">
      <path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z" /><circle cx="12" cy="10" r="2.5" />
    </symbol>
    <symbol id="i-check" viewBox="0 0 24 24"><path d="m4 12.5 5 5L20 6.5" /></symbol>
    <symbol id="i-shield" viewBox="0 0 24 24">
      <path d="M12 3l8 3v6c0 5-3.5 8.2-8 9-4.5-.8-8-4-8-9V6l8-3Z" /><path d="m8.5 12 2.5 2.5 4.5-4.5" />
    </symbol>
    <symbol id="i-chat" viewBox="0 0 24 24"><path d="M20 15a3 3 0 0 1-3 3H8l-4 3V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3Z" /></symbol>
    <symbol id="i-doc" viewBox="0 0 24 24">
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Z" /><path d="M14 3v5h5M9 13h6M9 17h4" />
    </symbol>
    <symbol id="i-bed" viewBox="0 0 24 24"><path d="M3 18v-8h13a4 4 0 0 1 4 4v4M3 14h17M3 18v2M20 18v2" /></symbol>
    <symbol id="i-sq" viewBox="0 0 24 24"><path d="M4 4h16v16H4z" /><path d="M4 9h5M15 4v5" /></symbol>
    <symbol id="i-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 3.6-6 8-6s8 2 8 6" /></symbol>
    <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6" /></symbol>
    <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" /></symbol>
    <symbol id="i-star" viewBox="0 0 24 24"><path d="m12 4 2.4 5 5.6.8-4 3.9 1 5.6-5-2.7-5 2.7 1-5.6-4-3.9 5.6-.8Z" /></symbol>
    <symbol id="i-camera" viewBox="0 0 24 24"><path d="M4 8h3l2-2.5h6L17 8h3v11H4z" /><circle cx="12" cy="13" r="3.5" /></symbol>
    <symbol id="i-bell" viewBox="0 0 24 24">
      <path d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 6H4s2-1 2-6" /><path d="M10 19a2 2 0 0 0 4 0" />
    </symbol>
    <symbol id="i-gear" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="3.2" />
      <path
        d="M12 3.5v2.3M12 18.2v2.3M4.6 7l2 1.15M17.4 15.85l2 1.15M4.6 17l2-1.15M17.4 8.15l2-1.15M3.5 12h2.3M18.2 12h2.3"
      />
    </symbol>
    <symbol id="i-lock" viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9" rx="2.4" /><path d="M8 11V7.5a4 4 0 0 1 8 0V11" /></symbol>
    <symbol id="i-list" viewBox="0 0 24 24"><path d="M9 6h11M9 12h11M9 18h11" /><path d="M4 6h.01M4 12h.01M4 18h.01" /></symbol>
    <symbol id="i-phone" viewBox="0 0 24 24">
      <path d="M5 3h4l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2Z" />
    </symbol>
    <symbol id="i-calendar" viewBox="0 0 24 24">
      <rect x="3.5" y="5" width="17" height="16" rx="2.5" /><path d="M3.5 10h17M8 3v4M16 3v4" />
    </symbol>
    <symbol id="i-out" viewBox="0 0 24 24"><path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3" /><path d="M10 16l-4-4 4-4M6 12h10" /></symbol>
    <symbol id="i-sun" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="4.2" />
      <path d="M12 2.5v2.2M12 19.3v2.2M4.2 4.2l1.6 1.6M18.2 18.2l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.2 19.8l1.6-1.6M18.2 5.8l1.6-1.6" />
    </symbol>
    <symbol id="i-moon" viewBox="0 0 24 24"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" /></symbol>
    <symbol id="i-trend" viewBox="0 0 24 24"><path d="M3 17l5.5-6 4 3.5L21 6" /><path d="M15 6h6v6" /></symbol>
    <symbol id="i-wallet" viewBox="0 0 24 24">
      <rect x="3" y="6" width="18" height="13" rx="2.5" /><path d="M3 10h18M16.5 14.5h.01" />
    </symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5" /><path d="M12 7.5V12l3 2" /></symbol>
    <symbol id="i-x" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" /></symbol>
    <symbol id="i-filter" viewBox="0 0 24 24"><path d="M3 5h18l-7 8v6l-4-2v-4Z" /></symbol>
    <symbol id="i-inbox" viewBox="0 0 24 24">
      <path d="M3 13h5l1.5 3h5L16 13h5" /><path d="M5 5h14l2 8v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4Z" />
    </symbol>
  </svg>
</template>
