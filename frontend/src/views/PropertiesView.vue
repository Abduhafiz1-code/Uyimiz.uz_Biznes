<script setup lang="ts">
/**
 * Obyektlar — Figmada CRM uchun freym yo'q edi.
 * 02/03-freymlardagi e'lon kartasi (.lcard: foto + narx + manzil + meta qatori)
 * agent portfeliga moslashtirildi: holat, ko'rish soni va egasi qo'shildi.
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import api from '@/api/client'
import EmptyState from '@/components/EmptyState.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import PageHead from '@/components/PageHead.vue'
import UiIcon from '@/components/UiIcon.vue'
import { nf, statusPill } from '@/lib/format'
import { toast } from '@/stores/toast'
import type { Paginated, Property } from '@/types'

const router = useRouter()

const STATUSES = ['Faol', 'Band', 'Sotilgan', 'Arxiv']
const TYPES = ['Sotib olish', 'Ijara', 'Kunlik']

const rows = ref<Property[]>([])
const count = ref(0)
const page = ref(1)
const loading = ref(true)
const search = ref('')
const status = ref('')
const dealType = ref('')

const pages = computed(() => Math.max(Math.ceil(count.value / 12), 1))

const summary = computed(() => {
  const active = rows.value.filter((r) => r.status === 'Faol').length
  const views = rows.value.reduce((s, r) => s + r.views, 0)
  return { active, views }
})

let debounce = 0
watch([search, status, dealType], () => {
  window.clearTimeout(debounce)
  debounce = window.setTimeout(() => {
    page.value = 1
    load()
  }, 280)
})
watch(page, load)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get<Paginated<Property>>('/properties/', {
      params: {
        page: page.value,
        search: search.value || undefined,
        status: status.value || undefined,
        deal_type: dealType.value || undefined,
      },
    })
    rows.value = data.results
    count.value = data.count
  } catch {
    toast.err("Obyektlarni yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

function badgeClass(b: string) {
  if (b === 'VIP') return 'pill pill-vip'
  if (b === 'Premium') return 'pill pill-ok'
  return 'pill'
}

/** Bosilganda obyektning alohida sahifasiga o'tadi. */
function openDetail(p: Property) {
  router.push({ name: 'property-detail', params: { id: p.id } })
}

/* ---------- yangi obyekt qo'shish ---------- */

const addOpen = ref(false)
const addSaving = ref(false)
const addError = ref('')
const blank = () => ({
  title: '',
  district: 'Chilonzor',
  address: '',
  deal_type: 'Sotib olish',
  price: '',
  currency: 'USD',
  rooms: 2,
  area: '',
  floor: 1,
  total_floors: 1,
  owner_name: '',
  owner_phone: '',
})
const addForm = ref(blank())

/* --- rasm tanlash --- */
interface Pick {
  file: File
  url: string
}
const picks = ref<Pick[]>([])
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

function addFiles(list: FileList | null) {
  if (!list) return
  for (const f of Array.from(list)) {
    if (!f.type.startsWith('image/')) continue
    if (f.size > 8 * 1024 * 1024) {
      addError.value = `${f.name} — 8 MB dan katta, o'tkazib yuborildi`
      continue
    }
    picks.value.push({ file: f, url: URL.createObjectURL(f) })
  }
  if (fileInput.value) fileInput.value.value = ''
}

function removePick(i: number) {
  URL.revokeObjectURL(picks.value[i].url)
  picks.value.splice(i, 1)
}

function clearPicks() {
  picks.value.forEach((p) => URL.revokeObjectURL(p.url))
  picks.value = []
}

function openAdd() {
  addError.value = ''
  addForm.value = blank()
  clearPicks()
  addOpen.value = true
}

/** Mavjud eng katta e'lon raqamidan keyingisini beradi. */
function nextListingId() {
  const nums = rows.value.map((r) => Number(r.listing_id)).filter((n) => Number.isFinite(n))
  return String((nums.length ? Math.max(...nums) : 40000) + 1)
}

