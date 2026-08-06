<script setup lang="ts">
/**
 * Bitim tafsiloti — alohida sahifa (avval oddiy kichkina panel edi).
 * Endi bosqichni boshqarish, izohni tahrirlash, shartnomani belgilash va
 * bitimni bekor qilish mumkin; pastda boshqa bitimlarga sahifa ichida o'tish bor.
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api from '@/api/client'
import EmptyState from '@/components/EmptyState.vue'
import UiIcon from '@/components/UiIcon.vue'
import { dateLabel, money, nf } from '@/lib/format'
import { toast } from '@/stores/toast'
import type { Deal, Paginated } from '@/types'

const STAGES = [
  { key: "Ko'rsatuv", tone: 'teal', icon: 'i-calendar' },
  { key: 'Kelishuv', tone: 'label', icon: 'i-chat' },
  { key: 'Shartnoma', tone: 'brass', icon: 'i-doc' },
  { key: 'Yopilgan', tone: 'deep', icon: 'i-check' },
]

const route = useRoute()
const router = useRouter()

const deal = ref<Deal | null>(null)
const loading = ref(true)
const notFound = ref(false)
const busy = ref(false)

const others = ref<Deal[]>([])

const noteDraft = ref('')
const noteDirty = ref(false)
const noteSaving = ref(false)

async function loadDeal(id: string | string[]) {
  loading.value = true
  notFound.value = false
  try {
    const { data } = await api.get<Deal>(`/deals/${id}/`)
    deal.value = data
    noteDraft.value = data.note || ''
    noteDirty.value = false
  } catch {
    notFound.value = true
    deal.value = null
  } finally {
    loading.value = false
  }
}

async function loadOthers() {
  try {
    const { data } = await api.get<Paginated<Deal>>('/deals/', { params: { page_size: 16 } })
    others.value = data.results
  } catch {
    // Panel ixtiyoriy — xato bo'lsa sahifaning asosiy qismi ishlashda davom etadi.
  }
}

function goTo(id: number) {
  if (deal.value?.id === id) return
  router.push({ name: 'deal-detail', params: { id } })
}

function goBack() {
  router.push({ name: 'deals' })
}

watch(
  () => route.params.id,
  (id) => {
    if (id) loadDeal(id)
  },
  { immediate: true },
)

loadOthers()

function isLast(stage: string) {
  return stage === STAGES[STAGES.length - 1].key
}
function isFirst(stage: string) {
  return stage === STAGES[0].key
}
function isCancelled(stage: string) {
  return stage === 'Bekor qilingan'
}
const stageIndex = computed(() =>
  deal.value ? STAGES.findIndex((s) => s.key === deal.value!.stage) : -1,
)

async function patchDeal(payload: Partial<Deal>, okMsg?: string) {
  if (!deal.value) return
  busy.value = true
  try {
    const { data } = await api.patch<Deal>(`/deals/${deal.value.id}/`, payload)
    deal.value = data
    if (!noteDirty.value) noteDraft.value = data.note || ''
    if (okMsg) toast.ok(okMsg)
  } catch {
    toast.err("Bitimni yangilab bo'lmadi")
  } finally {
    busy.value = false
  }
}

function advance(direction: 1 | -1) {
  if (!deal.value) return
  const order = STAGES.map((s) => s.key)
  const next = order[stageIndex.value + direction]
  if (!next) return
  patchDeal({ stage: next }, `Bosqich → ${next}`)
}

function cancelDeal() {
  if (!deal.value || isCancelled(deal.value.stage)) return
  patchDeal({ stage: 'Bekor qilingan' }, 'Bitim bekor qilindi')
}

function toggleContract() {
  if (!deal.value) return
  patchDeal(
    { contract_signed: !deal.value.contract_signed },
    deal.value.contract_signed ? 'Shartnoma belgisi olib tashlandi' : 'Shartnoma imzolangan deb belgilandi',
  )
}

async function saveNote() {
  if (!deal.value) return
  noteSaving.value = true
  try {
    const { data } = await api.patch<Deal>(`/deals/${deal.value.id}/`, { note: noteDraft.value })
    deal.value = data
    noteDirty.value = false
    toast.ok('Izoh saqlandi')
  } catch {
    toast.err("Izohni saqlab bo'lmadi")
  } finally {
    noteSaving.value = false
  }
}
</script>

<template>
  <div>
    <button class="btn btn-ghost btn-sm back" @click="goBack">
      <UiIcon name="i-arrow" :size="14" class="back-ic" />Bitimlarga qaytish
    </button>

    <div v-if="loading" class="grid" style="margin-top: 14px">
      <div class="sk" style="height: 340px; border-radius: var(--r-m); grid-column: 1 / -1" />
    </div>

    <EmptyState
      v-else-if="notFound || !deal"
      title="Bitim topilmadi"
      note="Bu bitim o'chirilgan yoki mavjud emas bo'lishi mumkin."
    />

    <template v-else>
      <header class="dhead anim-rise">
        <div>
          <span class="eyebrow">Bitim · #{{ deal.id }}</span>
          <h1 class="h-disp">{{ deal.client_name }}</h1>
          <p class="dim">
            <span class="pill" :class="{ 'pill-ok': deal.stage === 'Yopilgan', 'pill-hot': isCancelled(deal.stage) }">
              {{ deal.stage }}
            </span>
            <span v-if="deal.contract_signed" class="pill pill-ok" style="margin-left: 6px">
              <UiIcon name="i-check" :size="10" />imzolangan
            </span>
          </p>
        </div>
        <div class="stack">
          <button
            class="btn btn-ghost btn-sm"
            :disabled="isFirst(deal.stage) || isCancelled(deal.stage) || busy"
            @click="advance(-1)"
          >
            ← Orqaga
          </button>
          <button
            v-if="!isLast(deal.stage) && !isCancelled(deal.stage)"
            class="btn btn-pri btn-sm"
            :disabled="busy"
            @click="advance(1)"
          >
            Keyingi bosqich →
          </button>
          <button
            v-if="!isCancelled(deal.stage) && !isLast(deal.stage)"
            class="btn btn-ghost btn-sm danger"
            :disabled="busy"
            @click="cancelDeal"
          >
            <UiIcon name="i-x" :size="14" />Bekor qilish
          </button>
        </div>
      </header>

      <div class="detail-lg">
        <div class="detail-lg-main">
          <h3 class="h-sec sec-t" style="margin-top: 0">Bosqich</h3>
          <ul class="steps">
            <li v-for="(s, i) in STAGES" :key="s.key" :class="{ done: stageIndex >= i, cur: stageIndex === i }">
              <i /><span>{{ s.key }}</span>
            </li>
          </ul>
          <p v-if="isCancelled(deal.stage)" class="err" style="margin-top: 10px">
            <UiIcon name="i-x" :size="14" />Bu bitim bekor qilingan
          </p>

          <h3 class="h-sec sec-t">Obyekt</h3>
          <div v-if="deal.listing" class="card card-pad obj-card">
            <div>
              <b>{{ deal.listing_title || '—' }}</b>
              <p class="dim mono" style="margin-top: 3px">{{ deal.listing_address || '—' }} · ID {{ deal.listing_code }}</p>
            </div>
            <RouterLink :to="{ name: 'property-detail', params: { id: deal.listing } }" class="btn btn-ghost btn-sm">
              Obyektni ko'rish
            </RouterLink>
          </div>
          <p v-else class="dim" style="font-size: 12.5px">Obyekt biriktirilmagan.</p>

          <h3 class="h-sec sec-t">Izoh</h3>
          <textarea
            v-model="noteDraft"
            class="note-area"
            rows="4"
            placeholder="Bitim haqida izoh qoldiring…"
            @input="noteDirty = true"
          />
          <div class="stack" style="margin-top: 8px">
            <button class="btn btn-pri btn-sm" :disabled="!noteDirty || noteSaving" @click="saveNote">
              <span v-if="noteSaving" class="spinner" />
              <template v-else><UiIcon name="i-check" :size="14" />Izohni saqlash</template>
            </button>
            <span v-if="noteDirty" class="dim" style="font-size: 11px">saqlanmagan o'zgarish bor</span>
          </div>

          <p class="mono dim added">Ochilgan: {{ dateLabel(deal.created_at) }}</p>
          <p v-if="deal.closed_at" class="mono dim added" style="margin-top: 2px">
            Yopilgan: {{ dateLabel(deal.closed_at) }}
          </p>
        </div>

        <div class="detail-lg-side">
          <div class="h-disp price-big">{{ money(deal.amount, deal.currency) }}</div>

          <h3 class="h-sec sec-t" style="margin-top: 0">Komissiya taqsimoti</h3>
          <div class="split card">
            <div><span>Umumiy komissiya</span><b>{{ nf(deal.commission) }} so'm</b></div>
            <div><span>Platforma ulushi</span><b class="brass">−{{ nf(deal.platform_cut) }} so'm</b></div>
            <div class="net-row"><span>Sizning daromadingiz</span><b class="teal">{{ nf(deal.agent_net) }} so'm</b></div>
          </div>

          <h3 class="h-sec sec-t">Shartnoma</h3>
          <button class="btn btn-ghost" style="width: 100%" :disabled="busy" @click="toggleContract">
            <UiIcon :name="deal.contract_signed ? 'i-check' : 'i-doc'" :size="15" />
            {{ deal.contract_signed ? 'Imzolangan deb belgilangan' : "Imzolangan deb belgilash" }}
          </button>
        </div>
      </div>

      <!-- shu sahifa ichida boshqa bitimga o'tish -->
      <section v-if="others.length" class="others">
        <h3 class="h-sec sec-t">Boshqa bitimlar</h3>
        <div class="orow">
          <article
            v-for="o in others.filter((x) => x.id !== deal!.id)"
            :key="o.id"
            class="ocard card"
            @click="goTo(o.id)"
          >
            <div class="obody">
              <div class="otop">
                <b>{{ o.client_name }}</b>
                <span class="pill tiny-pill" :class="{ 'pill-ok': o.stage === 'Yopilgan', 'pill-hot': o.stage === 'Bekor qilingan' }">
                  {{ o.stage }}
                </span>
              </div>
              <p class="dim mono" style="margin-top: 4px">{{ money(o.amount, o.currency) }}</p>
            </div>
          </article>
        </div>
      </section>
    </template>
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
  margin-top: 8px;
}
.danger {
  color: var(--rose);
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

.sec-t {
  margin: 20px 0 10px;
}
.price-big {
  font-size: 28px;
  margin-bottom: 4px;
}

.steps {
  list-style: none;
  display: grid;
  gap: 0;
}
.steps li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-3);
  padding: 7px 0;
  position: relative;
}
.steps li i {
  width: 13px;
  height: 13px;
  border-radius: 50%;
  border: 2px solid var(--line);
  flex: none;
  transition:
    background-color var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out);
}
.steps li.done {
  color: var(--text);
}
.steps li.done i {
  background: var(--teal);
  border-color: var(--teal);
}
.steps li.cur span {
  font-weight: 700;
}
.steps li + li::before {
  content: '';
  position: absolute;
  left: 6px;
  top: -8px;
  width: 1px;
  height: 16px;
  background: var(--line);
}

.obj-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.note-area {
  width: 100%;
  resize: vertical;
  min-height: 78px;
  padding: 10px 12px;
  font: inherit;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--text);
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: var(--r-m);
}
.note-area:focus {
  outline: none;
  border-color: var(--teal);
}

.added {
  font-size: 10.5px;
  margin-top: 12px;
}

.split > div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 13px;
  font-size: 12.5px;
  color: var(--text-2);
}
.split > div + div {
  border-top: 1px solid var(--line-soft);
}
.split b {
  color: var(--text);
}
.split .brass {
  color: var(--brass);
}
.split .teal {
  color: var(--teal);
}
.net-row {
  background: var(--teal-glow);
}

/* ---- boshqa bitimlar ---- */
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
  width: 200px;
  cursor: pointer;
  padding: 12px;
  transition:
    transform var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out);
}
.ocard:hover {
  transform: translateY(-2px);
  border-color: var(--teal);
}
.otop {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.otop b {
  font-size: 12.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tiny-pill {
  font-size: 9px;
  padding: 2px 6px;
  flex: none;
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
}
</style>
