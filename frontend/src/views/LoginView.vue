<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import ThemeToggle from '@/components/ThemeToggle.vue'
import ToastHost from '@/components/ToastHost.vue'
import UiIcon from '@/components/UiIcon.vue'
import { useAuthStore } from '@/stores/auth'
import { toast } from '@/stores/toast'

const auth = useAuthStore()
const router = useRouter()

const phone = ref('+998901234567')
const password = ref('uyimiz2026')
const busy = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  busy.value = true
  try {
    await auth.login(phone.value.trim(), password.value)
    toast.ok(`Xush kelibsiz, ${auth.agent?.name ?? 'agent'}`)
    router.replace({ name: 'panel' })
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Kirishda xatolik yuz berdi'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth">
    <!-- chap: brend tomoni -->
    <section class="pitch girih girih-live">
      <div class="pitch-in anim-rise">
        <svg class="logo"><use href="#star" /></svg>
        <span class="eyebrow">Uyimiz Agent · CRM</span>
        <h1 class="h-disp">Mijozlar o'zi keladi — siz bitimni yoping.</h1>
        <p>
          Platforma mijozlarni hudud va reytingingiz bo'yicha avtomatik biriktiradi. Har bir bitim
          shu yerda ochiladi, kuzatiladi va onlayn shartnoma bilan yopiladi.
        </p>

        <ul class="pts">
          <li><UiIcon name="i-check" :size="15" />Avtomatik mijoz oqimi</li>
          <li><UiIcon name="i-check" :size="15" />Ochiq reyting va daraja tizimi</li>
          <li><UiIcon name="i-check" :size="15" />Bitim va komissiya nazorati</li>
        </ul>

        <div class="stats">
          <div><b>1–2%</b><small>fiks komissiya</small></div>
          <div><b>10–15%</b><small>platforma ulushi</small></div>
          <div><b>myID</b><small>shaxs tekshiruvi</small></div>
        </div>
      </div>
    </section>

    <!-- o'ng: forma -->
    <section class="form-side">
      <div class="tt"><ThemeToggle /></div>

      <form class="box anim-rise" @submit.prevent="submit">
        <span class="eyebrow">Agent kabineti</span>
        <h2 class="h-disp">Kirish</h2>
        <p class="sub">Sertifikatlangan agentlar uchun. Raqamingiz myID bilan bog'langan.</p>

        <label class="field">
          <span class="field-label">Telefon raqami</span>
          <span class="inp">
            <UiIcon name="i-phone" :size="15" />
            <input v-model="phone" type="tel" autocomplete="username" placeholder="+998 __ ___ __ __" required />
          </span>
        </label>

        <label class="field">
          <span class="field-label">Parol</span>
          <span class="inp">
            <UiIcon name="i-lock" :size="15" />
            <input v-model="password" type="password" autocomplete="current-password" placeholder="••••••••" required />
          </span>
        </label>

        <Transition name="toast">
          <p v-if="error" class="err"><UiIcon name="i-x" :size="14" />{{ error }}</p>
        </Transition>

        <button class="btn btn-pri wide" type="submit" :disabled="busy">
          <span v-if="busy" class="spinner" />
          <template v-else>
            <UiIcon name="i-shield" :size="15" />
            Kabinetga kirish
          </template>
        </button>

        <div class="demo">
          <b>Demo hisob</b>
          <span class="mono">+998901234567 · uyimiz2026</span>
        </div>
      </form>
    </section>

    <ToastHost />
  </div>
</template>

<style scoped>
.auth {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  min-height: 100vh;
}

/* ---- chap ---- */
.pitch {
  position: relative;
  display: grid;
  place-items: center;
  padding: 46px;
  background-color: var(--frame);
  border-right: 1px solid var(--line-soft);
  overflow: hidden;
}
.pitch::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(760px 420px at 68% -12%, var(--teal-glow), transparent 64%);
  pointer-events: none;
}
.pitch-in {
  position: relative;
  max-width: 460px;
}
.logo {
  width: 44px;
  height: 44px;
  color: var(--teal);
  margin-bottom: 20px;
}
.pitch h1 {
  font-size: clamp(26px, 3.2vw, 38px);
  margin: 10px 0 12px;
  max-width: 16ch;
}
.pitch p {
  color: var(--text-2);
  font-size: 14px;
  line-height: 1.65;
  max-width: 46ch;
}
.pts {
  list-style: none;
  margin: 22px 0;
  display: grid;
  gap: 9px;
}
.pts li {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 13.5px;
  color: var(--text-2);
}
.pts li :deep(.ico) {
  color: var(--teal);
}
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--line-soft);
  border: 1px solid var(--line-soft);
  border-radius: var(--r-m);
  overflow: hidden;
  margin-top: 26px;
}
.stats div {
  background: var(--surface);
  padding: 14px;
}
.stats b {
  display: block;
  font-family: var(--f-display);
  font-size: 19px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.stats small {
  font-size: 10.5px;
  color: var(--text-3);
}

/* ---- o'ng ---- */
.form-side {
  position: relative;
  display: grid;
  place-items: center;
  padding: 40px 26px;
}
.tt {
  position: absolute;
  top: 20px;
  right: 22px;
}
.box {
  width: 100%;
  max-width: 372px;
}
.box h2 {
  font-size: 30px;
  margin: 8px 0 6px;
}
.sub {
  font-size: 13px;
  color: var(--text-3);
  line-height: 1.6;
  margin-bottom: 22px;
}
.field {
  display: block;
  margin-bottom: 14px;
}
.wide {
  width: 100%;
  margin-top: 4px;
}
.err {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12.5px;
  color: var(--rose);
  background: var(--rose-glow);
  border: 1px solid color-mix(in srgb, var(--rose) 35%, transparent);
  border-radius: 9px;
  padding: 9px 11px;
  margin-bottom: 12px;
}
.demo {
  margin-top: 18px;
  padding: 12px;
  border-radius: 10px;
  border: 1px dashed var(--line);
  display: grid;
  gap: 3px;
}
.demo b {
  font-size: 11.5px;
  color: var(--text-2);
}
.demo span {
  font-size: 11.5px;
  color: var(--teal);
}

@media (max-width: 900px) {
  .auth {
    grid-template-columns: 1fr;
  }
  .pitch {
    display: none;
  }
}
</style>
