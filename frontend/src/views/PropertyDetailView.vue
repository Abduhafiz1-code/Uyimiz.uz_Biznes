<script setup lang="ts">
/**
 * Obyekt tafsiloti — alohida sahifa (avval o'ng tomondan chiqadigan kichkina
 * panel edi, endi mustaqil marshrut: /obyektlar/:id). Ro'yxatga qaytmasdan,
 * pastdagi "Boshqa obyektlar" qatoridan bosib, sahifa ichida boshqa obyektga
 * o'tish mumkin.
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api from '@/api/client'
import EmptyState from '@/components/EmptyState.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import UiIcon from '@/components/UiIcon.vue'
import { SUPPORT_PHONE, telHref } from '@/lib/config'
import { dateLabel, nf, statusPill } from '@/lib/format'
import { toast } from '@/stores/toast'
import type { Client, Paginated, Property } from '@/types'

const route = useRoute()
const router = useRouter()

const property = ref<Property | null>(null)
const loading = ref(true)
const notFound = ref(false)

const others = ref<Property[]>([])

function badgeClass(b: string) {
  if (b === 'VIP') return 'pill pill-vip'
  if (b === 'Premium') return 'pill pill-ok'
  return 'pill'
}

async function loadProperty(id: string | string[]) {
  loading.value = true
  notFound.value = false
  try {
    const { data } = await api.get<Property>(`/properties/${id}/`)
    property.value = data
  } catch {
    notFound.value = true
    property.value = null
  } finally {
    loading.value = false
  }
}

async function loadOthers() {
  try {
    const { data } = await api.get<Paginated<Property>>('/properties/', {
      params: { page_size: 16 },
    })
    others.value = data.results
  } catch {
    // Panel ixtiyoriy — xato bo'lsa sahifa asosiy qismi ishlashda davom etadi.
  }
}

/** Ro'yxatga qaytmasdan, shu sahifa ichida boshqa obyektga o'tish. */
function goTo(id: number) {
  if (property.value?.id === id) return
  router.push({ name: 'property-detail', params: { id } })
}

function goBack() {
  router.push({ name: 'properties' })
}

watch(
  () => route.params.id,
  (id) => {
    if (id) loadProperty(id)
  },
  { immediate: true },
)

loadOthers()

/* ---------- ko'rsatuv belgilash ---------- */

const showingOpen = ref(false)
const showingSaving = ref(false)
const showingError = ref('')
const clients = ref<Client[]>([])
const form = ref({ client: '', date: '', time: '15:00', note: '' })

const ownerPhone = computed(() => property.value?.owner_phone || SUPPORT_PHONE)

/** Bugundan oldingi sanani tanlab bo'lmasin. */
const minDate = computed(() => new Date().toISOString().slice(0, 10))

function defaultDate() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().slice(0, 10)
}

async function openShowing() {
  showingError.value = ''
  form.value = { client: '', date: defaultDate(), time: '15:00', note: '' }
  showingOpen.value = true
  if (!clients.value.length) {
    try {
      const { data } = await api.get<Paginated<Client>>('/clients/', {
        params: { page_size: 100, open: 'true' },
      })
      clients.value = data.results
    } catch {
      showingError.value = "Mijozlar ro'yxatini yuklab bo'lmadi"
    }
  }
}

async function saveShowing() {
  if (!property.value) return
  if (!form.value.client) {
    showingError.value = 'Mijozni tanlang'
    return
  }
  showingSaving.value = true
  showingError.value = ''
  try {
    await api.post('/showings/', {
      client: Number(form.value.client),
      listing: property.value.id,
      // Local vaqt sifatida yuboriladi; backend Asia/Tashkent zonasida saqlaydi.
      scheduled_at: new Date(`${form.value.date}T${form.value.time}`).toISOString(),
      status: 'Rejalashtirilgan',
      note: form.value.note,
    })
    const who = clients.value.find((c) => c.id === Number(form.value.client))
    toast.ok(`Ko'rsatuv belgilandi — ${who?.name ?? 'mijoz'}`)
    showingOpen.value = false
  } catch (e: any) {
    showingError.value =
      e?.response?.data?.detail ?? "Ko'rsatuvni saqlab bo'lmadi. Ma'lumotlarni tekshiring."
  } finally {
    showingSaving.value = false
  }
}
</script>

