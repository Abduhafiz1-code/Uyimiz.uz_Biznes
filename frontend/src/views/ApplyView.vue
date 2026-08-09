<script setup lang="ts">
/**
 * Uyimiz Agent bo'lish uchun ariza.
 *
 * Oqim: foydalanuvchi avval SMS-kod bilan kiradi (LoginView), keyin shu
 * yerda ariza to'ldiradi. Ariza "Kutilmoqda" holatida admin panelga
 * tushadi; admin tasdiqlagach CRM ochiladi.
 */
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import ThemeToggle from '@/components/ThemeToggle.vue'
import ToastHost from '@/components/ToastHost.vue'
import UiIcon from '@/components/UiIcon.vue'
import { useAuthStore } from '@/stores/auth'
import { toast } from '@/stores/toast'

const auth = useAuthStore()
const router = useRouter()

const TUMANLAR = [
  'Chilonzor', 'Yunusobod', "Mirzo Ulug'bek", 'Yakkasaroy', 'Shayxontohur',
  'Mirobod', 'Sergeli', 'Uchtepa', 'Bektemir', 'Yashnobod', 'Olmazor', 'Yangihayot',
]

const name = ref('')
const district = ref('')
const email = ref('')
const deals = ref<number | null>(null)
const busy = ref(false)
const error = ref('')

const formaOk = computed(() => name.value.trim().length >= 3 && !!district.value)

onMounted(async () => {
  await auth.refreshStatus()
  if (auth.canEnterCrm) {
    router.replace({ name: 'panel' })
    return
  }
  name.value = auth.agent?.name && auth.agent.name !== 'Foydalanuvchi' ? auth.agent.name : ''
  district.value = auth.agent?.district || ''
})

async function yubor() {
  if (!formaOk.value || busy.value) return
  error.value = ''
  busy.value = true
  try {
    await auth.applyAsAgent({
      name: name.value.trim(),
      district: district.value,
      email: email.value.trim() || undefined,
      historical_deals: deals.value ?? undefined,
    })
    toast.ok('Ariza yuborildi')
  } catch (e: any) {
    const d = e?.response?.data
    error.value = d?.detail || d?.error || d?.name?.[0] || d?.district?.[0] || 'Ariza yuborilmadi'
  } finally {
    busy.value = false
  }
}

async function chiqish() {
  await auth.logout()
  router.replace({ name: 'login' })
}
</script>