async function saveProperty() {
  const f = addForm.value
  if (!f.title.trim() || !f.address.trim() || !f.price || !f.area) {
    addError.value = "Sarlavha, manzil, narx va maydon to'ldirilishi shart"
    return
  }
  addSaving.value = true
  addError.value = ''
  try {
    // 1) obyektni yaratamiz
    const { data: created } = await api.post<Property>('/properties/', {
      ...f,
      listing_id: nextListingId(),
      price: Number(f.price),
      area: Number(f.area),
      rooms: Number(f.rooms),
      floor: Number(f.floor),
      total_floors: Number(f.total_floors),
      status: 'Faol',
      badge: 'Oddiy',
    })

    // 2) tanlangan rasmlarni yuklaymiz
    if (picks.value.length) {
      const fd = new FormData()
      picks.value.forEach((p) => fd.append('images', p.file))
      try {
        await api.post(`/properties/${created.id}/photos/`, fd)
      } catch {
        toast.err("Obyekt saqlandi, lekin rasmlarni yuklab bo'lmadi")
      }
    }

    toast.ok(`Obyekt qo'shildi — ${f.title}`)
    addOpen.value = false
    clearPicks()
    page.value = 1
    await load()
  } catch (e: any) {
    const d = e?.response?.data
    addError.value =
      typeof d === 'object' && d ? Object.values(d).flat().join(' · ') : "Obyektni saqlab bo'lmadi"
  } finally {
    addSaving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <PageHead
      title="Obyektlar"
      :note="`${count} ta e'lon portfelingizda · ${summary.active} tasi faol`"
      eyebrow="Portfel"
    >
      <span class="pill mono"><UiIcon name="i-trend" :size="12" />{{ nf(summary.views) }} ko'rish</span>
      <button class="btn btn-pri btn-sm" @click="openAdd">
        <UiIcon name="i-plus" :size="14" />Obyekt qo'shish
      </button>
    </PageHead>

    <section class="filters card anim-rise">
      <label class="inp grow">
        <UiIcon name="i-search" :size="15" />
        <input v-model="search" type="search" placeholder="Manzil, sarlavha yoki e'lon ID…" />
      </label>
      <label class="inp">
        <UiIcon name="i-filter" :size="15" />
        <select v-model="status">
          <option value="">Barcha holat</option>
          <option v-for="s in STATUSES" :key="s" :value="s">{{ s }}</option>
        </select>
      </label>
      <label class="inp">
        <UiIcon name="i-doc" :size="15" />
        <select v-model="dealType">
          <option value="">Barcha turi</option>
          <option v-for="t in TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
      </label>
    </section>

    <!-- yuklanish -->
    <div v-if="loading" class="grid">
      <div v-for="i in 6" :key="i" class="sk" style="height: 264px; border-radius: var(--r-m)" />
    </div>

    <EmptyState
      v-else-if="!rows.length"
      title="Obyekt topilmadi"
      note="Portfelingizga yangi e'lon qo'shing yoki filtrlarni kengaytiring."
    />

    <!-- e'lon kartalari -->
    <TransitionGroup v-else tag="div" name="list" class="grid stagger">
      <article v-for="p in rows" :key="p.id" class="lcard card" @click="openDetail(p)">
        <div class="rel">
          <div class="badges">
            <span v-if="p.badge !== 'Oddiy'" :class="badgeClass(p.badge)">{{ p.badge }}</span>
            <span v-if="p.is_verified" class="pill pill-ok">
              <UiIcon name="i-shield" :size="11" />Tasdiqlangan
            </span>
          </div>
          <img v-if="p.cover" :src="p.cover" class="cover" alt="" loading="lazy" />
          <div v-else class="ph" :data-l="`${p.photo_count} foto`" />
          <span class="st" :class="statusPill(p.status)">{{ p.status }}</span>
        </div>

        <div class="body">
          <div class="price">{{ p.price_label }}<small v-if="p.deal_type === 'Ijara'"> /oy</small></div>
          <div class="addr">{{ p.address }}</div>
          <div class="meta">
            <span><UiIcon name="i-bed" :size="13" />{{ p.rooms }} xona</span>
            <span><UiIcon name="i-sq" :size="13" />{{ p.area }} m²</span>
            <span>{{ p.floor }}/{{ p.total_floors }}</span>
          </div>
          <div class="foot">
            <span class="mono">ID {{ p.listing_id }}</span>
            <span class="mono"><UiIcon name="i-trend" :size="12" />{{ nf(p.views) }}</span>
          </div>
        </div>
      </article>
    </TransitionGroup>

    <footer v-if="!loading && rows.length" class="pager">
      <span class="dim mono">{{ count }} ta obyekt · {{ page }}/{{ pages }}-sahifa</span>
      <div class="stack">
        <button class="btn btn-ghost btn-sm" :disabled="page <= 1" @click="page--">Oldingi</button>
        <button class="btn btn-ghost btn-sm" :disabled="page >= pages" @click="page++">Keyingi</button>
      </div>
    </footer>

    <!-- ==== yangi obyekt ==== -->
    <ModalDialog
      :open="addOpen"
      title="Yangi obyekt"
      subtitle="Portfelingizga e'lon qo'shiladi"
      @close="addOpen = false"
    >
      <!-- Barcha maydonlar bitta ustunda, qatorma-qator: forma faqat pastga suriladi. -->
      <div class="form">
        <!-- rasmlar -->
        <div class="fld">
          <span class="field-label">Rasmlar</span>
          <div
            class="drop"
            :class="{ over: dragOver }"
            @click="fileInput?.click()"
            @dragover.prevent="dragOver = true"
            @dragleave.prevent="dragOver = false"
            @drop.prevent="((dragOver = false), addFiles($event.dataTransfer?.files ?? null))"
          >
            <UiIcon name="i-camera" :size="20" />
            <b>Rasm yuklash</b>
            <small>Bosing yoki bu yerga tashlang · JPG, PNG · 8 MB gacha</small>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            multiple
            class="sr-only"
            @change="addFiles(($event.target as HTMLInputElement).files)"
          />

          <TransitionGroup v-if="picks.length" tag="div" name="list" class="thumbs">
            <div v-for="(p, i) in picks" :key="p.url" class="thumb">
              <img :src="p.url" alt="" />
              <button type="button" aria-label="O'chirish" @click.stop="removePick(i)">
                <UiIcon name="i-x" :size="12" />
              </button>
              <span v-if="i === 0" class="cover-tag">Asosiy</span>
            </div>
          </TransitionGroup>
          <p v-if="picks.length" class="cnt mono">{{ picks.length }} ta rasm tanlandi</p>
        </div>

        <label class="fld">
          <span class="field-label">Sarlavha</span>
          <span class="inp">
            <input v-model="addForm.title" type="text" placeholder="3 xonali kvartira" />
          </span>
        </label>

        <label class="fld">
          <span class="field-label">Manzil</span>
          <span class="inp">
            <UiIcon name="i-pin" :size="15" />
            <input v-model="addForm.address" type="text" placeholder="Chilonzor 11-kvartal" />
          </span>
        </label>

        <label class="fld">
          <span class="field-label">Hudud</span>
          <span class="inp"><input v-model="addForm.district" type="text" placeholder="Chilonzor" /></span>
        </label>

        <label class="fld">
          <span class="field-label">Bitim turi</span>
          <span class="inp">
            <UiIcon name="i-doc" :size="15" />
            <select v-model="addForm.deal_type">
              <option v-for="t in TYPES" :key="t" :value="t">{{ t }}</option>
            </select>
          </span>
        </label>

        <label class="fld">
          <span class="field-label">Narx</span>
          <span class="inp">
            <input v-model="addForm.price" type="number" min="0" placeholder="54000" />
            <span class="seg">
              <button
                type="button"
                :class="{ on: addForm.currency === 'USD' }"
                @click.prevent="addForm.currency = 'USD'"
              >
                $
              </button>
              <button
                type="button"
                :class="{ on: addForm.currency === 'UZS' }"
                @click.prevent="addForm.currency = 'UZS'"
              >
                so'm
              </button>
            </span>
          </span>
        </label>

        <label class="fld">
          <span class="field-label">Xonalar soni</span>
          <span class="inp">
            <UiIcon name="i-bed" :size="15" />
            <input v-model="addForm.rooms" type="number" min="1" />
          </span>
        </label>

        <label class="fld">
          <span class="field-label">Maydon, m²</span>
          <span class="inp">
            <UiIcon name="i-sq" :size="15" />
            <input v-model="addForm.area" type="number" min="1" step="0.1" placeholder="72" />
          </span>
        </label>

        <label class="fld">
          <span class="field-label">Qavat</span>
          <span class="inp"><input v-model="addForm.floor" type="number" min="1" /></span>
        </label>

        <label class="fld">
          <span class="field-label">Binoning qavatlari</span>
          <span class="inp"><input v-model="addForm.total_floors" type="number" min="1" /></span>
        </label>

        <label class="fld">
          <span class="field-label">Uy egasi</span>
          <span class="inp">
            <UiIcon name="i-user" :size="15" />
            <input v-model="addForm.owner_name" type="text" placeholder="Dilshod A." />
          </span>
        </label>

        <label class="fld">
          <span class="field-label">Egasining raqami</span>
          <span class="inp">
            <UiIcon name="i-phone" :size="15" />
            <input v-model="addForm.owner_phone" type="tel" placeholder="+998 90 123 45 67" />
          </span>
        </label>
      </div>

      <Transition name="toast">
        <p v-if="addError" class="err"><UiIcon name="i-x" :size="14" />{{ addError }}</p>
      </Transition>

      <template #footer>
        <button class="btn btn-pri" style="flex: 1" :disabled="addSaving" @click="saveProperty">
          <span v-if="addSaving" class="spinner" />
          <template v-else><UiIcon name="i-plus" :size="15" />Qo'shish</template>
        </button>
        <button class="btn btn-ghost" @click="addOpen = false">Bekor</button>
      </template>
    </ModalDialog>
  </div>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 9px;
  padding: 11px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.grow {
  flex: 1;
  min-width: 190px;
}
.filters .inp {
  padding: 9px 12px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(232px, 1fr));
  gap: 14px;
}

.lcard {
  overflow: hidden;
  cursor: pointer;
  transition:
    transform var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out),
    box-shadow var(--dur-2) var(--ease-out);
}
.lcard:hover {
  transform: translateY(-4px);
  border-color: var(--teal);
  box-shadow: var(--shadow-card);
}
.rel {
  position: relative;
}
.rel .ph,
.rel .cover {
  height: 146px;
  border-radius: 0;
}
.rel .cover {
  display: block;
  width: 100%;
  object-fit: cover;
  transition: transform var(--dur-3) var(--ease-out);
}
.lcard:hover .ph {
  filter: brightness(1.06);
}
.lcard:hover .cover {
  transform: scale(1.04);
}
.badges {
  position: absolute;
  top: 9px;
  left: 9px;
  z-index: 2;
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}
.badges .pill {
  backdrop-filter: blur(6px);
}
.st {
  position: absolute;
  right: 9px;
  bottom: 9px;
  z-index: 2;
  backdrop-filter: blur(6px);
}

