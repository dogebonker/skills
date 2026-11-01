'use strict';

const { Notice, OverdueNotice } = require('./notices');

const DAY_MS = 24 * 60 * 60 * 1000;
const LOAN_DAYS = 21;
const FINE_PER_DAY = 0.25;
const MAX_FINE_PER_ITEM = 10;
const BLOCK_THRESHOLD = 15;
const RENEWAL_WINDOW_DAYS = 3;
const MAX_RENEWALS = 2;
const SEASONAL_LOAN_DAYS = { 6: 28, 7: 28, 12: 14 };

class HoldReadyNotice extends Notice {
  constructor(member, title) {
    super(member);
    this.title = title;
  }

  render() {
    return `${this.member.name}, "${this.title}" is waiting for you at the front desk`;
  }
}

function parseCatalogRecord(raw) {
  if (typeof raw !== 'object' || raw === null) throw new Error('catalog record is not an object');
  const title = typeof raw.title === 'string' ? raw.title.trim() : '';
  const year = typeof raw.pub_year === 'number' ? raw.pub_year : null;
  const authors = Array.isArray(raw.authors) ? raw.authors.filter((author) => typeof author === 'string') : [];
  const language = languageNames()[raw.lang] || 'Unknown';
  return { isbn: String(raw.isbn), title, year, authors, language, format: String(raw.format || 'print') };
}

function formatDueDate(date) {
  return date.toISOString().slice(0, 10);
}

function queueDepth(holds, isbn) {
  return holds.filter((hold) => hold.isbn === isbn).length;
}

function waitlistPosition(holds, isbn, memberId) {
  const queue = holds.filter((hold) => hold.isbn === isbn);
  return queue.findIndex((hold) => hold.memberId === memberId) + 1 || queueDepth(holds, isbn) + 1;
}

function estimatePickupDate(holds, isbn, today) {
  return new Date(today.getTime() + queueDepth(holds, isbn) * LOAN_DAYS * DAY_MS);
}

function seasonalLoanDays(month) {
  return SEASONAL_LOAN_DAYS[month] || LOAN_DAYS;
}

function isDigital(loan) {
  return loan.format.trim().toLowerCase() === 'ebook';
}

function runDailyCirculation(loans, members, today) {
  const memberById = new Map(members.map((member) => [member.id, member]));
  const problems = [];
  const active = [];
  for (const loan of loans) {
    if (!memberById.has(loan.memberId)) {
      problems.push(`loan ${loan.id} has no member`);
      continue;
    }
    if (loan.returnedAt) continue;
    active.push(loan);
  }
  const digitalCount = active.filter(isDigital).length;

  const overdue = [];
  for (const loan of active) {
    const daysLate = Math.floor((today - loan.dueDate) / DAY_MS);
    if (daysLate > 0) overdue.push({ loan, daysLate });
  }
  overdue.sort((a, b) => b.daysLate - a.daysLate);

  const fineByLoan = new Map();
  const finesByMember = new Map();
  for (const { loan, daysLate } of overdue) {
    if (loan.format === 'ebook') continue;
    const fine = Math.min(daysLate * FINE_PER_DAY, MAX_FINE_PER_ITEM);
    fineByLoan.set(loan.id, fine);
    finesByMember.set(loan.memberId, (finesByMember.get(loan.memberId) || 0) + fine);
  }
  const totalFines = [...finesByMember.values()].reduce((sum, fine) => sum + fine, 0);

  const blocked = [];
  for (const [memberId, fines] of finesByMember) {
    const member = memberById.get(memberId);
    if (member.balance + fines >= BLOCK_THRESHOLD) blocked.push(member.name);
  }

  const notices = [];
  for (const member of members) {
    const late = overdue.filter((entry) => entry.loan.memberId === member.id).map((entry) => entry.loan);
    if (late.length) notices.push(new OverdueNotice(member, late));
    for (const title of member.readyHolds) notices.push(new HoldReadyNotice(member, title));
  }
  const messages = notices.map((notice) => notice.render());

  const renewed = [];
  for (const loan of active) {
    const daysLeft = Math.ceil((loan.dueDate - today) / DAY_MS);
    if (daysLeft < 0 || daysLeft > RENEWAL_WINDOW_DAYS || loan.renewals >= MAX_RENEWALS) continue;
    const dueDate = new Date(loan.dueDate.getTime() + LOAN_DAYS * DAY_MS);
    renewed.push({ id: loan.id, renewals: loan.renewals + 1, dueDate });
  }

  const busiest = new Map();
  for (const loan of active) busiest.set(loan.title, (busiest.get(loan.title) || 0) + 1);
  const topTitles = [...busiest.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, 3)
    .map(([title, count]) => `${title} x${count}`);

  const summary = [
    `Circulation for ${today.toDateString()}`,
    `Active loans: ${active.length} (${digitalCount} digital)`,
    `Overdue: ${overdue.length}, fines raised: ${totalFines.toFixed(2)}`,
    `Renewed automatically: ${renewed.length}`,
    `Most borrowed: ${topTitles.join(', ') || 'none'}`,
  ];
  if (blocked.length) summary.push(`Borrowing blocked: ${blocked.join(', ')}`);
  for (const problem of problems) summary.push(`Check: ${problem}`);

  const exportRows = overdue.map(({ loan, daysLate }) => ({
    loan: loan.id,
    member: loan.memberId,
    days: daysLate,
    fine: fineByLoan.get(loan.id) || 0,
  }));
  return {
    summary,
    messages,
    renewed,
    exportRows,
    fines: Object.fromEntries(finesByMember),
  };
}

