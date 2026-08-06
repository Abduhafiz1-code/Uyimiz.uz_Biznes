<script setup lang="ts">
/**
 * Bildirishnomalar — qo'ng'iroq belgisi bosilganda ochiladi.
 * Manba: faollik tasmasi (/api/activities/) + yaqin ko'rsatuvlar (/api/showings/).
 * "O'qilgan" holati brauzerda (localStorage) oxirgi ko'rilgan vaqt bo'yicha hisoblanadi.
 */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import api from '@/api/client'
import { dateTimeLabel, timeAgo } from '@/lib/format'
import type { Activity, Paginated, Showing } from '@/types'
import UiIcon from './UiIcon.vue'

const SEEN_KEY = 'uyimiz_notif_seen'

interface Item {
  id: string
  icon: string
  text: string
  meta: string
  at: string
  tone: 'teal' | 'brass' | 'plain'
}

const open = ref(false)
const loading = ref(true)
const activities = ref<Activity[]>([])
const showings = ref<Showing[]>([])
const seenAt = ref<number>(Number(localStorage.getItem(SEEN_KEY) ?? 0))
const root = ref<HTMLElement | null>(null)

const ICONS: Record<string, string> = {
  mijoz: 'i-user',
  "qo'ng'iroq": 'i-phone',
  "ko'rsatuv": 'i-calendar',
  bitim: 'i-doc',
  shartnoma: 'i-check',
  reyting: 'i-star',
}

const items = computed<Item[]>(() => {
  const fromActivity: Item[] = activities.value.map((a) => ({
    id: `a${a.id}`,
    icon: ICONS[a.kind] ?? 'i-bell',
    text: a.text,
    meta: timeAgo(a.created_at),
    at: a.created_at,
    tone: a.kind === 'bitim' || a.kind === 'shartnoma' ? 'teal' : 'plain',
  }))

  const fromShowings: Item[] = showings.value.map((s) => ({
    id: `s${s.id}`,
    icon: 'i-calendar',
    text: `${s.client_name} bilan ko'rsatuv — ${s.listing_address}`,
    meta: dateTimeLabel(s.scheduled_at),
    at: s.scheduled_at,
    tone: 'brass',
  }))

  return [...fromActivity, ...fromShowings]
    .sort((a, b) => new Date(b.at).getTime() - new Date(a.at).getTime())
    .slice(0, 12)
})

const unread = computed(
  () => items.value.filter((i) => new Date(i.at).getTime() > seenAt.value).length,
)

async function load() {
  loading.value = true
  try {
    const [a, s] = await Promise.all([
      api.get<Paginated<Activity>>('/activities/', { params: { page_size: 10 } }),
      api.get<Paginated<Showing>>('/showings/', { params: { upcoming: 'true', page_size: 5 } }),
    ])
    activities.value = a.data.results
    showings.value = s.data.results
  } catch {
    /* bildirishnoma yuklanmasa panel bo'sh ko'rinadi */
  } finally {
    loading.value = false
  }
}

function toggle() {
  open.value = !open.value
  if (open.value && !activities.value.length) load()
}

function markRead() {
  seenAt.value = Date.now()
  localStorage.setItem(SEEN_KEY, String(seenAt.value))
}

function onDocClick(e: MouseEvent) {
  if (open.value && root.value && !root.value.contains(e.target as Node)) open.value = false
}
function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') open.value = false
}

onMounted(() => {
  load()
  document.addEventListener('click', onDocClick)
  window.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onDocClick)
  window.removeEventListener('keydown', onKey)
})
</script>

