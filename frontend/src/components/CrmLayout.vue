<script setup lang="ts">
/**
 * 07-freym qobig'i: chapda agent navigatsiyasi + reyting shkalasi,
 * tepada qidiruv, mavzu almashtirgichi va profil.
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { monthLabel } from '@/lib/format'
import { useAuthStore } from '@/stores/auth'
import { toast } from '@/stores/toast'
import NotificationsBell from './NotificationsBell.vue'
import ThemeToggle from './ThemeToggle.vue'
import ToastHost from './ToastHost.vue'
import UiIcon from './UiIcon.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const navOpen = ref(false)

const links = [
  { to: '/', label: 'Panel', icon: 'i-sq' },
  { to: '/mijozlar', label: 'Mijozlar', icon: 'i-user' },
  { to: '/obyektlar', label: 'Obyektlar', icon: 'i-pin' },
  { to: '/bitimlar', label: 'Bitimlar', icon: 'i-doc' },
  { to: '/reyting', label: 'Reyting', icon: 'i-star' },
]

const agent = computed(() => auth.agent)

function isActive(to: string) {
  return to === '/' ? route.path === '/' : route.path.startsWith(to)
}

async function signOut() {
  await auth.logout()
  toast.ok('Tizimdan chiqdingiz')
  router.replace({ name: 'login' })
}

onMounted(() => {
  if (!auth.agent) auth.fetchMe()
})
</script>

<template>
  <div class="shell">
    <!-- ==== chap panel ==== -->
    <aside class="rail" :class="{ open: navOpen }">
      <RouterLink to="/" class="brand">
        <svg class="mark"><use href="#star" /></svg>
        <span>Uyimiz <b>Agent</b></span>
      </RouterLink>

      <nav>
        <RouterLink
          v-for="l in links"
          :key="l.to"
          :to="l.to"
          class="nav-link"
          :class="{ on: isActive(l.to) }"
          @click="navOpen = false"
        >
          <UiIcon :name="l.icon" :size="16" />
          <span>{{ l.label }}</span>
          <i v-if="isActive(l.to)" class="marker" />
        </RouterLink>
      </nav>

      <!-- reyting shkalasi — agentning asosiy motivatsiyasi (07-freym) -->
      <div v-if="agent" class="tier">
        <div class="tier-top">
          <span class="dim">Reyting darajasi</span>
          <b class="mono">{{ String(agent.rating).replace('.', ',') }} ★</b>
        </div>
        <div class="bar"><i :style="{ width: agent.tier_percent + '%' }" /></div>
        <div class="tier-note mono">
          <template v-if="agent.tier_next_label">
            {{ agent.tier_next_label }}'ga {{ agent.tier_remaining }} bitim
          </template>
          <template v-else>Eng yuqori daraja</template>
        </div>
      </div>

      <button class="nav-link out" @click="signOut">
        <UiIcon name="i-out" :size="16" />
        <span>Chiqish</span>
      </button>
    </aside>

    <div v-if="navOpen" class="rail-veil" @click="navOpen = false" />

    <!-- ==== o'ng tomon ==== -->
    <div class="main">
      <header class="topbar">
        <button class="btn btn-ghost btn-icon burger" aria-label="Menyu" @click="navOpen = !navOpen">
          <UiIcon name="i-list" :size="16" />
        </button>

        <label class="search">
          <UiIcon name="i-search" :size="15" />
          <input type="search" placeholder="Mijoz, obyekt yoki bitim qidiring…" @keyup.enter="router.push('/mijozlar')" />
        </label>

        <span class="spacer" />
        <span class="pill month mono">{{ monthLabel() }}</span>

        <!-- 2-talab: mavzu (rang) almashtirgichi tepada -->
        <ThemeToggle />

        <NotificationsBell />

        <RouterLink v-if="agent" to="/reyting" class="me">
          <span class="ava ava-sm">{{ agent.initials }}</span>
          <span class="me-txt">
            <b>{{ agent.name }}</b>
            <small>{{ agent.district }} · {{ agent.tier }}</small>
          </span>
        </RouterLink>
      </header>

      <main class="canvas">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <ToastHost />
  </div>
</template>

<style scoped>
.shell {
  display: flex;
  align-items: flex-start;
  min-height: 100vh;
}

/* ---------- chap panel ---------- */
.rail {
  position: sticky;
  top: 0;
  z-index: 40;
  flex: none;
  width: var(--rail-w);
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 18px 12px;
  background: var(--nav-bg);
  border-right: 1px solid var(--line-soft);
  transition: background-color var(--dur-2) var(--ease-in-out);
}

