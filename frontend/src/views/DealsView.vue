<script setup lang="ts">
/**
 * Bitimlar — Figmada freym yo'q edi.
 * 09-freymdagi oqim diagrammasi (fnode/farrow) voronka ustunlariga aylantirildi:
 * har bir bosqich ustun, kartani keyingi bosqichga surish mumkin.
 */
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '@/api/client'
import DonutChart from '@/components/DonutChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import PageHead from '@/components/PageHead.vue'
import UiIcon from '@/components/UiIcon.vue'
import { compactSum, dateLabel, money, nf } from '@/lib/format'
import { toast } from '@/stores/toast'
import type { Deal, Paginated } from '@/types'

const router = useRouter()

const STAGES = [
  { key: "Ko'rsatuv", tone: 'teal', icon: 'i-calendar' },
  { key: 'Kelishuv', tone: 'label', icon: 'i-chat' },
  { key: 'Shartnoma', tone: 'brass', icon: 'i-doc' },
  { key: 'Yopilgan', tone: 'deep', icon: 'i-check' },
]

const rows = ref<Deal[]>([])
const loading = ref(true)
const moving = ref<number | null>(null)
const view = ref<'board' | 'table'>('board')

const byStage = computed(() =>
  STAGES.map((s) => ({
    ...s,
    items: rows.value.filter((d) => d.stage === s.key),
  })),
)

const cancelled = computed(() => rows.value.filter((d) => d.stage === 'Bekor qilingan'))

const totals = computed(() => {
  const closed = rows.value.filter((d) => d.stage === 'Yopilgan')
  const open = rows.value.filter((d) => !['Yopilgan', 'Bekor qilingan'].includes(d.stage))
  return {
    closed: closed.length,
    open: open.length,
    earned: closed.reduce((s, d) => s + Number(d.commission), 0),
    pending: open.reduce((s, d) => s + Number(d.commission), 0),
    platform: closed.reduce((s, d) => s + Number(d.platform_cut), 0),
  }
})

