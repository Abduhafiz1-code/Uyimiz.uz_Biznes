<script setup lang="ts">
/**
 * Mijozlar — bu ekran uchun Figmada freym yo'q edi.
 * 07-freymning jadval tili (mono sarlavhalar, pill holatlar, ava + ism ustuni)
 * saqlangan holda filtr qatori va o'ng yon panel qo'shildi.
 */
import { computed, onMounted, ref, watch } from 'vue'

import api from '@/api/client'
import DrawerPanel from '@/components/DrawerPanel.vue'
import EmptyState from '@/components/EmptyState.vue'
import PageHead from '@/components/PageHead.vue'
import SkeletonRows from '@/components/SkeletonRows.vue'
import UiIcon from '@/components/UiIcon.vue'
import { SUPPORT_PHONE, telHref } from '@/lib/config'
import { dateLabel, statusPill, timeAgo } from '@/lib/format'
import { toast } from '@/stores/toast'
import type { Client, Paginated } from '@/types'

const STATUSES = [
  "Qo'ng'iroq kutmoqda",
  "Ko'rsatuv belgilandi",
  'Fotoga chiqish',
  'Shartnomada',
  'Yopilgan',
  'Rad etilgan',
]
const SOURCES = ['Mobil ilova', 'Web', 'Telegram']

const rows = ref<Client[]>([])
const count = ref(0)
const page = ref(1)
const loading = ref(true)
const search = ref('')
const status = ref('')
const source = ref('')

const selected = ref<Client | null>(null)
const saving = ref(false)

const pages = computed(() => Math.max(Math.ceil(count.value / 12), 1))

/** Mijozda raqam bo'lmasa qo'llab-quvvatlash raqamiga qo'ng'iroq qilinadi. */
const callNumber = computed(() => selected.value?.phone || SUPPORT_PHONE)

let debounce = 0
watch([search, status, source], () => {
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
    const { data } = await api.get<Paginated<Client>>('/clients/', {
      params: {
        page: page.value,
        search: search.value || undefined,
        status: status.value || undefined,
        source: source.value || undefined,
      },
    })
    rows.value = data.results
    count.value = data.count
  } catch {
    toast.err("Mijozlarni yuklab bo'lmadi")
  } finally {
    loading.value = false
  }
}

async function setStatus(client: Client, next: string) {
  saving.value = true
  try {
    const { data } = await api.post<Client>(`/clients/${client.id}/status/`, { status: next })
    const i = rows.value.findIndex((r) => r.id === client.id)
    if (i !== -1) rows.value[i] = data
    if (selected.value?.id === client.id) selected.value = data
    toast.ok(`${data.name} → ${next}`)
  } catch {
    toast.err("Holatni o'zgartirib bo'lmadi")
  } finally {
    saving.value = false
  }
}

function clearFilters() {
  search.value = ''
  status.value = ''
  source.value = ''
}

onMounted(load)
</script>

