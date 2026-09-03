/**
 * FIXED mongo-trade-agent Priority Canvas snippet.
 *
 * Agents MUST copy this file into a NEW uniquely named:
 *   ~/.cursor/projects/<workspace>/canvases/{horizon}-priority-{collection}-{YYYYMMDD-HHmmss}.canvas.tsx
 * then fill `meta`, `picks`, and `newsRows` only. Do not reinvent highlight helpers.
 *
 * HARD RULES (Cursor Canvas SDK):
 * - NEVER use <Pill tone="…"> for MLBuy / MLSell / news colours — tones are ignored (always neutral).
 * - ALWAYS colour with <Text style={{ backgroundColor: "…" }}> using the hex constants below.
 * - Import ONLY from "cursor/canvas". Embed all data inline (no fetch).
 * - When helper ml_buy / ml_sell is true, keep literal "MLBuy" / "MLSell" in whyParts (not paraphrased away).
 * - Sentiment cell: green when Bullish + positive news; red when Bearish + negative news (SentimentCell).
 */

import {
  Callout,
  Divider,
  H1,
  H2,
  Row,
  Stack,
  Table,
  Text,
} from "cursor/canvas";

/** Mandatory highlight colours — do not substitute theme tokens for these. */
const HL = {
  orangeRow: "#FFE4C4",
  mlBuy: "#C6F6D5",
  mlSell: "#FEB2B2",
  newsPos: "#C6F6D5",
  newsNeg: "#FEB2B2",
  newsMix: "#FEFCBF",
  /** #UpStairs / UpPostLunchConsolidation momentum highlight */
  upMomentum: "#C6F6D5",
  /** #DownStairs / DownPostLunchConsolidation breakdown highlight */
  downMomentum: "#FEB2B2",
} as const;

type NewsTone = "positive" | "negative" | "mixed" | "neutral";
type WhyKind = "text" | "mlbuy" | "mlsell";

type PickRow = {
  priority: number;
  /** Omit / leave "" for single-table boards */
  table?: string;
  symbol: string;
  lastDay: string;
  today: string;
  sentiment: string;
  conviction: string;
  prob: number;
  /**
   * Raw scan tags/filter strings joined — used to detect #UpStairs,
   * UpPostLunchConsolidation, #DownStairs, DownPostLunchConsolidation.
   */
  scanTags?: string;
  /** Parallel to whyText: "mlbuy" | "mlsell" | "text" */
  whyParts: WhyKind[];
  whyText: string[];
  /** true when buy&(LastDay|Today)>3 or sell&(LastDay|Today)<-3 */
  orange: boolean;
  /**
   * News tone for this symbol (same as newsRows.tone). Used to colour Sentiment:
   * Bullish + positive → green; Bearish + negative → red.
   */
  newsTone?: NewsTone;
};

type NewsRow = {
  table?: string;
  symbol: string;
  catalyst: string;
  tone: NewsTone;
  extend: string;
};

// ─── fill these per query ─────────────────────────────────────────────
const meta = {
  title: "Priority Picks — REPLACE_HORIZON",
  collections: "REPLACE_db.collection",
  generatedAt: "YYYY-MM-DD HH:mm IST",
  multiTable: false,
};

const picks: PickRow[] = [
  // Example — replace with real ranked rows from query_suggestions.py
  // {
  //   priority: 1,
  //   table: "buy_all_processor",
  //   symbol: "FORTIS",
  //   lastDay: "-0.7",
  //   today: "+3.8",
  //   sentiment: "Bullish",
  //   conviction: "Med",
  //   prob: 66,
  //   whyParts: ["mlbuy", "text"],
  //   whyText: ["", " + NearLowMo + UpMorningConsolidation; Q1 print · orange"],
  //   orange: true,
  //   newsTone: "positive",
  // },
];

const newsRows: NewsRow[] = [
  // {
  //   table: "buy_all_processor",
  //   symbol: "FORTIS",
  //   catalyst: "Q1 print summary ≤120 chars",
  //   tone: "positive",
  //   extend: "Possible",
  // },
];
// ─── end fill ─────────────────────────────────────────────────────────

const chipStyle = (bg: string) => ({
  backgroundColor: bg,
  padding: "1px 6px",
  borderRadius: 4,
  display: "inline-block" as const,
});