<template>
  <div>
    <button class="btn btn-ghost btn-sm back" @click="goBack">
      <UiIcon name="i-arrow" :size="14" class="back-ic" />Obyektlarga qaytish
    </button>

    <div v-if="loading" class="grid" style="margin-top: 14px">
      <div class="sk" style="height: 340px; border-radius: var(--r-m); grid-column: 1 / -1" />
    </div>

    <EmptyState
      v-else-if="notFound || !property"
      title="Obyekt topilmadi"
      note="Bu obyekt o'chirilgan yoki mavjud emas bo'lishi mumkin."
    />

    <template v-else>
      <header class="dhead anim-rise">
        <div>
          <span class="eyebrow">Obyekt · ID {{ property.listing_id }}</span>
          <h1 class="h-disp">{{ property.title }}</h1>
          <p class="dim">{{ property.address }}</p>
        </div>
        <div class="stack">
          <button class="btn btn-pri btn-sm" @click="openShowing">
            <UiIcon name="i-calendar" :size="14" />Ko'rsatuv belgilash
          </button>
          <a :href="telHref(ownerPhone)" class="btn btn-ghost btn-sm" title="Uy egasiga qo'ng'iroq">
            <UiIcon name="i-phone" :size="14" />Qo'ng'iroq
          </a>
        </div>
      </header>

      <div class="detail-lg">
        <div class="detail-lg-main">
          <div class="gal gal-lg">
            <template v-if="property.photos.length">
              <img
                v-for="ph in property.photos.slice(0, 3)"
                :key="ph.id"
                :src="ph.image"
                class="gal-img"
                alt=""
              />
              <div v-if="property.photos.length < 3" class="ph" data-l="" />
              <div v-if="property.photos.length < 2" class="ph" data-l="" />
            </template>
            <template v-else>
              <div class="ph" data-l="FOTO YO'Q" />
              <div class="ph" data-l="" />
              <div class="ph" data-l="" />
            </template>
          </div>

          <h3 class="h-sec sec-t">Tavsif</h3>
          <p class="note">{{ property.description || 'Tavsif kiritilmagan.' }}</p>
          <p class="dim added mono">Qo'shilgan: {{ dateLabel(property.created_at) }}</p>
        </div>

        <div class="detail-lg-side">
          <div class="stack" style="margin-bottom: 14px">
            <span :class="statusPill(property.status)">{{ property.status }}</span>
            <span v-if="property.badge !== 'Oddiy'" :class="badgeClass(property.badge)">{{ property.badge }}</span>
            <span class="pill">{{ property.deal_type }}</span>
          </div>

          <div class="h-disp price-big">{{ property.price_label }}</div>

          <dl class="facts">
            <div><dt>Xonalar</dt><dd>{{ property.rooms }}</dd></div>
            <div><dt>Maydon</dt><dd>{{ property.area }} m²</dd></div>
            <div><dt>Qavat</dt><dd>{{ property.floor }} / {{ property.total_floors }}</dd></div>
            <div><dt>Qurilgan</dt><dd>{{ property.built_year ?? '—' }}</dd></div>
            <div><dt>Hudud</dt><dd>{{ property.district }}</dd></div>
            <div><dt>Ko'rishlar</dt><dd>{{ nf(property.views) }}</dd></div>
          </dl>

          <h3 class="h-sec sec-t">Uy egasi</h3>
          <div class="owner card">
            <span class="ava ava-sm"><UiIcon name="i-user" :size="15" /></span>
            <div>
              <b>{{ property.owner_name || 'Noma\'lum' }}</b>
              <small class="mono">{{ property.owner_phone || '—' }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- shu sahifa ichida boshqa obyektga o'tish -->
      <section v-if="others.length" class="others">
        <h3 class="h-sec sec-t">Boshqa obyektlar</h3>
        <div class="orow">
          <article
            v-for="o in others.filter((x) => x.id !== property!.id)"
            :key="o.id"
            class="ocard card"
            @click="goTo(o.id)"
          >
            <img v-if="o.cover" :src="o.cover" class="ocover" alt="" loading="lazy" />
            <div v-else class="ph ocover" data-l="" />
            <div class="obody">
              <div class="oprice">{{ o.price_label }}</div>
              <div class="oaddr">{{ o.address }}</div>
            </div>
          </article>
        </div>
      </section>
    </template>

    <!-- ==== ko'rsatuv belgilash ==== -->
    <ModalDialog
      :open="showingOpen"
      title="Ko'rsatuv belgilash"
      :subtitle="property ? `${property.title} · ${property.address}` : ''"
      @close="showingOpen = false"
    >
      <label class="fld">
        <span class="field-label">Mijoz</span>
        <span class="inp">
          <UiIcon name="i-user" :size="15" />
          <select v-model="form.client">
            <option value="">Mijozni tanlang…</option>
            <option v-for="c in clients" :key="c.id" :value="c.id">
              {{ c.name }} — {{ c.request }}
            </option>
          </select>
        </span>
      </label>

      <div class="two">
        <label class="fld">
          <span class="field-label">Sana</span>
          <span class="inp">
            <input v-model="form.date" type="date" :min="minDate" />
          </span>
        </label>
        <label class="fld">
          <span class="field-label">Vaqt</span>
          <span class="inp">
            <input v-model="form.time" type="time" />
          </span>
        </label>
      </div>

      <label class="fld">
        <span class="field-label">Izoh (ixtiyoriy)</span>
        <span class="inp">
          <input v-model="form.note" type="text" placeholder="Masalan: kadastr hujjatini olib borish" />
        </span>
      </label>

      <p class="hint">
        Uy egasi: <b>{{ property?.owner_name || '—' }}</b> · {{ ownerPhone }}
      </p>

      <Transition name="toast">
        <p v-if="showingError" class="err"><UiIcon name="i-x" :size="14" />{{ showingError }}</p>
      </Transition>

      <template #footer>
        <button class="btn btn-pri" style="flex: 1" :disabled="showingSaving" @click="saveShowing">
          <span v-if="showingSaving" class="spinner" />
          <template v-else><UiIcon name="i-check" :size="15" />Saqlash</template>
        </button>
        <button class="btn btn-ghost" @click="showingOpen = false">Bekor</button>
      </template>
    </ModalDialog>
  </div>
</template>

<style scoped>
.back {
  margin-bottom: 14px;
}
.back-ic {
  transform: rotate(180deg);
}

.dhead {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.dhead h1 {
  font-size: 22px;
  margin-top: 4px;
}
.dhead p {
  font-size: 12.5px;
  color: var(--text-3);
  margin-top: 3px;
}

.detail-lg {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 28px;
  align-items: start;
}
.detail-lg-side {
  position: sticky;
  top: 14px;
}
@media (max-width: 760px) {
  .detail-lg {
    grid-template-columns: 1fr;
  }
  .detail-lg-side {
    position: static;
  }
}

.gal-lg {
  grid-template-rows: 200px 200px;
}
.gal {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 8px;
  margin-bottom: 8px;
}
.gal .ph:first-child,
.gal .gal-img:first-child {
  grid-row: span 2;
}
.gal-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--r-m);
  display: block;
}