.body {
  padding: 13px 14px 12px;
}
.price {
  font-family: var(--f-display);
  font-size: 19px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.price small {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-3);
}
.addr {
  font-size: 12.5px;
  color: var(--text-2);
  margin: 4px 0 9px;
}
.meta {
  display: flex;
  gap: 11px;
  font-size: 11.5px;
  color: var(--text-3);
  border-top: 1px solid var(--line-soft);
  padding-top: 9px;
}
.meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.foot {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text-3);
  margin-top: 9px;
}
.foot span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 18px;
  font-size: 11.5px;
  flex-wrap: wrap;
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
/* Yangi obyekt formasi — bitta ustun, hamma maydon to'liq kenglikda. */
.form {
  display: grid;
  gap: 13px;
}
.form .fld {
  margin-bottom: 0;
  min-width: 0;
}
.form .inp {
  width: 100%;
}
.form .inp input,
.form .inp select {
  width: 100%;
  min-width: 0;
}

/* narx yonidagi valyuta tanlagichi */
.seg {
  display: inline-flex;
  gap: 2px;
  flex: none;
  padding: 2px;
  border-radius: 7px;
  background: var(--frame);
  border: 1px solid var(--line);
}
.seg button {
  border: 0;
  background: none;
  font-family: inherit;
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-3);
  padding: 4px 9px;
  border-radius: 5px;
  cursor: pointer;
  transition:
    background-color var(--dur-1) var(--ease-out),
    color var(--dur-1) var(--ease-out);
}
.seg button.on {
  background: var(--teal);
  color: var(--on-teal);
}