function languageNames() {
  return {
    en: 'English',
    fr: 'French',
    de: 'German',
    es: 'Spanish',
    it: 'Italian',
    pt: 'Portuguese',
    nl: 'Dutch',
    sv: 'Swedish',
    no: 'Norwegian',
    da: 'Danish',
    fi: 'Finnish',
    is: 'Icelandic',
    pl: 'Polish',
    cs: 'Czech',
    sk: 'Slovak',
    hu: 'Hungarian',
    ro: 'Romanian',
    bg: 'Bulgarian',
    el: 'Greek',
    ru: 'Russian',
    uk: 'Ukrainian',
    be: 'Belarusian',
    sr: 'Serbian',
    hr: 'Croatian',
    sl: 'Slovenian',
    bs: 'Bosnian',
    mk: 'Macedonian',
    sq: 'Albanian',
    lt: 'Lithuanian',
    lv: 'Latvian',
    et: 'Estonian',
    ga: 'Irish',
    cy: 'Welsh',
    gd: 'Scottish Gaelic',
    eu: 'Basque',
    ca: 'Catalan',
    gl: 'Galician',
    mt: 'Maltese',
    lb: 'Luxembourgish',
    tr: 'Turkish',
    ar: 'Arabic',
    he: 'Hebrew',
    fa: 'Persian',
    ur: 'Urdu',
    hi: 'Hindi',
    bn: 'Bengali',
    pa: 'Punjabi',
    gu: 'Gujarati',
    mr: 'Marathi',
    ta: 'Tamil',
    te: 'Telugu',
    kn: 'Kannada',
    ml: 'Malayalam',
    si: 'Sinhala',
    ne: 'Nepali',
    zh: 'Chinese',
    ja: 'Japanese',
    ko: 'Korean',
    vi: 'Vietnamese',
    th: 'Thai',
    lo: 'Lao',
    km: 'Khmer',
    my: 'Burmese',
    ms: 'Malay',
    id: 'Indonesian',
    tl: 'Tagalog',
    sw: 'Swahili',
    am: 'Amharic',
    yo: 'Yoruba',
    ig: 'Igbo',
    ha: 'Hausa',
    zu: 'Zulu',
    xh: 'Xhosa',
    af: 'Afrikaans',
    so: 'Somali',
    mn: 'Mongolian',
    kk: 'Kazakh',
    uz: 'Uzbek',
    hy: 'Armenian',
    ka: 'Georgian',
  };
}

if (require.main === module) {
  const ebook = parseCatalogRecord({ isbn: 9780141439518, title: ' Persuasion ', pub_year: 1817, authors: ['Jane Austen'], lang: 'en', format: 'ebook' });
  const novel = parseCatalogRecord({ isbn: 9789722036351, title: 'Ensaio sobre a Cegueira', lang: 'pt', format: ' eBook' });
  const members = [
    { id: 'M1', name: 'Ines', balance: 12, readyHolds: ['Dune'] },
    { id: 'M2', name: 'Tomas', balance: 0, readyHolds: [] },
  ];
  const loans = [
    { id: 'L1', memberId: 'M1', title: ebook.title, format: ebook.format, dueDate: new Date('2026-10-01'), renewals: 0, returnedAt: null },
    { id: 'L2', memberId: 'M1', title: novel.title, format: novel.format, dueDate: new Date('2026-10-10'), renewals: 1, returnedAt: null },
    { id: 'L3', memberId: 'M2', title: novel.title, format: 'print', dueDate: new Date('2026-11-03'), renewals: 0, returnedAt: null },
  ];
  const report = runDailyCirculation(loans, members, new Date('2026-11-01'));
  console.log(report.summary.join('\n'), report.messages, report.renewed, report.exportRows, report.fines, novel.language);
}