<template>
  <div class="wrap">
    <div class="tt"><ThemeToggle /></div>

    <div class="box anim-rise">
      <!-- kirmagan bo'lsa -->
      <template v-if="!auth.isAuthenticated">
        <svg class="logo"><use href="#star" /></svg>
        <h2 class="h-disp">Avval kiring</h2>
        <p class="sub">
          Ariza topshirish uchun telefon raqamingizni tasdiqlashingiz kerak.
        </p>
        <RouterLink class="btn btn-pri wide" :to="{ name: 'login' }">
          <UiIcon name="i-phone" :size="15" />Kirish sahifasi
        </RouterLink>
      </template>

      <!-- ariza ko'rib chiqilmoqda -->
      <template v-else-if="auth.isPending">
        <span class="badge wait"><UiIcon name="i-clock" :size="14" />Ko'rib chiqilmoqda</span>
        <h2 class="h-disp">Arizangiz qabul qilindi</h2>
        <p class="sub">
          Admin arizangizni tekshirmoqda. Tasdiqlangach shu yerdan CRM
          kabinetiga kirasiz — qayta ariza topshirish shart emas.
        </p>
        <dl class="info">
          <div><dt>Ism</dt><dd>{{ auth.agent?.name }}</dd></div>
          <div><dt>Telefon</dt><dd class="mono">{{ auth.agent?.phone }}</dd></div>
          <div v-if="auth.agent?.district"><dt>Hudud</dt><dd>{{ auth.agent.district }}</dd></div>
        </dl>
        <button class="btn wide" @click="auth.refreshStatus()">
          <UiIcon name="i-refresh" :size="15" />Holatni yangilash
        </button>
        <button class="linkbtn" @click="chiqish">Chiqish</button>
      </template>

      <!-- rad etilgan -->
      <template v-else-if="auth.isRejected">
        <span class="badge no"><UiIcon name="i-x" :size="14" />{{ auth.certification }}</span>
        <h2 class="h-disp">Ariza rad etilgan</h2>
        <p class="sub">
          Ma'lumotlarni to'ldirib qayta topshirishingiz mumkin. Savollar
          bo'lsa qo'llab-quvvatlash xizmatiga murojaat qiling.
        </p>
        <button class="btn btn-pri wide" @click="auth.certification = 'Rad etilgan'; error = ''">
          Qayta topshirish
        </button>
        <button class="linkbtn" @click="chiqish">Chiqish</button>
      </template>

      <!-- ariza formasi -->
      <template v-else>
        <span class="eyebrow">Uyimiz Agent</span>
        <h2 class="h-disp">Agent bo'lish</h2>
        <p class="sub">
          Arizangizni admin ko'rib chiqadi. Tasdiqlangach mijozlar hudud va
          reytingingiz bo'yicha avtomatik biriktiriladi.
        </p>

        <label class="field">
          <span class="field-label">To'liq ism</span>
          <span class="inp">
            <UiIcon name="i-user" :size="15" />
            <input v-model="name" type="text" placeholder="Familiya Ism" required />
          </span>
        </label>

        <label class="field">
          <span class="field-label">Ishlaydigan hudud</span>
          <span class="inp">
            <UiIcon name="i-pin" :size="15" />
            <select v-model="district" required>
              <option value="" disabled>Tumanni tanlang</option>
              <option v-for="t in TUMANLAR" :key="t" :value="t">{{ t }}</option>
            </select>
          </span>
        </label>

        <label class="field">
          <span class="field-label">Email <em>(ixtiyoriy)</em></span>
          <span class="inp">
            <UiIcon name="i-mail" :size="15" />
            <input v-model="email" type="email" placeholder="ism@pochta.uz" />
          </span>
        </label>

        <label class="field">
          <span class="field-label">Ilgari yopgan bitimlar soni <em>(ixtiyoriy)</em></span>
          <span class="inp">
            <UiIcon name="i-check" :size="15" />
            <input v-model.number="deals" type="number" min="0" max="10000" placeholder="0" />
          </span>
        </label>

        <Transition name="toast">
          <p v-if="error" class="err"><UiIcon name="i-x" :size="14" />{{ error }}</p>
        </Transition>

        <button class="btn btn-pri wide" :disabled="busy || !formaOk" @click="yubor">
          <span v-if="busy" class="spinner" />
          <template v-else><UiIcon name="i-shield" :size="15" />Ariza yuborish</template>
        </button>
        <button class="linkbtn" @click="chiqish">Chiqish</button>
      </template>
    </div>

    <ToastHost />
  </div>
</template>

<style scoped>
.wrap {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 40px 22px;
}
.tt {
  position: absolute;
  top: 20px;
  right: 22px;
}
.box {
  width: 100%;
  max-width: 400px;
}
.logo {
  width: 40px;
  height: 40px;
  color: var(--teal);
  margin-bottom: 14px;
}
.box h2 {
  font-size: 27px;
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
.field-label em {
  font-style: normal;
  color: var(--text-3);
  font-weight: 400;
}
.inp select {
  width: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  outline: none;
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
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  font-weight: 600;
  padding: 5px 10px;
  border-radius: 999px;
  margin-bottom: 12px;
}
.badge.wait {
  color: var(--amber, #d08700);
  background: color-mix(in srgb, var(--amber, #d08700) 14%, transparent);
}
.badge.no {
  color: var(--rose);
  background: var(--rose-glow);
}
.info {
  display: grid;
  gap: 1px;
  background: var(--line-soft);
  border: 1px solid var(--line-soft);
  border-radius: var(--r-m);
  overflow: hidden;
  margin-bottom: 18px;
}
.info > div {
  background: var(--surface);
  padding: 11px 13px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.info dt {
  font-size: 12px;
  color: var(--text-3);
}
.info dd {
  font-size: 13px;
  font-weight: 600;
  margin: 0;
}
.linkbtn {
  display: block;
  width: 100%;
  margin-top: 12px;
  border: 0;
  background: transparent;
  color: var(--text-3);
  font: inherit;
  font-size: 12.5px;
  cursor: pointer;
}
.linkbtn:hover {
  color: var(--rose);
}
</style>
