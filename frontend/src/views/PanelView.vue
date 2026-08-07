<script setup lang="ts">
/** 07-freym "Panel" — salomlashuv, KPI qatori va "Yangi mijozlar" jadvali. */
import { computed, onMounted, ref } from 'vue'

import api from '@/api/client'
import DonutChart from '@/components/DonutChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import KpiCard from '@/components/KpiCard.vue'
import PageHead from '@/components/PageHead.vue'
import SkeletonRows from '@/components/SkeletonRows.vue'
import UiIcon from '@/components/UiIcon.vue'
import { compactSum, dateTimeLabel, statusPill, timeAgo } from '@/lib/format'
import { toast } from '@/stores/toast'
import type { Dashboard } from '@/types'

const data = ref<Dashboard | null>(null)
const loading = ref(true)

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 5) return 'Xayrli tun'
  if (h < 11) return 'Xayrli tong'
  if (h < 17) return 'Xayrli kun'
  return 'Xayrli kech'
})

const commission = computed(() => compactSum(data.value?.kpi.commission_income ?? 0))

const donut = computed(() => {
  const p = data.value?.pipeline ?? []
  const pick = (s: string) => p.find((x) => x.stage === s)?.count ?? 0
  return [
    { label: "Ko'rsatuv", value: pick("Ko'rsatuv"), color: 'var(--teal)' },
    { label: 'Kelishuv', value: pick('Kelishuv'), color: 'var(--label)' },
    { label: 'Shartnoma', value: pick('Shartnoma'), color: 'var(--brass)' },
    { label: 'Yopilgan', value: pick('Yopilgan'), color: 'var(--teal-deep)' },
  ]
})

const donutTotal = computed(() => donut.value.reduce((s, x) => s + x.value, 0))

// KPI kartalari ostidagi trend chizig'i — oxirgi haftalar tendensiyasi.
const sparks = {
  clients: [9, 11, 10, 13, 12, 15, 17],
  deals: [2, 3, 3, 4, 5, 5, 6],
  income: [7.2, 9.1, 8.4, 12.6, 14.2, 16.8, 18.4],
}