.price-big {
  font-size: 30px;
  margin-bottom: 14px;
}
.facts {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1px;
  background: var(--line-soft);
  border: 1px solid var(--line-soft);
  border-radius: var(--r-m);
  overflow: hidden;
}
.facts > div {
  background: var(--surface);
  padding: 11px;
}
.facts dt {
  font-size: 10.5px;
  color: var(--text-3);
  margin-bottom: 3px;
}
.facts dd {
  font-size: 13px;
  font-weight: 700;
}
.sec-t {
  margin: 20px 0 10px;
}
.owner {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 12px;
}
.owner b {
  display: block;
  font-size: 13px;
}
.owner small {
  font-size: 11px;
  color: var(--text-3);
}
.note {
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.65;
}
.added {
  font-size: 10.5px;
  margin-top: 14px;
}

/* ---- boshqa obyektlar ---- */
.others {
  margin-top: 34px;
  border-top: 1px solid var(--line-soft);
  padding-top: 6px;
}
.orow {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 6px;
}
.ocard {
  flex: none;
  width: 190px;
  cursor: pointer;
  overflow: hidden;
  transition:
    transform var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out);
}
.ocard:hover {
  transform: translateY(-2px);
  border-color: var(--teal);
}
.ocover {
  width: 100%;
  height: 104px;
  object-fit: cover;
  display: block;
  border-radius: 0;
}
.obody {
  padding: 9px 10px 10px;
}
.oprice {
  font-family: var(--f-display);
  font-size: 14px;
  font-weight: 800;
}
.oaddr {
  font-size: 11px;
  color: var(--text-3);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ---- ko'rsatuv formasi ---- */
.fld {
  display: block;
  margin-bottom: 13px;
}
.two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.hint {
  font-size: 11.5px;
  color: var(--text-3);
  padding: 10px 11px;
  border-radius: 9px;
  background: var(--surface-2);
}
.hint b {
  color: var(--text-2);
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
  margin-top: 12px;
}
</style>