/** MLBuy / MLSell token — Text + backgroundColor only (never Pill tone). */
function MlToken({ kind }: { kind: "mlbuy" | "mlsell" }) {
  if (kind === "mlbuy") {
    return (
      <Text as="span" size="small" weight="semibold" style={chipStyle(HL.mlBuy)}>
        MLBuy
      </Text>
    );
  }
  return (
    <Text as="span" size="small" weight="semibold" style={chipStyle(HL.mlSell)}>
      MLSell
    </Text>
  );
}

function WhyCell({
  parts,
  texts,
  today,
}: {
  parts: WhyKind[];
  texts: string[];
  today: string;
}) {
  const todayNum = parseFloat(today ?? "0");
  return (
    <Row gap={4} style={{ flexWrap: "wrap", alignItems: "center" }}>
      {parts.map((p, i) => {
        if (p === "mlbuy") return <MlToken key={i} kind="mlbuy" />;
        if (p === "mlsell") return <MlToken key={i} kind="mlsell" />;
        return <MomentumWhyText key={i} text={texts[i] ?? ""} today={todayNum} />;
      })}
    </Row>
  );
}

/** Momentum keyword chip colour when Today% threshold is met; otherwise plain. */
function momentumKeywordBg(keyword: string, today: number): string | null {
  const k = keyword.toLowerCase();
  if (k.includes("uppostlunchconsolidation") && today > 3) return HL.upMomentum;
  if (k.includes("upstairs") && today > 2) return HL.upMomentum;
  if (k.includes("downpostlunchconsolidation") && today < -3) return HL.downMomentum;
  if (k.includes("downstairs") && today < -2) return HL.downMomentum;
  return null;
}

const MOMENTUM_KEYWORD_RE =
  /(UpPostLunchConsolidation(?::[\w-]+)?|#?UpStairs\b|DownPostLunchConsolidation(?::[\w-]+)?|#?DownStairs\b)/gi;

/** Colour only momentum keywords in Why text — not the whole row or scrip. */
function MomentumWhyText({ text, today }: { text: string; today: number }) {
  const segments: Array<{ text: string; bg?: string }> = [];
  let lastIndex = 0;
  const re = new RegExp(MOMENTUM_KEYWORD_RE.source, MOMENTUM_KEYWORD_RE.flags);
  let match: RegExpExecArray | null;
  while ((match = re.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ text: text.slice(lastIndex, match.index) });
    }
    const kw = match[0];
    const bg = momentumKeywordBg(kw, today);
    segments.push({ text: kw, bg: bg ?? undefined });
    lastIndex = re.lastIndex;
  }
  if (lastIndex < text.length) {
    segments.push({ text: text.slice(lastIndex) });
  }
  if (segments.length === 0) {
    return (
      <Text as="span" size="small">
        {text}
      </Text>
    );
  }
  return (
    <>
      {segments.map((seg, i) =>
        seg.bg ? (
          <Text
            key={i}
            as="span"
            size="small"
            weight="semibold"
            style={chipStyle(seg.bg)}
          >
            {seg.text}
          </Text>
        ) : (
          <Text key={i} as="span" size="small">
            {seg.text}
          </Text>
        )
      )}
    </>
  );
}

/** News catalyst cell — Text + backgroundColor by tone (never Pill tone). */
function NewsCell({ text, tone }: { text: string; tone: NewsTone }) {
  if (tone === "neutral" || !text || text === "No fresh news") {
    return <Text size="small">{text || "No fresh news"}</Text>;
  }
  const bg =
    tone === "positive" ? HL.newsPos : tone === "negative" ? HL.newsNeg : HL.newsMix;
  return (
    <Text as="span" size="small" style={chipStyle(bg)}>
      {text}
    </Text>
  );
}

function SymbolCell({ symbol, orange }: { symbol: string; orange: boolean }) {
  if (!orange) return <Text size="small">{symbol}</Text>;
  return (
    <Text as="span" size="small" weight="semibold" style={chipStyle(HL.orangeRow)}>
      {symbol}
    </Text>
  );
}

/**
 * Sentiment cell — green when Bullish + positive news; red when Bearish + negative news.
 * Otherwise plain text (Neutral / Mixed / mismatched news stay uncoloured).
 */