<template>
  <div>
    <PageHead title="Mijozlar" :note="`Jami ${count} ta so'rov · sizga biriktirilgan`" eyebrow="CRM">
      <span class="pill pill-ok"><UiIcon name="i-check" :size="12" />Avtomatik taqsimlangan</span>
    </PageHead>

    <!-- filtr qatori -->
    <section class="filters card anim-rise">
      <label class="inp grow">
        <UiIcon name="i-search" :size="15" />
        <input v-model="search" type="search" placeholder="Ism, telefon yoki so'rov bo'yicha…" />
      </label>

      <label class="inp">
        <UiIcon name="i-filter" :size="15" />
        <select v-model="status">
          <option value="">Barcha holat</option>
          <option v-for="s in STATUSES" :key="s" :value="s">{{ s }}</option>
        </select>
      </label>

      <label class="inp">
        <UiIcon name="i-inbox" :size="15" />
        <select v-model="source">
          <option value="">Barcha manba</option>
          <option v-for="s in SOURCES" :key="s" :value="s">{{ s }}</option>
        </select>
      </label>

      <button
        class="btn btn-ghost btn-sm"
        :disabled="!search && !status && !source"
        @click="clearFilters"
      >
        Tozalash
      </button>
    </section>

    <!-- tez filtr chiplari -->
    <div class="chips">
      <button
        class="pill pill-btn"
        :class="{ 'pill-ok': !status }"
        @click="status = ''"
      >
        Hammasi
      </button>
      <button
        v-for="s in STATUSES"
        :key="s"
        class="pill pill-btn"
        :class="{ 'pill-ok': status === s }"
        @click="status = status === s ? '' : s"
      >
        {{ s }}
      </button>
    </div>

    <!-- jadval -->
    <section class="card table-card anim-rise">
      <div v-if="loading" style="padding: 16px"><SkeletonRows :rows="7" /></div>

      <EmptyState
        v-else-if="!rows.length"
        title="Mijoz topilmadi"
        note="Filtrlarni kengaytiring yoki qidiruvni tozalang — yangi so'rovlar avtomatik shu yerga tushadi."
      >
        <button class="btn btn-sec btn-sm" @click="clearFilters">Filtrni tozalash</button>
      </EmptyState>

      <div v-else class="tbl-wrap">
        <table class="tbl">
          <thead>
            <tr>
              <th>Mijoz</th>
              <th>So'rov</th>
              <th>Byudjet</th>
              <th>Holat</th>
              <th>Manba</th>
              <th>Qo'shilgan</th>
            </tr>
          </thead>
          <TransitionGroup tag="tbody" name="list">
            <tr v-for="c in rows" :key="c.id" class="row-link" @click="selected = c">
              <td>
                <div class="who">
                  <span class="ava ava-sm">{{ c.initials }}</span>
                  <span>
                    <b>{{ c.name }}
                      <UiIcon v-if="c.is_verified" name="i-shield" :size="12" class="vf" />
                    </b>
                    <small class="mono">{{ c.phone || '—' }}</small>
                  </span>
                </div>
              </td>
              <td>{{ c.request }}</td>
              <td><b>{{ c.budget_label }}</b></td>
              <td><span :class="statusPill(c.status)">{{ c.status }}</span></td>
              <td class="mono dim">{{ c.source }}</td>
              <td class="mono dim">{{ timeAgo(c.created_at) }}</td>
            </tr>
          </TransitionGroup>
        </table>
      </div>

      <footer v-if="!loading && rows.length" class="pager">
        <span class="dim mono">{{ count }} ta yozuv · {{ page }}/{{ pages }}-sahifa</span>
        <div class="stack">
          <button class="btn btn-ghost btn-sm" :disabled="page <= 1" @click="page--">Oldingi</button>
          <button class="btn btn-ghost btn-sm" :disabled="page >= pages" @click="page++">Keyingi</button>
        </div>
      </footer>
    </section>

    <!-- ==== tafsilot paneli ==== -->
    <DrawerPanel
      :open="!!selected"
      :title="selected?.name ?? ''"
      :subtitle="selected ? `${selected.request} · ${selected.budget_label}` : ''"
      @close="selected = null"
    >
      <template v-if="selected">
        <div class="d-top">
          <span class="ava">{{ selected.initials }}</span>
          <div>
            <span :class="statusPill(selected.status)">{{ selected.status }}</span>
            <p class="mono d-phone">
            {{ selected.phone || `Shaxsiy raqam yo'q · qo'llab-quvvatlash ${SUPPORT_PHONE}` }}
          </p>
          </div>
        </div>

        <dl class="facts">
          <div><dt>Bitim turi</dt><dd>{{ selected.deal_type }}</dd></div>
          <div><dt>Hudud</dt><dd>{{ selected.district || '—' }}</dd></div>
          <div><dt>Manba</dt><dd>{{ selected.source }}</dd></div>
          <div><dt>myID</dt><dd>{{ selected.is_verified ? 'Tasdiqlangan' : 'Tasdiqlanmagan' }}</dd></div>
          <div><dt>Bitimlar</dt><dd>{{ selected.deals_count }} ta</dd></div>
          <div><dt>Qo'shilgan</dt><dd>{{ dateLabel(selected.created_at) }}</dd></div>
        </dl>

        <h3 class="h-sec sec-t">Holatni o'zgartirish</h3>
        <div class="stack">
          <button
            v-for="s in STATUSES"
            :key="s"
            class="pill pill-btn"
            :class="{ 'pill-ok': selected.status === s }"
            :disabled="saving"
            @click="setStatus(selected, s)"
          >
            {{ s }}
          </button>
        </div>

        <h3 class="h-sec sec-t">Izoh</h3>
        <p class="note">{{ selected.note || 'Izoh yozilmagan.' }}</p>

        <div class="safe">
          <b>Xavfsiz bitim.</b> Mijozdan oldindan to'lov olmang — komissiya faqat shartnoma
          imzolangach platforma orqali hisoblanadi.
        </div>
      </template>

      <template #footer>
        <a :href="telHref(callNumber)" class="btn btn-pri" style="flex: 1">
          <UiIcon name="i-phone" :size="15" />Qo'ng'iroq qilish
        </a>
        <button class="btn btn-ghost" @click="selected = null">Yopish</button>
      </template>
    </DrawerPanel>
  </div>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 9px;
  padding: 11px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.grow {
  flex: 1;
  min-width: 190px;
}
.filters .inp {
  padding: 9px 12px;
}

.chips {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}
.chips button {
  background: none;
  cursor: pointer;
  font-family: inherit;
}

.table-card {
  overflow: hidden;
}
.tbl-wrap {
  padding: 14px 8px 4px;
}

.who {
  display: flex;
  align-items: center;
  gap: 9px;
}
.who b {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12.5px;
}
.who small {
  font-size: 10.5px;
  color: var(--text-3);
}
.vf {
  color: var(--teal);
}

.pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid var(--line-soft);
  font-size: 11.5px;
  flex-wrap: wrap;
}

/* ---- drawer ---- */
.d-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}
.d-phone {
  font-size: 11.5px;
  color: var(--text-3);
  margin-top: 5px;
}
.facts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--line-soft);
  border: 1px solid var(--line-soft);
  border-radius: var(--r-m);
  overflow: hidden;
}
.facts > div {
  background: var(--surface);
  padding: 11px 12px;
}
.facts dt {
  font-size: 10.5px;
  color: var(--text-3);
  margin-bottom: 3px;
}
.facts dd {
  font-size: 13px;
  font-weight: 600;
}
.sec-t {
  margin: 20px 0 10px;
}
.note {
  font-size: 12.5px;
  color: var(--text-2);
  line-height: 1.6;
}
.safe {
  margin-top: 18px;
  font-size: 12px;
  color: var(--text-2);
  line-height: 1.55;
  padding: 13px;
  border-radius: var(--r-m);
  background: var(--teal-glow);
  border: 1px solid color-mix(in srgb, var(--teal) 28%, transparent);
}
.safe b {
  color: var(--teal);
}
</style>