.brand {
  display: flex;
  align-items: center;
  gap: 9px;
  margin: 0 10px 20px;
  text-decoration: none;
  color: var(--text);
  font-family: var(--f-display);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.brand b {
  color: var(--teal);
  font-weight: 800;
}
.mark {
  width: 20px;
  height: 20px;
  color: var(--teal);
  flex: none;
  transition: transform var(--dur-3) var(--ease-out);
}
.brand:hover .mark {
  transform: rotate(45deg);
}

nav {
  display: grid;
  gap: 2px;
}
.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 10px;
  border: 0;
  border-radius: 9px;
  background: none;
  font-family: inherit;
  font-size: 13px;
  color: var(--text-2);
  text-decoration: none;
  cursor: pointer;
  transition:
    background-color var(--dur-1) var(--ease-out),
    color var(--dur-1) var(--ease-out),
    padding-left var(--dur-2) var(--ease-out);
}
.nav-link:hover {
  background: var(--surface-2);
  color: var(--text);
  padding-left: 14px;
}
.nav-link.on {
  background: var(--teal-glow);
  color: var(--teal);
  font-weight: 600;
}
.marker {
  position: absolute;
  left: 0;
  top: 50%;
  width: 3px;
  height: 17px;
  border-radius: 3px;
  background: var(--teal);
  transform: translateY(-50%);
  animation: pop var(--dur-2) var(--ease-out) both;
}

.tier {
  margin: 18px 10px 0;
  padding-top: 14px;
  border-top: 1px solid var(--line-soft);
}
.tier-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 7px;
}
.tier-top b {
  color: var(--teal);
  font-size: 11.5px;
}
.tier-note {
  font-size: 10px;
  color: var(--teal);
  margin-top: 7px;
}

.out {
  margin-top: auto;
  color: var(--text-3);
}
.out:hover {
  background: var(--rose-glow);
  color: var(--rose);
}

.rail-veil {
  display: none;
}

/* ---------- o'ng tomon ---------- */
.main {
  flex: 1;
  min-width: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  gap: 10px;
  height: var(--topbar-h);
  padding: 0 clamp(14px, 2.5vw, 24px);
  background: var(--topbar-bg);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--line-soft);
}
.burger {
  display: none;
}

.search {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  max-width: 340px;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--surface-2);
  color: var(--text-3);
  transition:
    border-color var(--dur-1) var(--ease-out),
    box-shadow var(--dur-1) var(--ease-out),
    max-width var(--dur-2) var(--ease-out);
}
.search:focus-within {
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-glow);
  max-width: 420px;
}
.search input {
  flex: 1;
  min-width: 0;
  border: 0;
  outline: none;
  background: none;
  color: var(--text);
  font-family: inherit;
  font-size: 13px;
}
.search input::placeholder {
  color: var(--text-3);
}

.spacer {
  flex: 1;
}
.month {
  font-size: 10.5px;
}

.me {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 4px 9px 4px 4px;
  border-radius: 30px;
  border: 1px solid var(--line);
  text-decoration: none;
  color: var(--text);
  transition:
    border-color var(--dur-1) var(--ease-out),
    background-color var(--dur-1) var(--ease-out);
}
.me:hover {
  border-color: var(--teal);
  background: var(--surface-2);
}
.me-txt {
  display: grid;
  line-height: 1.25;
}
.me-txt b {
  font-size: 12.5px;
  font-weight: 700;
}
.me-txt small {
  font-size: 10.5px;
  color: var(--text-3);
}

.canvas {
  position: relative;
  padding: 22px clamp(14px, 2.5vw, 26px) 70px;
}

/* ---------- moslashuvchanlik ---------- */
@media (max-width: 1080px) {
  .me-txt {
    display: none;
  }
  .me {
    padding: 4px;
  }
}
@media (max-width: 900px) {
  .rail {
    position: fixed;
    left: 0;
    top: 0;
    transform: translateX(-100%);
    transition: transform var(--dur-2) var(--ease-out);
    z-index: 60;
    box-shadow: var(--shadow-pop);
  }
  .rail.open {
    transform: none;
  }
  .rail-veil {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 50;
    background: rgba(0, 0, 0, 0.5);
    animation: fade var(--dur-2) var(--ease-out);
  }
  .burger {
    display: inline-flex;
  }
  .month {
    display: none;
  }
  /* Menyu ochilganda navigatsiya barmoq uchun kattaroq bo'lsin. */
  .nav-link {
    padding: 12px 12px;
    font-size: 14px;
  }
}

/* Telefon: qidiruv maydoni topbarda joy yetarli bo'lmaganda olib tashlanadi —
   har bir sahifaning o'z qidiruvi bor. */
@media (max-width: 700px) {
  .search {
    display: none;
  }
  .topbar {
    gap: 8px;
  }
  .spacer {
    flex: 1;
  }
}
@media (max-width: 380px) {
  .topbar {
    padding: 0 10px;
    gap: 6px;
  }
}
</style>