const donut = computed(() =>
  byStage.value.map((s) => ({
    label: s.key,
    value: s.items.length,
    color:
      s.tone === 'teal'
        ? 'var(--teal)'
        : s.tone === 'label'
          ? 'var(--label)'
          : s.tone === 'brass'
            ? 'var(--brass)'
            : 'var(--teal-deep)',
  })),
)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get<Paginated<Deal>>('/deals/', { params: { page_size: 100 } })
    rows.value = data.results
  } catch {
    toast.err("Bitimlarni yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

/** Kartani voronkaning keyingi bosqichiga suradi. */
async function advance(deal: Deal, direction: 1 | -1) {
  const order = STAGES.map((s) => s.key)
  const i = order.indexOf(deal.stage)
  const next = order[i + direction]
  if (!next) return

  moving.value = deal.id
  try {
    const { data } = await api.patch<Deal>(`/deals/${deal.id}/`, { stage: next })
    const idx = rows.value.findIndex((d) => d.id === deal.id)
    if (idx !== -1) rows.value[idx] = data
    toast.ok(`${data.client_name} → ${next}`)
  } catch {
    toast.err("Bosqichni o'zgartirib bo'lmadi")
  } finally {
    moving.value = null
  }
}

function isLast(stage: string) {
  return stage === STAGES[STAGES.length - 1].key
}
function isFirst(stage: string) {
  return stage === STAGES[0].key
}

/** Bosilganda bitimning alohida sahifasiga o'tadi. */
function openDetail(d: Deal) {
  router.push({ name: 'deal-detail', params: { id: d.id } })
}

onMounted(load)
</script>

<template>
  <div>
    <PageHead title="Bitimlar" note="Voronka bo'ylab har bir bitimning holati" eyebrow="Pipeline">
      <div class="switch">
        <button :class="{ on: view === 'board' }" @click="view = 'board'">Voronka</button>
        <button :class="{ on: view === 'table' }" @click="view = 'table'">Jadval</button>
      </div>
    </PageHead>

    <!-- yig'ma ko'rsatkichlar -->
    <section class="tops stagger">
      <div class="card card-pad t-card">
        <span class="lbl">Yopilgan bitimlar</span>
        <b>{{ totals.closed }}</b>
        <small class="dim">jami {{ rows.length }} tadan</small>
      </div>
      <div class="card card-pad t-card">
        <span class="lbl">Ochiq bitimlar</span>
        <b>{{ totals.open }}</b>
        <small class="dim">voronkada harakatda</small>
      </div>
      <div class="card card-pad t-card teal">
        <span class="lbl">Olingan komissiya</span>
        <b>{{ compactSum(totals.earned).value }} <i>{{ compactSum(totals.earned).unit }}</i></b>
        <small class="dim">platformaga {{ nf(totals.platform) }} so'm</small>
      </div>
      <div class="card card-pad t-card brass">
        <span class="lbl">Kutilayotgan komissiya</span>
        <b>{{ compactSum(totals.pending).value }} <i>{{ compactSum(totals.pending).unit }}</i></b>
        <small class="dim">ochiq bitimlardan</small>
      </div>
      <div class="card card-pad donut-card">
        <DonutChart :slices="donut" :center-value="rows.length" center-label="bitim" />
      </div>
    </section>

    <div v-if="loading" class="board">
      <div v-for="i in 4" :key="i" class="sk" style="height: 300px; border-radius: var(--r-m)" />
    </div>

    <!-- ===== voronka ===== -->
    <section v-else-if="view === 'board'" class="board">
      <div v-for="col in byStage" :key="col.key" class="col" :class="col.tone">
        <header>
          <span class="c-ttl"><UiIcon :name="col.icon" :size="14" />{{ col.key }}</span>
          <span class="c-n mono">{{ col.items.length }}</span>
        </header>

        <TransitionGroup tag="div" name="list" class="col-body">
          <article
            v-for="d in col.items"
            :key="d.id"
            class="deal"
            :class="{ busy: moving === d.id }"
            @click="openDetail(d)"
          >
            <div class="d-top">
              <b>{{ d.client_name }}</b>
              <span class="mono d-id">#{{ d.id }}</span>
            </div>
            <p class="d-obj">{{ d.listing_title || 'Obyekt biriktirilmagan' }}</p>
            <p class="mono d-addr">{{ d.listing_address || '—' }}</p>

            <div class="d-sum">
              <span class="amt">{{ money(d.amount, d.currency) }}</span>
              <span class="com mono">+{{ compactSum(d.commission).value }} {{ compactSum(d.commission).unit }}</span>
            </div>

            <div class="d-act" @click.stop>
              <button
                class="mv"
                :disabled="isFirst(d.stage) || moving === d.id"
                title="Orqaga"
                @click="advance(d, -1)"
              >
                ←
              </button>
              <span v-if="d.contract_signed" class="pill pill-ok tiny-pill">
                <UiIcon name="i-check" :size="10" />imzolangan
              </span>
              <button
                class="mv fwd"
                :disabled="isLast(d.stage) || moving === d.id"
                title="Keyingi bosqich"
                @click="advance(d, 1)"
              >
                →
              </button>
            </div>
          </article>
        </TransitionGroup>

        <p v-if="!col.items.length" class="col-empty">Bo'sh</p>
      </div>
    </section>

    <!-- ===== jadval ===== -->
    <section v-else class="card table-card">
      <EmptyState v-if="!rows.length" title="Bitim yo'q" note="Mijoz bilan ishlashni boshlaganingizda bitim shu yerda paydo bo'ladi." />
      <div v-else class="tbl-wrap">
        <table class="tbl">
          <thead>
            <tr>
              <th>Mijoz</th>
              <th>Obyekt</th>
              <th>Bosqich</th>
              <th>Summa</th>
              <th>Komissiya</th>
              <th>Sof daromad</th>
              <th>Yopilgan</th>
            </tr>
          </thead>
          <TransitionGroup tag="tbody" name="list">
            <tr v-for="d in rows" :key="d.id" class="row-link" @click="openDetail(d)">
              <td><b>{{ d.client_name }}</b></td>
              <td>{{ d.listing_title || '—' }}<br /><small class="mono dim">{{ d.listing_code }}</small></td>
              <td>
                <span class="pill" :class="{ 'pill-ok': d.stage === 'Yopilgan', 'pill-hot': d.stage === 'Bekor qilingan' }">
                  {{ d.stage }}
                </span>
              </td>
              <td><b>{{ money(d.amount, d.currency) }}</b></td>
              <td>{{ nf(d.commission) }}</td>
              <td class="net">{{ nf(d.agent_net) }}</td>
              <td class="mono dim">{{ d.closed_at ? dateLabel(d.closed_at) : '—' }}</td>
            </tr>
          </TransitionGroup>
        </table>
      </div>
    </section>

    <!-- bekor qilinganlar -->
    <section v-if="view === 'board' && cancelled.length" class="cancelled card card-pad anim-rise">
      <h3 class="h-sec">Bekor qilingan</h3>
      <div class="stack" style="margin-top: 10px">
        <span v-for="d in cancelled" :key="d.id" class="pill pill-hot">{{ d.client_name }}</span>
      </div>
    </section>

  </div>
</template>

<style scoped>
.switch {
  display: flex;
  gap: 3px;
  padding: 3px;
  border-radius: 9px;
  background: var(--surface-2);
  border: 1px solid var(--line);
}
.switch button {
  border: 0;
  background: none;
  font-family: inherit;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-3);
  padding: 6px 12px;
  border-radius: 7px;
  cursor: pointer;
  transition:
    background-color var(--dur-1) var(--ease-out),
    color var(--dur-1) var(--ease-out);
}
.switch button.on {
  background: var(--teal);
  color: var(--on-teal);
}

.tops {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}
.t-card .lbl {
  display: block;
  font-size: 11px;
  color: var(--text-3);
  margin-bottom: 6px;
}
.t-card b {
  font-family: var(--f-display);
  font-size: 23px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.t-card b i {
  font-style: normal;
  font-size: 13px;
  color: var(--text-2);
}
.t-card small {
  display: block;
  font-size: 10.5px;
  margin-top: 4px;
}
.t-card.teal b {
  color: var(--teal);
}
.t-card.brass b {
  color: var(--brass);
}
.donut-card {
  display: grid;
  place-items: center;
  padding: 10px;
}

/* ---- voronka ---- */
.board {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  align-items: start;
}
.col {
  background: var(--surface);
  border: 1px solid var(--line-soft);
  border-radius: var(--r-m);
  padding: 12px 10px;
  min-height: 180px;
}
.col > header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 0 3px 10px;
  border-bottom: 1px solid var(--line-soft);
  margin-bottom: 10px;
}
.c-ttl {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 12.5px;
  font-weight: 700;
}
.col.teal .c-ttl {
  color: var(--teal);
}
.col.label .c-ttl {
  color: var(--label);
}
.col.brass .c-ttl {
  color: var(--brass);
}
.col.deep .c-ttl {
  color: var(--teal-deep);
}
.c-n {
  font-size: 11px;
  color: var(--text-3);
  background: var(--surface-2);
  border-radius: 20px;
  padding: 2px 8px;
}
.col-body {
  display: grid;
  gap: 9px;
}

.deal {
  padding: 11px;
  border-radius: 10px;
  background: var(--surface-2);
  border: 1px solid transparent;
  cursor: pointer;
  transition:
    border-color var(--dur-1) var(--ease-out),
    transform var(--dur-1) var(--ease-out),
    opacity var(--dur-1) var(--ease-out);
}
.deal:hover {
  border-color: var(--teal);
  transform: translateY(-2px);
}
.deal.busy {
  opacity: 0.5;
  pointer-events: none;
}
.d-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 6px;
}
.d-top b {
  font-size: 12.5px;
}
.d-id {
  font-size: 9.5px;
  color: var(--text-3);
}
.d-obj {
  font-size: 11.5px;
  color: var(--text-2);
  margin-top: 4px;
}
.d-addr {
  font-size: 10px;
  color: var(--text-3);
  margin-top: 1px;
}
.d-sum {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 6px;
  margin-top: 9px;
  padding-top: 8px;
  border-top: 1px solid var(--line-soft);
}
.amt {
  font-family: var(--f-display);
  font-size: 14px;
  font-weight: 800;
  letter-spacing: -0.01em;
}
.com {
  font-size: 10px;
  color: var(--teal);
}
.d-act {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin-top: 9px;
}
.mv {
  width: 24px;
  height: 24px;
  border-radius: 7px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--text-2);
  cursor: pointer;
  font-size: 12px;
  line-height: 1;
  transition:
    background-color var(--dur-1) var(--ease-out),
    color var(--dur-1) var(--ease-out),
    border-color var(--dur-1) var(--ease-out);
}
.mv:hover:not(:disabled) {
  background: var(--teal);
  color: var(--on-teal);
  border-color: var(--teal);
}
.mv:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.tiny-pill {
  font-size: 9.5px;
  padding: 2px 7px;
}
.col-empty {
  text-align: center;
  font-size: 11.5px;
  color: var(--text-3);
  padding: 18px 0;
}

.cancelled {
  margin-top: 16px;
}

/* ---- jadval ---- */
.table-card {
  overflow: hidden;
}
.tbl-wrap {
  padding: 14px 8px 8px;
}
.net {
  color: var(--teal);
  font-weight: 600;
}

@media (max-width: 1080px) {
  .board {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 620px) {
  .board {
    grid-template-columns: 1fr;
  }
}
</style>
