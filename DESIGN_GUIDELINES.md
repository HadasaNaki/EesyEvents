# 🎨 EasyEvents - Design & UX Guidelines

## Overview
Event planning platform for young Israeli couples. Elegant, calm, and user-focused design with Hebrew RTL support.

---

## 📐 Card Design System

### **Card Structure (Venues & Suppliers)**

```
┌─────────────────────────────────────┐
│  [Icon Header - 48px height]        │  ← Large emoji or icon
├─────────────────────────────────────┤
│  Title           📍 Location Badge  │  ← Name + location right-aligned
├─────────────────────────────────────┤
│  [Key Stats Row]                    │  ← Icons + key metrics
│  👥 Capacity / 💰 Price            │
├─────────────────────────────────────┤
│  [Category/Type Badge]              │  ← Tag for type
│  🍽️ קייטרינג  |  🥩 סוג קולינרי   │
├─────────────────────────────────────┤
│  [CTA Buttons]                      │
│  [☎️ התקשר] [❤️ שמור]              │
└─────────────────────────────────────┘
```

### **Design Principles**

✅ **DO:**
- Use emojis as visual anchors (scan-friendly)
- Group related info horizontally (Stats row)
- Keep card height ~320-380px max (mobile-friendly)
- Use icons + numbers instead of labels only
- Make CTAs prominent and large (min 40px tap target)
- Consistent spacing: 16px/24px/32px padding rhythm
- Show hover effects: shadow, scale, color shift
- Single info hierarchy per section

❌ **DON'T:**
- Mix text-only labels with icons (pick one)
- Crowd more than 5 visual elements per card
- Use buttons smaller than 40px height
- Show all info at once (prioritize key metrics)
- Overload with colors (stick to 2-3 accent colors)
- Make text-only CTAs (use icons + text)

---

## 🎯 Information Hierarchy

### **Venue Cards**

| Priority | Element | Icon | Example |
|----------|---------|------|---------|
| 1 (Title) | Name | — | "אולם הזהב" |
| 1 (Badge) | City | 📍 | "תל אביב" |
| 2 (Stats) | Capacity | 👥 | "עד 200 אורחים" |
| 2 (Stats) | Price | 💰 | "₪ 5,000" |
| 3 (Secondary) | Style | 💎✨🏛️ | "בוהו" / "הפקסה" |
| 4 (CTA) | Call/Save | ☎️❤️ | Buttons |

### **Supplier Cards**

| Priority | Element | Icon | Example |
|----------|---------|------|---------|
| 1 (Title) | Name | — | "קייטרינג בשר" |
| 1 (Badge) | City | 📍 | "תל אביב" |
| 2 (Type) | Category | 🍽️🎧📷 | "קייטרינג" |
| 2 (Type) | Cuisine/Style | 🥩🥛🥗 | "בשרי / חלבי" |
| 3 (Price) | Starting Price | 💰 | "₪ 150" |
| 4 (CTA) | Call/Save | ☎️❤️ | Buttons |

---

## 🎨 Icon Reference

### **Category Icons**
```
🍽️ Catering         🎧 DJ              📷 Photographer
🎨 Designer         🌸 Florist         🎵 Music Band
🏛️ Venue            ✨ Event Planning  👰 Wedding
```

### **Attribute Icons**
```
📍 Location         👥 Capacity        💰 Price
💎 Luxury/Style     ✨ Boho Style     🏛️ Modern
🥩 Meat             🥛 Dairy           🥗 Vegan
👨‍🍳 Private Chef    ❤️ Save/Like      ☎️ Call
```

### **Action Icons**
```
☎️ Call/Phone      💬 Message         ❤️ Save/Like
✏️ Edit            🔗 Share           📅 Book
```

---

## 💬 UX Copy (Hebrew)

### **Headings**
- ✅ "🏛️ אולמות לאירוע" (instead of "Venue List")
- ✅ "✨ צוות מומלץ" (instead of "Suppliers")
- ✅ "🎉 התוצאות שלך מוכנות!" (instead of "Search Results")

### **Labels & Microcopy**
- ✅ "קיבולת: עד 200" (instead of "Capacity: 200 guests")
- ✅ "סוג קולינרי: בשרי" (instead of "Type: Meat")
- ✅ "תחיל מ-₪ 150" (instead of "Price: 150 NIS")
- ✅ "☎️ התקשר" (instead of "Contact")
- ✅ "לא מצאנו אולמות" (instead of "No results")

### **CTA Button Copy**
- ✅ "☎️ התקשר" - Call button (friendly)
- ✅ "❤️" - Save favorite (heart emoji only)
- ✅ "📅 בקש הצעה" - Request offer
- ✅ "🔗 שיתוף" - Share

---

## 🎨 Color Palette