/* rasm yuklash */
.drop {
  display: grid;
  place-items: center;
  gap: 3px;
  padding: 20px 14px;
  border: 1.5px dashed var(--line);
  border-radius: var(--r-m);
  background: var(--surface-2);
  color: var(--text-3);
  cursor: pointer;
  text-align: center;
  transition:
    border-color var(--dur-1) var(--ease-out),
    background-color var(--dur-1) var(--ease-out),
    color var(--dur-1) var(--ease-out);
}
.drop:hover,
.drop.over {
  border-color: var(--teal);
  background: var(--teal-glow);
  color: var(--teal);
}
.drop b {
  font-size: 13px;
  color: var(--text);
}
.drop small {
  font-size: 10.5px;
  color: var(--text-3);
}

.thumbs {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(72px, 1fr));
  gap: 8px;
  margin-top: 10px;
}
.thumb {
  position: relative;
  aspect-ratio: 4 / 3;
  border-radius: 9px;
  overflow: hidden;
  border: 1px solid var(--line);
  background: var(--surface-2);
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.thumb button {
  position: absolute;
  top: 4px;
  right: 4px;
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
  border: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.65);
  color: #fff;
  cursor: pointer;
}
.thumb button:hover {
  background: var(--rose);
}
.cover-tag {
  position: absolute;
  left: 4px;
  bottom: 4px;
  font-family: var(--f-mono);
  font-size: 8.5px;
  padding: 2px 5px;
  border-radius: 4px;
  background: var(--teal);
  color: var(--on-teal);
}
.cnt {
  font-size: 10.5px;
  color: var(--text-3);
  margin-top: 7px;
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