<template>
  <div ref="root" class="wrap">
    <button
      class="btn btn-ghost btn-icon bell"
      :class="{ active: open }"
      aria-label="Bildirishnomalar"
      :aria-expanded="open"
      @click="toggle"
    >
      <UiIcon name="i-bell" :size="16" />
      <i v-if="unread" class="dot" />
    </button>

    <Transition name="pop">
      <div v-if="open" class="panel">
        <header>
          <div>
            <b>Bildirishnomalar</b>
            <small v-if="unread">{{ unread }} ta yangi</small>
            <small v-else>Yangi yo'q</small>
          </div>
          <button v-if="unread" class="mark" @click="markRead">O'qilgan</button>
        </header>

        <div v-if="loading" class="pad">
          <div v-for="i in 3" :key="i" class="sk" style="height: 40px; margin-bottom: 8px" />
        </div>

        <p v-else-if="!items.length" class="pad empty">Hozircha bildirishnoma yo'q.</p>

        <ul v-else class="list">
          <li
            v-for="it in items"
            :key="it.id"
            :class="[it.tone, { fresh: new Date(it.at).getTime() > seenAt }]"
          >
            <span class="ic"><UiIcon :name="it.icon" :size="14" /></span>
            <div>
              <span class="txt">{{ it.text }}</span>
              <small class="mono">{{ it.meta }}</small>
            </div>
          </li>
        </ul>

        <footer>
          <RouterLink to="/bitimlar" @click="open = false">Bitimlarga o'tish</RouterLink>
        </footer>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.wrap {
  position: relative;
}
.bell {
  position: relative;
}
.bell.active {
  color: var(--teal);
  border-color: var(--teal);
}
.dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--rose);
  animation: pulse-ring 2.2s var(--ease-out) infinite;
}

.panel {
  position: absolute;
  top: calc(100% + 9px);
  right: 0;
  z-index: 90;
  width: min(320px, calc(100vw - 24px));
  background: var(--frame);
  border: 1px solid var(--line);
  border-radius: var(--r-m);
  box-shadow: var(--shadow-pop);
  overflow: hidden;
}
.panel > header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 13px;
  border-bottom: 1px solid var(--line-soft);
}
.panel > header b {
  display: block;
  font-size: 13px;
}
.panel > header small {
  font-size: 10.5px;
  color: var(--text-3);
}
.mark {
  border: 0;
  background: none;
  font-family: inherit;
  font-size: 11px;
  color: var(--teal);
  cursor: pointer;
  padding: 3px 6px;
  border-radius: 6px;
}
.mark:hover {
  background: var(--teal-glow);
}

.pad {
  padding: 13px;
}
.empty {
  font-size: 12.5px;
  color: var(--text-3);
  text-align: center;
}

.list {
  list-style: none;
  max-height: 330px;
  overflow-y: auto;
}
.list li {
  display: flex;
  gap: 10px;
  padding: 11px 13px;
  border-bottom: 1px solid var(--line-soft);
  transition: background-color var(--dur-1) var(--ease-out);
}
.list li:hover {
  background: var(--surface-2);
}
.list li.fresh {
  background: var(--teal-glow);
}
.ic {
  display: grid;
  place-items: center;
  width: 27px;
  height: 27px;
  border-radius: 9px;
  background: var(--surface-2);
  color: var(--text-3);
  flex: none;
}
.list li.teal .ic {
  color: var(--teal);
}
.list li.brass .ic {
  color: var(--brass);
}
.txt {
  display: block;
  font-size: 12px;
  color: var(--text-2);
  line-height: 1.45;
}
.list li.fresh .txt {
  color: var(--text);
}
.list small {
  font-size: 10px;
  color: var(--text-3);
}

.panel > footer {
  padding: 10px 13px;
  border-top: 1px solid var(--line-soft);
  text-align: center;
}
.panel > footer a {
  font-size: 12px;
  color: var(--teal);
  text-decoration: none;
}
.panel > footer a:hover {
  text-decoration: underline;
}

.pop-enter-active,
.pop-leave-active {
  transition:
    opacity var(--dur-1) var(--ease-out),
    transform var(--dur-1) var(--ease-out);
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
}

@media (max-width: 560px) {
  .panel {
    position: fixed;
    top: calc(var(--topbar-h) + 6px);
    right: 8px;
    left: 8px;
    width: auto;
  }
}
</style>