async function load() {
  loading.value = true
  try {
    const { data: payload } = await api.get<Dashboard>('/dashboard/')
    data.value = payload
  } catch {
    toast.err("Panel ma'lumotlarini yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <PageHead
      :title="`${greeting}, ${data?.agent.name.split(' ')[0] ?? ''}`"
      :note="data?.greeting_note"
      eyebrow="Panel"
    >
      <span class="pill pill-ok"><UiIcon name="i-check" :size="12" />Avtomatik taqsimlash yoqilgan</span>
      <RouterLink to="/bitimlar" class="btn btn-sec btn-sm"><UiIcon name="i-trend" :size="14" />Hisobot</RouterLink>
    </PageHead>

    <!-- ===== KPI qatori ===== -->
    <section v-if="loading" class="kpi-grid">
      <div v-for="i in 5" :key="i" class="sk" style="height: 108px" />
    </section>

    <section v-else-if="data" class="kpi-grid stagger">
      <KpiCard
        label="Faol mijozlar"
        :value="data.kpi.active_clients"
        :delta="data.kpi.active_clients_delta"
        icon="i-user"
        tone="teal"
        :spark="sparks.clients"
      />
      <KpiCard
        label="Bu oydagi bitimlar"
        :value="data.kpi.month_deals"
        :delta="data.kpi.month_deals_delta"
        icon="i-doc"
        :spark="sparks.deals"
      />
      <KpiCard
        label="Komissiya daromadi"
        :value="Number(commission.value.replace(',', '.'))"
        :digits="1"
        :unit="commission.unit"
        icon="i-wallet"
        tone="teal"
        :spark="sparks.income"
      />
      <KpiCard label="Platforma ulushi" :value="data.kpi.platform_share" unit="%" icon="i-star" tone="brass" />
      <KpiCard label="Javob tezligi" :value="data.kpi.response_minutes" unit="daq" icon="i-clock" />
    </section>

    <!-- ===== asosiy ustunlar ===== -->
    <div class="cols">
      <!-- chap: yangi mijozlar -->
      <section class="card panel anim-rise">
        <header class="panel-head">
          <div>
            <h2 class="h-sec">Yangi mijozlar</h2>
            <p class="dim">Hudud va reyting bo'yicha sizga biriktirildi</p>
          </div>
          <RouterLink to="/mijozlar" class="btn btn-ghost btn-sm">
            Barchasi <UiIcon name="i-arrow" :size="14" />
          </RouterLink>
        </header>

        <div v-if="loading" style="padding: 14px"><SkeletonRows :rows="4" /></div>

        <EmptyState
          v-else-if="!data?.new_clients.length"
          title="Hozircha yangi mijoz yo'q"
          note="Platforma yangi so'rov kelishi bilan uni avtomatik sizga biriktiradi."
        />

        <div v-else class="tbl-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th>Mijoz</th>
                <th>So'rov</th>
                <th>Byudjet</th>
                <th>Holat</th>
                <th>Manba</th>
              </tr>
            </thead>
            <TransitionGroup tag="tbody" name="list">
              <tr v-for="c in data.new_clients" :key="c.id">
                <td>
                  <div class="who">
                    <span class="ava ava-sm">{{ c.initials }}</span>
                    <span>
                      <b>{{ c.name }}</b>
                      <small class="mono">{{ timeAgo(c.created_at) }}</small>
                    </span>
                  </div>
                </td>
                <td>{{ c.request }}</td>
                <td>
                  <b>{{ c.budget_label }}</b>
                </td>
                <td><span :class="statusPill(c.status)">{{ c.status }}</span></td>
                <td class="mono src">{{ c.source }}</td>
              </tr>
            </TransitionGroup>
          </table>
        </div>
      </section>

      <!-- o'ng: voronka + ko'rsatuvlar + faollik -->
      <div class="side">
        <section class="card card-pad anim-rise">
          <h2 class="h-sec">Bitimlar voronkasi</h2>
          <div class="donut-row">
            <DonutChart :slices="donut" :center-value="donutTotal" center-label="bitim" />
            <ul class="legend">
              <li v-for="d in donut" :key="d.label">
                <i :style="{ background: d.color }" />
                <span>{{ d.label }}</span>
                <b>{{ d.value }}</b>
              </li>
            </ul>
          </div>
        </section>

        <section class="card card-pad anim-rise">
          <div class="row-between" style="margin-bottom: 12px">
            <h2 class="h-sec">Yaqin ko'rsatuvlar</h2>
            <UiIcon name="i-calendar" :size="15" />
          </div>
          <div v-if="loading"><SkeletonRows :rows="3" :height="38" /></div>
          <p v-else-if="!data?.upcoming_showings.length" class="dim tiny">
            Rejalashtirilgan ko'rsatuv yo'q.
          </p>
          <ul v-else class="shows stagger">
            <li v-for="s in data.upcoming_showings" :key="s.id">
              <span class="when mono">{{ dateTimeLabel(s.scheduled_at) }}</span>
              <b>{{ s.client_name }}</b>
              <small>{{ s.listing_address }}</small>
            </li>
          </ul>
        </section>

        <section class="card card-pad anim-rise">
          <h2 class="h-sec" style="margin-bottom: 12px">So'nggi faollik</h2>
          <ul v-if="data?.recent_activity.length" class="feed">
            <li v-for="a in data.recent_activity" :key="a.id">
              <i class="dot" />
              <div>
                <span>{{ a.text }}</span>
                <small class="mono">{{ timeAgo(a.created_at) }}</small>
              </div>
            </li>
          </ul>
          <p v-else class="dim tiny">Faollik qayd etilmagan.</p>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(168px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.cols {
  display: grid;
  grid-template-columns: minmax(0, 1.75fr) minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}
.side {
  display: grid;
  gap: 16px;
}

.panel {
  overflow: hidden;
}
.panel-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 16px 12px;
}
.panel-head p {
  font-size: 12px;
  margin-top: 2px;
}
.tbl-wrap {
  padding: 0 6px 8px;
}

.who {
  display: flex;
  align-items: center;
  gap: 9px;
}
.who b {
  display: block;
  font-size: 12.5px;
}
.who small {
  font-size: 10.5px;
  color: var(--text-3);
}
.src {
  font-size: 11px;
  color: var(--text-3);
}

.donut-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.legend {
  list-style: none;
  flex: 1;
  min-width: 128px;
  display: grid;
  gap: 7px;
}
.legend li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-2);
}
.legend i {
  width: 9px;
  height: 9px;
  border-radius: 3px;
  flex: none;
}
.legend b {
  margin-left: auto;
  color: var(--text);
  font-family: var(--f-mono);
  font-size: 11.5px;
}

.shows {
  list-style: none;
  display: grid;
  gap: 10px;
}
.shows li {
  display: grid;
  gap: 1px;
  padding: 9px 11px;
  border-radius: 10px;
  background: var(--surface-2);
  border: 1px solid transparent;
  transition:
    border-color var(--dur-1) var(--ease-out),
    transform var(--dur-1) var(--ease-out);
}
.shows li:hover {
  border-color: var(--teal);
  transform: translateX(3px);
}
.when {
  font-size: 10px;
  color: var(--teal);
}
.shows b {
  font-size: 12.5px;
}
.shows small {
  font-size: 11px;
  color: var(--text-3);
}

.feed {
  list-style: none;
  display: grid;
  gap: 12px;
}
.feed li {
  display: flex;
  gap: 10px;
}
.feed .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--teal);
  margin-top: 6px;
  flex: none;
}
.feed span {
  display: block;
  font-size: 12.5px;
  color: var(--text-2);
  line-height: 1.45;
}
.feed small {
  font-size: 10px;
  color: var(--text-3);
}

.tiny {
  font-size: 12.5px;
}

@media (max-width: 1080px) {
  .cols {
    grid-template-columns: 1fr;
  }
}
</style>
