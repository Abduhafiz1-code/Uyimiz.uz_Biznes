<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import ThemeToggle from '@/components/ThemeToggle.vue'
import ToastHost from '@/components/ToastHost.vue'
import UiIcon from '@/components/UiIcon.vue'
import { useAuthStore } from '@/stores/auth'
import { toast } from '@/stores/toast'

const auth = useAuthStore()
const router = useRouter()

/**
 * Ikki xil kirish:
 *   • 'code'  — SMS-kod (asosiy yo'l, yangi agentlar shundan kiradi)
 *   • 'pass'  — parol (eski, admin bergan parolga ega agentlar uchun)
 */
const usul = ref<'code' | 'pass'>('code')
const bosqich = ref<1 | 2>(1)

const phone = ref('')
const password = ref('')
const code = ref('')
const busy = ref(false)
const error = ref('')
const demoCode = ref('')

const phoneOk = computed(() => phone.value.replace(/\D/g, '').length >= 9)
const toliqPhone = computed(() => {
  const d = phone.value.replace(/\D/g, '').slice(-9)
  return '+998' + d
})

function xato(e: any, fallback: string) {
  const d = e?.response?.data
  return d?.detail || d?.error || e?.message || fallback
}

/** Kirgandan keyin qayerga yo'naltirishni hal qiladi. */
function yonaltir() {
  if (auth.canEnterCrm) {
    toast.ok(`Xush kelibsiz, ${auth.agent?.name ?? 'agent'}`)
    router.replace({ name: 'panel' })
  } else {
    // Agent emas yoki ariza hali tasdiqlanmagan — ariza sahifasiga.
    router.replace({ name: 'apply' })
  }
}

async function kodYuborish() {
  if (!phoneOk.value || busy.value) return
  error.value = ''
  busy.value = true
  try {
    const res = await auth.sendCode(toliqPhone.value)
    demoCode.value = res.demoCode
    bosqich.value = 2
  } catch (e: any) {
    error.value = xato(e, "Kod yuborilmadi. Qaytadan urinib ko'ring")
  } finally {
    busy.value = false
  }
}

async function kodniTasdiqlash() {
  if (code.value.replace(/\D/g, '').length < 4 || busy.value) return
  error.value = ''
  busy.value = true
  try {
    await auth.verifyCode(toliqPhone.value, code.value.replace(/\D/g, ''))
    yonaltir()
  } catch (e: any) {
    error.value = xato(e, "Kod noto'g'ri")
  } finally {
    busy.value = false
  }
}

async function parolBilan() {
  error.value = ''
  busy.value = true
  try {
    await auth.login(toliqPhone.value, password.value)
    yonaltir()
  } catch (e: any) {
    error.value = xato(e, 'Kirishda xatolik yuz berdi')
  } finally {
    busy.value = false
  }
}

function usulniAlmashtir(u: 'code' | 'pass') {
  usul.value = u
  bosqich.value = 1
  error.value = ''
  code.value = ''
  demoCode.value = ''
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

      <form
        class="box anim-rise"
        @submit.prevent="usul === 'pass' ? parolBilan() : bosqich === 1 ? kodYuborish() : kodniTasdiqlash()"
      >
        <span class="eyebrow">Agent kabineti</span>
        <h2 class="h-disp">Kirish</h2>
        <p class="sub">
          Telefon raqamingizni kiriting — tasdiqlash kodi yuboriladi.
        </p>

        <!-- kirish usuli -->
        <div class="tabs">
          <button
            type="button"
            :class="['tab', usul === 'code' && 'on']"
            @click="usulniAlmashtir('code')"
          >
            SMS-kod
          </button>
          <button
            type="button"
            :class="['tab', usul === 'pass' && 'on']"
            @click="usulniAlmashtir('pass')"
          >
            Parol
          </button>
        </div>

        <label class="field">
          <span class="field-label">Telefon raqami</span>
          <span class="inp">
            <UiIcon name="i-phone" :size="15" />
            <input
              v-model="phone"
              type="tel"
              autocomplete="username"
              placeholder="90 123 45 67"
              :disabled="usul === 'code' && bosqich === 2"
              required
            />
          </span>
        </label>

        <!-- parol bilan -->
        <label v-if="usul === 'pass'" class="field">
          <span class="field-label">Parol</span>
          <span class="inp">
            <UiIcon name="i-lock" :size="15" />
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              required
            />
          </span>
        </label>

        <!-- kod bilan, 2-bosqich -->
        <template v-if="usul === 'code' && bosqich === 2">
          <p v-if="demoCode" class="testmode">
            Test rejimi — kod: <b>{{ demoCode }}</b>
          </p>
          <label class="field">
            <span class="field-label">Tasdiqlash kodi</span>
            <span class="inp">
              <UiIcon name="i-shield" :size="15" />
              <input
                v-model="code"
                inputmode="numeric"
                maxlength="4"
                placeholder="0000"
                class="code-inp"
                required
              />
            </span>
          </label>
        </template>

        <Transition name="toast">
          <p v-if="error" class="err"><UiIcon name="i-x" :size="14" />{{ error }}</p>
        </Transition>

        <button
          class="btn btn-pri wide"
          type="submit"
          :disabled="busy || (usul === 'code' && bosqich === 1 && !phoneOk)"
        >
          <span v-if="busy" class="spinner" />
          <template v-else>
            <UiIcon name="i-shield" :size="15" />
            {{ usul === 'pass' ? 'Kabinetga kirish' : bosqich === 1 ? 'Kod yuborish' : 'Tasdiqlash' }}
          </template>
        </button>

        <button
          v-if="usul === 'code' && bosqich === 2"
          type="button"
          class="linkbtn"
          @click="usulniAlmashtir('code')"
        >
          Raqamni o'zgartirish
        </button>

        <p class="apply-hint">
          Hali agent emasmisiz?
          <RouterLink :to="{ name: 'apply' }">Ariza topshiring</RouterLink>
        </p>
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
/* kirish usuli tanlagichi */
.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  padding: 4px;
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  margin-bottom: 16px;
}
.tab {
  border: 0;
  background: transparent;
  color: var(--text-2);
  font: inherit;
  font-size: 13px;
  padding: 8px 10px;
  border-radius: 7px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.tab:hover {
  color: var(--text-1);
}
.tab.on {
  background: var(--frame);
  color: var(--teal);
  font-weight: 600;
}

.code-inp {
  letter-spacing: 0.5em;
  font-size: 17px;
  font-weight: 700;
  text-align: center;
}

.testmode {
  font-size: 12px;
  color: var(--teal);
  background: var(--teal-glow);
  border: 1px dashed color-mix(in srgb, var(--teal) 40%, transparent);
  border-radius: 9px;
  padding: 9px 11px;
  margin-bottom: 12px;
  text-align: center;
}
.testmode b {
  font-size: 15px;
  letter-spacing: 0.2em;
}

.linkbtn {
  display: block;
  width: 100%;
  margin-top: 10px;
  border: 0;
  background: transparent;
  color: var(--text-3);
  font: inherit;
  font-size: 12.5px;
  cursor: pointer;
}
.linkbtn:hover {
  color: var(--teal);
}

.apply-hint {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid var(--line-soft);
  font-size: 12.5px;
  color: var(--text-3);
  text-align: center;
}
.apply-hint a {
  color: var(--teal);
  font-weight: 600;
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