function SentimentCell({
  sentiment,
  newsTone,
}: {
  sentiment: string;
  newsTone?: NewsTone;
}) {
  const s = (sentiment || "").trim().toLowerCase();
  const n = (newsTone || "neutral").toLowerCase() as NewsTone;
  if (s === "bullish" && n === "positive") {
    return (
      <Text as="span" size="small" weight="semibold" style={chipStyle(HL.newsPos)}>
        {sentiment}
      </Text>
    );
  }
  if (s === "bearish" && n === "negative") {
    return (
      <Text as="span" size="small" weight="semibold" style={chipStyle(HL.newsNeg)}>
        {sentiment}
      </Text>
    );
  }
  return <Text size="small">{sentiment}</Text>;
}

function resolveNewsTone(p: PickRow): NewsTone | undefined {
  if (p.newsTone) return p.newsTone;
  const match = newsRows.find(
    (n) =>
      n.symbol === p.symbol &&
      (!meta.multiTable || !p.table || !n.table || n.table === p.table)
  );
  return match?.tone;
}

function buildWhyParts(mlBuy: boolean, mlSell: boolean, whyRest: string): {
  whyParts: WhyKind[];
  whyText: string[];
} {
  const whyParts: WhyKind[] = [];
  const whyText: string[] = [];
  if (mlBuy) {
    whyParts.push("mlbuy");
    whyText.push("");
  }
  if (mlSell) {
    whyParts.push("mlsell");
    whyText.push("");
  }
  whyParts.push("text");
  whyText.push(whyRest.startsWith(" ") || whyRest.startsWith("+") ? whyRest : ` ${whyRest}`);
  return { whyParts, whyText };
}
void buildWhyParts; // available for agents constructing picks from helper flags

export default function PriorityCanvasSnippet() {
  const multi = meta.multiTable;
  const headers = multi
    ? ["#", "Table", "Symbol", "LastDay%", "Today%", "Sent", "Conv", "Prob%", "Why"]
    : ["#", "Symbol", "LastDay%", "Today%", "Sent", "Conv", "Prob%", "Why"];

  const rows = picks.map((p) => {
    const why = <WhyCell parts={p.whyParts} texts={p.whyText} today={p.today} />;
    const sym = <SymbolCell symbol={p.symbol} orange={p.orange} />;
    const sent = (
      <SentimentCell sentiment={p.sentiment} newsTone={resolveNewsTone(p)} />
    );
    if (multi) {
      return [
        String(p.priority),
        p.table ?? "",
        sym,
        p.lastDay,
        p.today,
        sent,
        p.conviction,
        String(p.prob),
        why,
      ];
    }
    return [
      String(p.priority),
      sym,
      p.lastDay,
      p.today,
      sent,
      p.conviction,
      String(p.prob),
      why,
    ];
  });

  const rowTone = picks.map((p) => (p.orange ? ("warning" as const) : undefined));

  const newsHeaders = multi
    ? ["Table", "Symbol", "News catalyst", "May extend?"]
    : ["Symbol", "News catalyst", "May extend?"];
  const newsTableRows = newsRows.map((n) => {
    const cat = <NewsCell text={n.catalyst} tone={n.tone} />;
    if (multi) return [n.table ?? "", n.symbol, cat, n.extend];
    return [n.symbol, cat, n.extend];
  });

  return (
    <Stack gap={16} style={{ padding: 16 }}>
      <H1>{meta.title}</H1>
      <Text tone="secondary" size="small">
        {meta.collections} · as-of {meta.generatedAt}
      </Text>

      <Callout tone="neutral">
        Legend: orange Symbol chip / warning row-dot = buy &amp; (LastDay% or Today%
        &gt; 3) or sell &amp; (&lt; −3). MLBuy = green chip, MLSell = red chip. News
        catalyst: green / red / yellow by tone. Sentiment green when Bullish +
        positive news; Sentiment red when Bearish + negative news. Momentum
        keywords in Why: green chip on UpStairs (Today% &gt; 2) or
        UpPostLunchConsolidation (Today% &gt; 3); red chip on DownStairs
        (Today% &lt; −2) or DownPostLunchConsolidation (Today% &lt; −3).
        Colours use Text backgroundColor — never Pill tone.
      </Callout>

      <H2>Priority board</H2>
      <Table headers={headers} rows={rows} rowTone={rowTone} />

      {newsRows.length > 0 ? (
        <>
          <Divider />
          <H2>News &amp; Extension Snapshot</H2>
          <Table headers={newsHeaders} rows={newsTableRows} />
        </>
      ) : null}
    </Stack>
  );
}
