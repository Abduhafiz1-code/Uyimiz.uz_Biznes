<script setup lang="ts">
/**
 * Reyting — Figmada freym yo'q edi.
 * 07-freymning chap paneldagi shkalasi ("Top Makler'ga 8 bitim") to'liq sahifaga
 * kengaytirildi: daraja yo'li, ko'rsatkichlar va agentlar jadvali.
 */
import { onMounted, ref } from 'vue'

import api from '@/api/client'
import CountUp from '@/components/CountUp.vue'
import PageHead from '@/components/PageHead.vue'
import SkeletonRows from '@/components/SkeletonRows.vue'
import UiIcon from '@/components/UiIcon.vue'
import { compactSum, nf } from '@/lib/format'
import { toast } from '@/stores/toast'
import type { RatingPayload } from '@/types'

const TIERS = [
  { key: 'Yangi', label: 'Yangi agent', need: 0 },
  { key: 'Faol', label: 'Faol makler', need: 5 },
  { key: 'Tajribali', label: 'Tajribali makler', need: 15 },
  { key: 'Top', label: 'Top Makler', need: 40 },
]

const data = ref<RatingPayload | null>(null)
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const { data: payload } = await api.get<RatingPayload>('/rating/')
    data.value = payload
  } catch {
    toast.err("Reytingni yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

function tierIndex(key: string) {
  return TIERS.findIndex((t) => t.key === key)
}

onMounted(load)
</script>

<template>
  <div>
    <PageHead
      title="Reyting"
      note="Ochiq reyting — mijoz oqimi va keyingi darajangiz shunga bog'liq"
      eyebrow="Daraja"
    >
      <span v-if="data?.rank" class="pill pill-vip">
        <UiIcon name="i-star" :size="12" />Umumiy {{ data.rank }}-o'rin
      </span>
    </PageHead>

    <div v-if="loading"><SkeletonRows :rows="6" :height="72" /></div>

    <template v-else-if="data">
      <!-- ===== yuqori blok: reyting + daraja yo'li ===== -->
      <section class="hero card anim-rise">
        <div class="hero-l girih">
          <span class="ava big">{{ data.agent.initials }}</span>
          <div>
            <div class="h-disp score">{{ String(data.agent.rating).replace('.', ',') }} <span>★</span></div>
            <p class="muted">{{ data.agent.full_name }} · {{ data.agent.district }}</p>
            <div class="stack" style="margin-top: 10px">
              <span class="pill pill-ok"><UiIcon name="i-shield" :size="11" />{{ data.agent.certification }}</span>
              <span class="pill">{{ data.agent.tier }}</span>
            </div>
          </div>
        </div>

        <div class="hero-r">
          <div class="row-between" style="margin-bottom: 10px">
            <h2 class="h-sec">Daraja yo'li</h2>
            <span v-if="data.tier.next_label" class="mono next">
              {{ data.tier.next_label }}'ga {{ data.tier.remaining }} bitim
            </span>
            <span v-else class="mono next">Eng yuqori daraja</span>
          </div>

          <div class="bar big-bar"><i :style="{ width: data.tier.percent + '%' }" /></div>

          <ol class="ladder">
            <li
              v-for="(t, i) in TIERS"
              :key="t.key"
              :class="{ done: i <= tierIndex(data.tier.current), now: t.key === data.tier.current }"
            >
              <i />
              <b>{{ t.label }}</b>
              <small class="mono">{{ t.need }}+ bitim</small>
            </li>
          </ol>
        </div>
      </section>

      <!-- ===== ko'rsatkichlar ===== -->
      <section class="metrics stagger">
        <div class="card card-pad m">
          <span class="lbl">CRMda yopilgan</span>
          <b><CountUp :value="data.metrics.closed_deals" /></b>
        </div>
        <div class="card card-pad m">
          <span class="lbl">Ochiq bitimlar</span>
          <b><CountUp :value="data.metrics.open_deals" /></b>
        </div>
        <div class="card card-pad m teal">
          <span class="lbl">Konversiya</span>
          <b><CountUp :value="data.metrics.conversion" /><i>%</i></b>
        </div>
        <div class="card card-pad m">
          <span class="lbl">Javob tezligi</span>
          <b><CountUp :value="data.metrics.response_minutes" /><i>daq</i></b>
        </div>
        <div class="card card-pad m teal">
          <span class="lbl">Jami komissiya</span>
          <b>{{ compactSum(data.metrics.total_commission).value }}<i>{{ compactSum(data.metrics.total_commission).unit }}</i></b>
        </div>
        <div class="card card-pad m brass">
          <span class="lbl">Platformaga to'langan</span>
          <b>{{ compactSum(data.metrics.platform_paid).value }}<i>{{ compactSum(data.metrics.platform_paid).unit }}</i></b>
        </div>
      </section>

      <!-- ===== reyting jadvali ===== -->
      <section class="card table-card anim-rise">
        <header class="t-head">
          <div>
            <h2 class="h-sec">Agentlar reytingi</h2>
            <p class="dim">Toshkent bo'yicha eng yuqori 10 ta agent</p>
          </div>
          <span class="pill mono">Yangilandi: bugun</span>
        </header>

        <div class="tbl-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th>#</th>
                <th>Agent</th>
                <th>Hudud</th>
                <th>Daraja</th>
                <th>Reyting</th>
                <th>Karyera</th>
                <th>Bu oy</th>
              </tr>
            </thead>
            <TransitionGroup tag="tbody" name="list">
              <tr v-for="(a, i) in data.leaderboard" :key="a.id" :class="{ me: a.is_me }">
                <td class="mono rank" :class="{ podium: i < 3 }">{{ i + 1 }}</td>
                <td>
                  <div class="who">
                    <span class="ava ava-sm" :class="{ 'ava-brass': i === 0 }">{{ a.initials }}</span>
                    <b>{{ a.full_name }}<span v-if="a.is_me" class="you">siz</span></b>
                  </div>
                </td>
                <td>{{ a.district || '—' }}</td>
                <td><span class="pill" :class="{ 'pill-vip': a.tier === 'Top' }">{{ a.tier }}</span></td>
                <td><b class="star">{{ String(a.rating).replace('.', ',') }} ★</b></td>
                <td>{{ a.closed_deals }}</td>
                <td class="mono dim">{{ a.month_deals }}</td>
              </tr>
            </TransitionGroup>
          </table>
        </div>
      </section>

      <p class="foot-note">
        Reyting yopilgan bitimlar soni, javob tezligi va mijoz baholaridan hisoblanadi. Daraja
        ko'tarilganda platforma sizga ko'proq mijoz biriktiradi — komissiya foizi esa
        <b>{{ nf(data.agent.commission_rate, 1) }}%</b> darajasida qoladi.
      </p>
    </template>
  </div>
</template>

<style scoped>
/* ---- hero ---- */
.hero {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
  overflow: hidden;
  margin-bottom: 18px;
}
.hero-l {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px;
  background-color: var(--surface-2);
  border-right: 1px solid var(--line-soft);
}
.ava.big {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  font-size: 20px;
}
.score {
  font-size: 34px;
}
.score span {
  color: var(--brass);
  font-size: 24px;
}
.hero-l p {
  font-size: 12.5px;
  margin-top: 3px;
}

.hero-r {
  padding: 22px;
}
.next {
  font-size: 10.5px;
  color: var(--teal);
}
.big-bar {
  height: 7px;
  margin-bottom: 18px;
}

.ladder {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.ladder li {
  display: grid;
  gap: 3px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid var(--line-soft);
  background: var(--surface-2);
  transition:
    border-color var(--dur-2) var(--ease-out),
    background-color var(--dur-2) var(--ease-out);
}
.ladder li i {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--line);
  margin-bottom: 3px;
}
.ladder li.done i {
  background: var(--teal);
}
.ladder li.now {
  border-color: var(--teal);
  background: var(--teal-glow);
}
.ladder b {
  font-size: 12px;
}
.ladder small {
  font-size: 10px;
  color: var(--text-3);
}

/* ---- ko'rsatkichlar ---- */
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}
.m .lbl {
  display: block;
  font-size: 11px;
  color: var(--text-3);
  margin-bottom: 6px;
}
.m b {
  font-family: var(--f-display);
  font-size: 23px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.m b i {
  font-style: normal;
  font-size: 13px;
  color: var(--text-2);
  margin-left: 3px;
}
.m.teal b {
  color: var(--teal);
}
.m.brass b {
  color: var(--brass);
}

/* ---- jadval ---- */
.table-card {
  overflow: hidden;
}
.t-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 16px 12px;
}
.t-head p {
  font-size: 12px;
  margin-top: 2px;
}
.tbl-wrap {
  padding: 0 8px 10px;
}
.rank {
  color: var(--text-3);
  width: 30px;
}
.rank.podium {
  color: var(--brass);
  font-weight: 700;
}
.who {
  display: flex;
  align-items: center;
  gap: 9px;
}
.who b {
  font-size: 12.5px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.you {
  font-size: 9.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--on-teal);
  background: var(--teal);
  border-radius: 20px;
  padding: 1px 7px;
}
tr.me {
  background: var(--teal-glow);
}
.star {
  color: var(--brass);
}

.foot-note {
  font-size: 12.5px;
  color: var(--text-3);
  line-height: 1.65;
  margin-top: 16px;
  max-width: 76ch;
}
.foot-note b {
  color: var(--text-2);
}

@media (max-width: 980px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .hero-l {
    border-right: 0;
    border-bottom: 1px solid var(--line-soft);
  }
  .ladder {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
