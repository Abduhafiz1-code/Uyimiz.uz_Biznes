export interface Agent {
  id: number
  phone: string
  full_name: string
  email: string
  district: string
  initials: string
  rating: string
  tier: string
  certification: string
  platform_share: number
  commission_rate: string
  avg_response_minutes: number
  total_deals: number
  joined_at: string
  tier_percent: number
  tier_remaining: number
  tier_next_label: string | null
}

export interface Client {
  id: number
  name: string
  phone: string
  request: string
  deal_type: string
  district: string
  budget_label: string
  budget_min: string | null
  budget_max: string | null
  status: string
  source: string
  note: string
  is_verified: boolean
  initials: string
  deals_count: number
  created_at: string
  last_contact_at: string | null
}

export interface PropertyPhoto {
  id: number
  image: string
  order: number
  uploaded_at: string
}

export interface Property {
  id: number
  photos: PropertyPhoto[]
  /** Birinchi rasmning to'liq manzili; rasm bo'lmasa null. */
  cover: string | null
  listing_id: string
  title: string
  district: string
  address: string
  deal_type: string
  price: string
  price_label: string
  currency: string
  rooms: number
  area: string
  floor: number
  total_floors: number
  built_year: number | null
  status: string
  badge: string
  is_verified: boolean
  owner_name: string
  owner_phone: string
  photo_count: number
  views: number
  description: string
  created_at: string
}

export interface Deal {
  id: number
  client: number
  client_name: string
  listing: number | null
  listing_title: string
  listing_code: string
  listing_address: string
  stage: string
  amount: string
  currency: string
  commission: string
  platform_cut: string
  agent_net: string
  contract_signed: boolean
  note: string
  created_at: string
  closed_at: string | null
}

export interface Showing {
  id: number
  client: number
  client_name: string
  listing: number
  listing_title: string
  listing_address: string
  listing_code: string
  scheduled_at: string
  status: string
  note: string
}

export interface Activity {
  id: number
  kind: string
  text: string
  client: number | null
  client_name: string
  created_at: string
}

export interface Dashboard {
  agent: Agent
  greeting_note: string
  kpi: {
    active_clients: number
    active_clients_delta: number
    month_deals: number
    month_deals_delta: number
    commission_income: string
    platform_share: number
    response_minutes: number
  }
  tier: {
    percent: number
    remaining: number
    next_label: string | null
    current: string
    rating: string
  }
  new_clients: Client[]
  pipeline: { stage: string; count: number }[]
  upcoming_showings: Showing[]
  recent_activity: Activity[]
}

export interface LeaderRow {
  id: number
  full_name: string
  initials: string
  district: string
  rating: string
  tier: string
  closed_deals: number
  month_deals: number
  is_me: boolean
}

export interface RatingPayload {
  agent: Agent
  rank: number | null
  tier: { percent: number; remaining: number; next_label: string | null; current: string }
  metrics: {
    closed_deals: number
    open_deals: number
    conversion: number
    response_minutes: number
    total_commission: string
    platform_paid: string
    avg_commission: string
  }
  leaderboard: LeaderRow[]
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