### **Primary Colors**
- **Burgundy** (#800020) - Main CTA, headings
- **Dark Burgundy** (#600018) - Hover state, darker accents
- **Light Burgundy** (#800020/10%) - Badge backgrounds

### **Neutrals**
- **Text Primary** (#1F2937) - Body text, titles
- **Text Secondary** (#6B7280) - Labels, captions
- **Background** (#F9FAFB) - Page background
- **Border** (#E5E7EB) - Card borders, dividers

### **Semantic Colors**
- **Success** (#10B981) - Confirmation
- **Warning** (#F59E0B) - Alert
- **Danger** (#EF4444) - Error
- **Info** (#3B82F6) - Information

---

## 📱 Responsive Layout

### **Desktop (1024px+)**
```
Grid: 3 columns
Gap: 32px (2rem)
Card Width: ~300px
```

### **Tablet (768px - 1024px)**
```
Grid: 2 columns
Gap: 24px (1.5rem)
Card Width: ~280px
```

### **Mobile (< 768px)**
```
Grid: 1 column
Gap: 16px (1rem)
Card Width: 100% (full width)
```

---

## ✨ Interaction States

### **Card Hover (Desktop)**
```css
.venue-card:hover {
  box-shadow: 0 20px 40px rgba(0,0,0,0.12);
  transform: translateY(-4px);
  transition: all 0.3s ease;
}
```

### **Button States**

| State | Style |
|-------|-------|
| Normal | `bg-[#800020]` |
| Hover | `bg-[#600018]` shadow lift |
| Active | `bg-[#400010]` scale down |
| Disabled | `bg-gray-300` cursor-not-allowed |

### **Heart/Save Button**

| State | Style |
|-------|-------|
| Unsaved | `❤️ gray` |
| Saved | `❤️ red (#d32f2f)` |
| Hover | `bg-red-100` |

---

## 🔤 Typography System

### **Font Stack**
- **Headers (H1-H3):** Assistant (400/500/600/700) from Google Fonts
- **Body Text:** Rubik (300/400/500/700) from Google Fonts
- **Language:** Hebrew (עברית) with RTL support

### **Type Sizes**

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| H1 | 48px | 700 | Page title |
| H2 | 32px | 700 | Section heading |
| H3 | 24px | 600 | Card title |
| Body | 16px | 400 | Main text |
| Caption | 14px | 500 | Labels |
| Tiny | 12px | 600 | Tags, badges |

---

## 📊 Card Metrics

### **Venue Card Anatomy**
```
Total Height: 340px
Header: 120px (icon + gradient)
Content: 220px (padding + text)
Button Height: 40px
```

### **Spacing Rules**
```
Card Padding: 24px (p-6 in Tailwind)
Section Gap: 16px (mb-4)
Divider: 1px #E5E7EB
Icon Size: 48-64px
```

---

## 🎯 Conversion Optimization

### **CTA Button Strategy**
- Always visible above fold
- Minimum 44px height (mobile accessible)
- High contrast with background
- Icon + Text (not icon only, except heart)
- Primary action: "☎️ התקשר" (bold color)
- Secondary action: "❤️" (minimal, neutral)

### **Trust Signals**
- Show number of results
- Display location prominently
- Show price upfront (no hidden costs)
- Phone number visible (easy contact)
- Emoji icons = friendly, trustworthy

---

## 🚀 Implementation Checklist

- [x] Icon-based card layout implemented
- [x] Location badges in top-right corner
- [x] Icon + number stats row
- [x] Category/type badges
- [x] CTA buttons with phone link
- [x] Save/heart button
- [x] Responsive grid (3-2-1 columns)
- [x] Hover effects with shadow lift
- [x] Hebrew RTL text alignment
- [x] Cuisine type badges (catering)
- [ ] Add animation on page load
- [ ] Add filter functionality by type
- [ ] Add favorites/saved page
- [ ] Add booking modal

---

## 📸 Visual Examples

### **Clean Venue Card**
```
╔═════════════════════════╗
║         🏛️             ║
║     (120px header)      ║
╠═════════════════════════╣
║ אולם הזהב    📍 תל אביב ║
│                         │
│ 👥 עד 200      💰 5,000₪│
│                         │
│ 💎 בוהו                 │
│                         │
│ [☎️ התקשר] [❤️]         │
╚═════════════════════════╝
```

### **Clean Supplier Card**
```
╔═════════════════════════╗
║         🍽️             ║
║     (120px header)      ║
╠═════════════════════════╣
║ קייטרינג בשר  📍 תל אביב║
│                         │
│ [🍽️ קייטרינג]          │
│ [🥩 בשרי]              │
│                         │
│ 💰 תחיל מ-₪ 150        │
│                         │
│ [☎️ התקשר] [❤️]         │
╚═════════════════════════╝
```

---

## 📚 Resources

- **Typography:** [Google Fonts - Assistant & Rubik](https://fonts.google.com)
- **Icons:** Emojis (Unicode)
- **Colors:** Tailwind CSS (#800020 burgundy primary)
- **Framework:** Flask + Jinja2 + Tailwind CSS

---

**Last Updated:** December 25, 2025
**Version:** 1.0
**Author:** Design System
