/* 东风日历 UI —— 单页，localStorage 持久化 */
(function () {
  'use strict';
  const C = Core;
  const $ = (s, el) => (el || document).querySelector(s);
  const LS = { get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { } } };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const nowFn = () => new Date();
  const ST = { pending: '待确认', confirmed: '已确认', rescheduled: '已改期' };
  const REP = { none: '不重复', daily: '每天', weekdays: '工作日', weekly: '每周', biweekly: '每两周', monthly: '每月', yearly: '每年' };

  // ---------- 状态 ----------
  const data = LS.get('dfc.v1', { events: [], settings: {} });
  const S = {
    events: data.events || [],
    settings: Object.assign({ theme: 'auto', reminders: C.DEFAULT_REMINDERS.slice() }, data.settings || {}),
    view: 'brief', sel: C.fmtDate(nowFn()), person: null, peopleQ: '',
    fired: LS.get('dfc.fired', {}), alerts: LS.get('dfc.alerts', []), snooze: LS.get('dfc.snooze', {}),
  };
  const save = () => { LS.set('dfc.v1', { events: S.events, settings: S.settings }); LS.set('dfc.fired', S.fired); LS.set('dfc.alerts', S.alerts); LS.set('dfc.snooze', S.snooze); };
  const byId = id => S.events.find(e => e.id === id);

  // ---------- 格式化 ----------
  const hm = d => C.pad(d.getHours()) + ':' + C.pad(d.getMinutes());
  const md = d => `${d.getMonth() + 1}月${d.getDate()}日`;
  const wk = d => '周' + C.WD[d.getDay()];
  function relDate(ds) {
    const n = C.dayNum(C.parseDate(ds)) - C.dayNum(nowFn());
    const lab = { '-2': '前天', '-1': '昨天', 0: '今天', 1: '明天', 2: '后天' }[n];
    const d = C.parseDate(ds);
    return (lab ? lab + ' ' : '') + md(d) + ' ' + wk(d);
  }
  const timeLabel = o => o.allDay ? '全天' : hm(o.start) + (o.ev.kind === 'event' ? '–' + hm(o.end) : '');
  function toast(msg, opt) {
    opt = opt || {}; const box = $('#toast'); const el = document.createElement('div');
    el.className = 't' + (opt.warn ? ' warn' : ''); el.innerHTML = `<span>${esc(msg)}</span>`;
    if (opt.action) { const b = document.createElement('button'); b.textContent = opt.action.label; b.onclick = () => { opt.action.fn(); el.remove(); }; el.appendChild(b); }
    while (box.children.length >= 3) box.firstChild.remove(); box.appendChild(el); setTimeout(() => el.remove(), opt.ms || 5000);
  }

  // ---------- 卡片 ----------
  function badge(st) { return `<span class="badge b-${st}">${ST[st]}</span>`; }
  function card(o, opt) {
    opt = opt || {}; const ev = o.ev; const isTask = ev.kind === 'task'; const cf = opt.conf && opt.conf[o.key];
    const past = !isTask && o.end < nowFn(); const cls = [isTask ? 'task' : ev.status, cf ? 'conflict' : '', past && !opt.noPast ? 'past' : '', o.done ? 'done' : ''].join(' ');
    const when = opt.showDate ? `<div class="time">${esc(relDate(o.date).replace(/ 周.$/, ''))}<br>${timeLabel(o)}</div>` : `<div class="time">${timeLabel(o)}</div>`;
    const meta = [];
    if (ev.who) meta.push(`<span>👤 ${esc(ev.who)}</span>`);
    if (ev.where) meta.push(`<span>📍 ${esc(ev.where)}</span>`);
    if (ev.repeat && ev.repeat !== 'none') meta.push(`<span>🔁 ${REP[ev.repeat]}</span>`);
    if (!isTask && (ev.reminders || []).length) meta.push(`<span>🔔 ${ev.reminders.slice().sort((a, b) => b - a).map(C.reminderLabel).join('/')}</span>`);
    if (cf) meta.push(`<span class="badge b-warn">⚠ 冲突：${esc(cf.map(x => x.ev.title).join('、'))}</span>`);
    let acts = '';
    if (!isTask && opt.actions !== false && !past && ev.status !== 'confirmed') acts = `<div class="acts"><button class="primary" data-act="confirm" data-id="${ev.id}">✓ 已确认</button><button data-act="resched" data-id="${ev.id}" data-date="${o.date}">改期</button></div>`;
    const lead = isTask ? `<button class="chk ${o.done ? 'on' : ''}" data-act="toggle" data-id="${ev.id}" data-date="${o.date}" aria-label="完成">${o.done ? '✓' : ''}</button>` : '';
    return `<div class="card ${cls}" data-card="${esc(o.key)}"><div class="row">${lead}${when}<div class="grow" data-act="edit" data-id="${ev.id}" data-date="${o.date}"><div class="ttl">${esc(ev.title)} ${isTask ? '' : badge(ev.status)}</div>${meta.length ? `<div class="meta">${meta.join('')}</div>` : ''}</div></div>${acts}</div>`;
  }
  const cardsOrEmpty = (occs, opt, empty) => occs.length ? occs.map(o => card(o, opt)).join('') : `<div class="empty">${empty}</div>`;

  // ---------- 简报 ----------
  function viewBrief() {
    const now = nowFn(), t = C.startOfDay(now), tm = C.addDays(t, 1);
    const pend = C.occurrencesInRange(S.events, t, C.addDays(t, 30)).filter(o => o.ev.kind === 'event' && o.ev.status !== 'confirmed' && o.end >= now);
    const fus = C.pendingFollowups(S.events, now, 14);
    const todays = C.occurrencesOn(S.events, t), tomos = C.occurrencesOn(S.events, tm);
    const conf = Object.assign({}, C.conflictMap(todays), C.conflictMap(tomos));
    const nEv = todays.filter(o => o.ev.kind === 'event').length, nTk = todays.filter(o => o.ev.kind === 'task' && !o.done).length;
    let h = `<div class="card" style="border-left-color:var(--brand2)"><div class="ttl">${esc(md(now))} ${wk(now)} · 今日简报</div><div class="meta"><span>${nEv} 件约定/日程</span><span>${nTk} 项待办</span><span>${pend.length} 件未确认</span><span>${fus.length} 件待跟进</span></div></div>`;
    if (!S.events.length) h += `<div class="card"><div class="ttl">还没有记录</div><div class="meta">在下方输入框写一句话，例如“周三下午3点和蒋宇飞喝咖啡”。</div><div class="acts"><button class="primary" data-act="seed">载入示例数据</button></div></div>`;
    h += `<h2>⏳ 待确认的约定 ${pend.length ? `<span class="n">${pend.length}</span>` : ''}</h2>` + cardsOrEmpty(pend, { showDate: true, conf: conflictAll(pend) }, '没有未确认的约定 👍');
    h += `<h2>📝 约后记一笔 ${fus.length ? `<span class="n">${fus.length}</span>` : ''}</h2>`;
    h += fus.length ? fus.map(followCard).join('') : `<div class="empty">没有待跟进的约定</div>`;
    h += `<h2>📅 今天</h2>` + cardsOrEmpty(todays, { conf }, '今天没有安排');
    h += `<h2>🌤 明天</h2>` + cardsOrEmpty(tomos, { conf }, '明天没有安排');
    return h;
  }
  function conflictAll(occs) { // 对列表中每个 occ 计算其当日冲突
    const m = {}; const days = [...new Set(occs.map(o => o.date))];
    for (const d of days) Object.assign(m, C.conflictMap(C.occurrencesOn(S.events, C.parseDate(d))));
    return m;
  }
  function followCard(o) {
    const ev = o.ev;
    return `<div class="card" style="border-left-color:var(--brand)" data-fu="${esc(o.key)}"><div class="ttl">${esc(ev.title)}</div><div class="meta"><span>${esc(relDate(o.date))} ${timeLabel(o)}</span>${ev.who ? `<span>👤 ${esc(ev.who)}</span>` : ''}</div><div class="meta" style="margin-top:6px">聊得如何？有什么要跟进 / 对方答应了什么？</div><textarea class="fu" rows="2" id="fu-${esc(o.key)}" placeholder="例如：对方下周发合同；我要回复报价"></textarea><div class="acts"><button class="primary" data-act="fu-save" data-id="${ev.id}" data-date="${o.date}">保存记录</button><button data-act="fu-skip" data-id="${ev.id}" data-date="${o.date}">无需跟进</button></div></div>`;
  }

  // ---------- 网格（日/周） ----------
  const minsOf = d => d.getHours() * 60 + d.getMinutes();
  function layout(occs) {
    const items = occs.filter(o => !o.allDay).map(o => { const s = minsOf(o.start); let e = Math.min(1440, s + Math.max(30, Math.round((o.end - o.start) / 60000))); return { o, s, e, col: 0, n: 1 }; }).sort((a, b) => a.s - b.s || a.e - b.e);
    let cluster = [], cEnd = -1; const flush = () => { const n = Math.max(...cluster.map(x => x.col)) + 1; cluster.forEach(x => x.n = n); cluster = []; };
    for (const it of items) {
      if (cluster.length && it.s >= cEnd) { flush(); cEnd = -1; }
      const used = cluster.filter(x => x.e > it.s).map(x => x.col); let c = 0; while (used.includes(c)) c++;
      it.col = c; cluster.push(it); cEnd = Math.max(cEnd, it.e);
    }
    if (cluster.length) flush();
    return items;
  }
  function gridHTML(dates, H, withTime) {
    const now = nowFn(); const todayS = C.fmtDate(now);
    let gut = ''; for (let h = 0; h < 24; h++) gut += `<div style="height:${H}px">${h ? C.pad(h) + ':00' : ''}</div>`;
    let cols = '';
    for (const d of dates) {
      const ds = C.fmtDate(d); const occs = C.occurrencesOn(S.events, d); const cm = C.conflictMap(occs);
      const items = layout(occs).map(it => {
        const o = it.o, ev = o.ev; const top = it.s / 60 * H, ht = Math.max(18, (it.e - it.s) / 60 * H - 1);
        const w = 100 / it.n; const cls = [ev.kind === 'task' ? 'task' : ev.status, cm[o.key] ? 'conflict' : ''].join(' ');
        return `<div class="ev ${cls}" data-act="edit" data-id="${ev.id}" data-date="${o.date}" style="top:${top}px;height:${ht}px;left:calc(${it.col * w}% + 1px);width:calc(${w}% - 2px)">${withTime ? `<b>${hm(o.start)}</b> ` : ''}${esc(ev.title)}</div>`;
      }).join('');
      const nowLine = ds === todayS ? `<div class="now" style="top:${minsOf(now) / 60 * H}px"></div>` : '';
      cols += `<div class="col" data-date="${ds}" style="height:${H * 24}px;background-image:repeating-linear-gradient(to bottom,var(--line) 0,var(--line) 1px,transparent 1px,transparent ${H}px)">${items}${nowLine}</div>`;
    }
    return `<div class="grid" id="grid" data-h="${H}"><div class="gutter">${gut}</div><div class="cols">${cols}</div></div>`;
  }
  function allDayBlock(dates) {
    const parts = dates.map(d => { const occs = C.occurrencesOn(S.events, d).filter(o => o.allDay); return occs.length ? (dates.length > 1 ? `<h2>${md(d)} ${wk(d)}</h2>` : '') + occs.map(o => card(o, { noPast: true })).join('') : ''; }).join('');
    return parts ? `<div class="allday"><h2>全天 / 待办</h2>${parts}</div>` : '';
  }
  function viewDay() {
    const d = C.parseDate(S.sel);
    const timedTasks = '';
    return allDayBlock([d]) + gridHTML([d], 52, true) + timedTasks;
  }
  function weekDates() { const d = C.parseDate(S.sel); const mon = C.addDays(d, -C.monIdx(d)); return [...Array(7)].map((_, i) => C.addDays(mon, i)); }
  function viewWeek() {
    const ds = weekDates(); const today = C.fmtDate(nowFn());
    const head = `<div class="wkhead">${ds.map(d => { const s = C.fmtDate(d); return `<div data-act="gotoday" data-date="${s}" class="${s === today ? 'today' : ''} ${s === S.sel ? 'sel' : ''}">周${C.WD[d.getDay()]}<br><b>${d.getDate()}</b></div>`; }).join('')}</div>`;
    return head + allDayBlock(ds) + gridHTML(ds, 44, false);
  }
  function viewMonth() {
    const sel = C.parseDate(S.sel); const first = new Date(sel.getFullYear(), sel.getMonth(), 1); const start = C.addDays(first, -C.monIdx(first));
    const end = C.addDays(start, 41); const occs = C.occurrencesInRange(S.events, start, end); const by = {};
    occs.forEach(o => (by[o.date] = by[o.date] || []).push(o));
    const today = C.fmtDate(nowFn());
    let cells = ['一', '二', '三', '四', '五', '六', '日'].map(x => `<div class="mh">${x}</div>`).join('');
    for (let i = 0; i < 42; i++) {
      const d = C.addDays(start, i), ds = C.fmtDate(d), list = by[ds] || [];
      const pills = list.slice(0, 2).map(o => `<span class="pill ${o.ev.kind === 'task' ? 'task' : o.ev.status}">${o.allDay ? '' : hm(o.start).replace(/^0/, '') + ' '}${esc(o.ev.title)}</span>`).join('') + (list.length > 2 ? `<span class="more">+${list.length - 2} 项</span>` : '');
      cells += `<div class="mc ${d.getMonth() !== sel.getMonth() ? 'out' : ''} ${ds === today ? 'today' : ''} ${ds === S.sel ? 'sel' : ''}" data-act="gotoday-m" data-date="${ds}"><div class="d"><b>${d.getDate()}</b></div>${pills}</div>`;
    }
    const dayOccs = C.occurrencesOn(S.events, sel);
    return `<div class="mgrid">${cells}</div><h2>${esc(relDate(S.sel))}</h2>` + cardsOrEmpty(dayOccs, { conf: C.conflictMap(dayOccs), noPast: true }, '这一天没有安排');
  }

  // ---------- 人物 ----------
  function peopleIndex() {
    const now = nowFn(); const map = {};
    for (const ev of S.events) for (const n of C.splitWho(ev.who)) {
      const p = map[n] = map[n] || { name: n, evs: [], up: 0, past: 0, pend: 0, next: null };
      p.evs.push(ev);
    }
    const from = C.addDays(now, -365), to = C.addDays(now, 365);
    for (const o of C.occurrencesInRange(S.events.filter(e => e.who), from, to)) for (const n of C.splitWho(o.ev.who)) {
      const p = map[n]; if (!p) continue;
      if (o.end >= now) { p.up++; if (!p.next || o.start < p.next.start) p.next = o; if (o.ev.status !== 'confirmed' && o.ev.kind === 'event') p.pend++; } else p.past++;
    }
    return Object.values(map).sort((a, b) => (a.next ? 0 : 1) - (b.next ? 0 : 1) || (a.next && b.next ? a.next.start - b.next.start : 0) || a.name.localeCompare(b.name));
  }
  function viewPeople() {
    if (S.person) return viewPerson(S.person);
    const q = S.peopleQ.trim().toLowerCase(); const list = peopleIndex().filter(p => !q || p.name.toLowerCase().includes(q));
    let h = `<div class="f"><input id="pq" type="search" placeholder="搜索人名" value="${esc(S.peopleQ)}"></div>`;
    if (!list.length) return h + `<div class="empty">还没有“约了谁”的记录。<br>记约定时带上“和某某”，这里会自动按人归档。</div>`;
    return h + `<div class="people">` + list.map(p => `<div class="card p" data-act="person" data-name="${esc(p.name)}"><div class="avatar">${esc([...p.name][0])}</div><div class="grow"><div class="ttl">${esc(p.name)}</div><div class="meta"><span>即将 ${p.up}</span><span>历史 ${p.past}</span>${p.pend ? `<span class="badge b-pending">待确认 ${p.pend}</span>` : ''}${p.next ? `<span>下次：${esc(relDate(p.next.date))} ${timeLabel(p.next)}</span>` : ''}</div></div></div>`).join('') + `</div>`;
  }
  function viewPerson(name) {
    const now = nowFn();
    const evs = S.events.filter(e => C.splitWho(e.who).includes(name));
    let occs = C.occurrencesInRange(evs, C.addDays(now, -365), C.addDays(now, 365));
    // 重复事件每个系列最多保留：最近 5 次已发生 + 未来 3 次
    const keep = []; const per = {};
    for (const o of occs) (per[o.ev.id] = per[o.ev.id] || []).push(o);
    for (const id in per) { const a = per[id]; const past = a.filter(o => o.end < now).slice(-5), up = a.filter(o => o.end >= now).slice(0, 3); keep.push(...past, ...up); }
    const upcoming = keep.filter(o => o.end >= now).sort((a, b) => a.start - b.start), past = keep.filter(o => o.end < now).sort((a, b) => b.start - a.start);
    let h = `<div class="acts"><button data-act="person-back">‹ 全部人物</button><button class="primary" data-act="person-new" data-name="${esc(name)}">＋ 约 ${esc(name)}</button></div><div class="card p" style="margin-top:10px"><div class="avatar">${esc([...name][0])}</div><div class="grow"><div class="ttl">${esc(name)}</div><div class="meta"><span>共 ${evs.length} 条约定</span><span>即将 ${upcoming.length}</span><span>历史 ${past.length}</span></div></div></div>`;
    h += `<h2>即将到来</h2>` + cardsOrEmpty(upcoming, { showDate: true, conf: conflictAll(upcoming) }, '暂无即将到来的约定');
    h += `<h2>历史约定</h2>` + (past.length ? past.map(o => {
      const note = o.ev.followups && o.ev.followups[o.date];
      return card(o, { showDate: true, actions: false, noPast: true }).replace(/<\/div>$/, (note && note !== '__skip' ? `<div class="note">📝 ${esc(note)}</div>` : '') + '</div>');
    }).join('') : `<div class="empty">还没有历史记录</div>`);
    return h;
  }

  // ---------- 渲染 ----------
  let lastScroll = '';
  function render() {
    document.documentElement.dataset.theme = S.settings.theme;
    $('#main').innerHTML = ({ brief: viewBrief, day: viewDay, week: viewWeek, month: viewMonth, people: viewPeople })[S.view]();
    document.querySelectorAll('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.view === S.view));
    const d = C.parseDate(S.sel);
    const nav = $('#nav');
    if (['day', 'week', 'month'].includes(S.view)) nav.innerHTML = `<button data-act="prev">‹</button><button data-act="today">今天</button><button data-act="next">›</button>`; else nav.innerHTML = '';
    $('#subtitle').textContent = S.view === 'month' ? `${d.getFullYear()}年${d.getMonth() + 1}月` : S.view === 'week' ? (() => { const w = weekDates(); return `${md(w[0])} – ${md(w[6])}`; })() : S.view === 'day' ? `${md(d)} ${wk(d)}` : S.view === 'people' ? '约了谁' : `${md(nowFn())} ${wk(nowFn())}`;
    updateBadge(); renderAlerts();
    const sk = S.view + S.sel; if ((S.view === 'day' || S.view === 'week') && sk !== lastScroll) { lastScroll = sk; const g = $('#grid'); if (g) { const H = +g.dataset.h; const nowM = minsOf(nowFn()); const target = Math.max(0, (C.fmtDate(nowFn()) === S.sel || S.view === 'week' ? Math.max(6 * 60, nowM - 90) : 7 * 60) / 60 * H); window.scrollTo(0, g.getBoundingClientRect().top + window.scrollY + target - 90); } }
  }
  function pendingCount() { const t = C.startOfDay(nowFn()), now = nowFn(); return C.occurrencesInRange(S.events, t, C.addDays(t, 30)).filter(o => o.ev.kind === 'event' && o.ev.status !== 'confirmed' && o.end >= now).length + C.pendingFollowups(S.events, now, 14).length; }
  function updateBadge() { const n = pendingCount(); const b = $('#badge'); b.textContent = n; b.classList.toggle('show', n > 0); const na = S.alerts.length; document.title = (na ? `(${na}) 🔔 ` : n ? `(${n}) ` : '') + '东风日历'; }

  // ---------- 提醒 ----------
  function addAlert(a) { if (S.alerts.some(x => x.key === a.key && x.kind === a.kind)) return; S.alerts.push(a); notifySys(a); beep(); }
  function alertText(a) {
    const ev = byId(a.evId); if (!ev) return null; const o = C.makeOcc(ev, a.date); const now = nowFn();
    if (a.kind === 'follow') return { title: `约后记一笔：${ev.title}`, body: `${relDate(a.date)} ${timeLabel(o)} 已结束${ev.who ? '，和' + ev.who + '聊得如何？' : ''} 记一下结论和要跟进的事。` };
    const diff = Math.round((C.reminderTime(o, 0) - now) / 60000); const when = diff > 1440 * 1.5 ? `${Math.round(diff / 1440)}天后` : diff >= 120 ? `${Math.round(diff / 60)}小时后` : diff > 0 ? `${diff}分钟后` : diff > -5 ? '现在' : `已开始${-diff}分钟`;
    return { title: `${C.reminderLabel(a.offset)}提醒：${ev.title}`, body: `${when} · ${relDate(a.date)} ${timeLabel(o)}${ev.where ? ' · 📍' + ev.where : ''}${ev.who ? ' · 👤' + ev.who : ''}${ev.status !== 'confirmed' && ev.kind === 'event' ? ' · ⚠' + ST[ev.status] : ''}` };
  }
  function renderAlerts() {
    S.alerts = S.alerts.filter(a => byId(a.evId));
    const html = S.alerts.map((a, i) => {
      const t = alertText(a); const ev = byId(a.evId);
      if (a.kind === 'follow') return `<div class="alert follow" data-alert="${i}"><b>📝 ${esc(t.title)}</b>${esc(t.body)}<div class="acts"><button data-act="alert-follow" data-i="${i}">去记录</button><button data-act="alert-ack" data-i="${i}">稍后</button></div></div>`;
      return `<div class="alert" data-alert="${i}"><b>🔔 ${esc(t.title)}</b>${esc(t.body)}<div class="acts"><button data-act="alert-ack" data-i="${i}">知道了</button>${ev.kind === 'event' && ev.status !== 'confirmed' ? `<button data-act="alert-confirm" data-i="${i}">✓ 已确认</button>` : ''}<button data-act="alert-snooze" data-i="${i}">10分钟后再提醒</button><button data-act="alert-open" data-i="${i}">查看</button></div></div>`;
    }).join('');
    const html2 = S.alerts.length > 1 ? html + `<div class="alert allack"><button data-act="alert-all">全部知道了（${S.alerts.length}）</button></div>` : html;
    const box = $('#alerts'); if (box.dataset.h !== html2) { box.innerHTML = html2; box.dataset.h = html2; }
  }
  function notifySys(a) {
    try { if ('Notification' in window && Notification.permission === 'granted') { const t = alertText(a); if (t) new Notification('东风日历 · ' + t.title, { body: t.body, tag: a.key + a.kind, requireInteraction: true }); } } catch (e) { }
  }
  let actx; function beep() { try { actx = actx || new (window.AudioContext || window.webkitAudioContext)(); const o = actx.createOscillator(), g = actx.createGain(); o.connect(g); g.connect(actx.destination); o.frequency.value = 880; g.gain.value = .08; o.start(); o.stop(actx.currentTime + .25); } catch (e) { } }
  function tick() {
    const now = nowFn(); const t = now.getTime();
    for (const d of C.dueReminders(S.events, now, S.fired)) { S.fired[d.key] = t; addAlert({ key: d.key, kind: 'remind', evId: d.occ.ev.id, date: d.occ.date, offset: d.offset }); }
    for (const k of Object.keys(S.snooze)) if (S.snooze[k].until <= t) { const a = S.snooze[k]; delete S.snooze[k]; if (byId(a.evId)) addAlert({ key: a.key + '#s' + t, kind: 'remind', evId: a.evId, date: a.date, offset: 0 }); }
    for (const o of C.pendingFollowups(S.events, now, 1)) { const k = 'fu|' + o.key; if (!S.fired[k]) { S.fired[k] = t; addAlert({ key: k, kind: 'follow', evId: o.ev.id, date: o.date, offset: 0 }); } }
    for (const k of Object.keys(S.fired)) if (t - S.fired[k] > 30 * 86400000) delete S.fired[k];
    save(); updateBadge(); renderAlerts();
  }

  // ---------- 编辑器 ----------
  let ed = null; // {orig, draft, newFlag, delChoice}
  const sheet = $('#sheet');
  function closeSheet() { sheet.classList.add('hidden'); sheet.innerHTML = ''; ed = null; }
  function openEditor(ev, date, opt) {
    opt = opt || {}; const now = nowFn();
    let draft;
    if (ev) draft = JSON.parse(JSON.stringify(ev));
    else draft = C.buildEvent(Object.assign({ kind: 'event', date: date || S.sel, time: '', dur: 60 }, opt.draft || {}), { reminders: S.settings.reminders });
    if (!ev && !(opt.draft && 'time' in opt.draft)) { const isToday = draft.date === C.fmtDate(now); draft.time = isToday ? C.pad(Math.min(23, now.getHours() + 1)) + ':00' : '09:00'; }
    ed = { orig: ev ? JSON.parse(JSON.stringify(ev)) : null, d: draft, occDate: date || draft.date, forceResched: !!opt.resched, delChoice: false };
    drawEditor(); sheet.classList.remove('hidden');
    if (opt.resched) { const el = $('#f-date'); el && el.focus(); }
  }
  function formVal(id) { const el = $('#' + id); return el ? el.value : ''; }
  function syncForm() {
    if (!ed || !$('#f-title')) return; const d = ed.d;
    d.title = formVal('f-title').trim(); d.who = formVal('f-who').trim(); d.date = formVal('f-date') || d.date; d.notes = formVal('f-notes');
    if (d.kind === 'event') { d.where = formVal('f-where').trim(); d.status = formVal('f-status') || d.status; d.dur = +formVal('f-dur') || d.dur; d.followup = $('#f-fu').checked; }
    d.repeat = formVal('f-repeat') || 'none'; d.until = d.repeat === 'none' ? '' : formVal('f-until');
    d.time = $('#f-allday').checked ? '' : (formVal('f-time') || d.time || '09:00');
  }
  function drawEditor() {
    const d = ed.d, isEv = d.kind === 'event', isNew = !ed.orig;
    const remChips = [1440, 120, 60, 15, 0].map(v => `<button type="button" class="${(d.reminders || []).includes(v) ? 'on' : ''}" data-act="rem" data-v="${v}">${C.reminderLabel(v)}</button>`).join('');
    const confl = C.findConflicts(S.events, d);
    sheet.innerHTML = `<div class="panel" role="dialog" aria-label="${isNew ? '新建' : '编辑'}"><h3>${isNew ? '新建' : '编辑'}${isEv ? '约定 / 日程' : '待办'}</h3>
    <div class="seg"><button type="button" class="${isEv ? 'on' : ''}" data-act="kind" data-v="event">约定 / 日程</button><button type="button" class="${!isEv ? 'on' : ''}" data-act="kind" data-v="task">待办</button></div>
    <label class="f"><span>标题</span><input id="f-title" value="${esc(d.title)}" placeholder="${isEv ? '例如：和蒋宇飞喝咖啡' : '例如：回复报价'}"></label>
    <label class="f"><span>约了谁（多人用“、”分隔）</span><input id="f-who" value="${esc(d.who)}" placeholder="蒋宇飞"></label>
    ${isEv ? `<label class="f"><span>地点</span><input id="f-where" value="${esc(d.where)}" placeholder="国贸星巴克"></label>` : ''}
    <div class="f2"><label class="f"><span>日期</span><input id="f-date" type="date" value="${esc(d.date)}"></label>
    <label class="f"><span>时间</span><input id="f-time" type="time" value="${esc(d.time || '')}" ${d.time ? '' : 'disabled'}></label></div>
    <label class="f" style="display:flex;gap:8px;align-items:center"><input id="f-allday" type="checkbox" style="width:auto" ${d.time ? '' : 'checked'}> <span style="margin:0">全天 / 未定具体时间</span></label>
    ${isEv ? `<div class="f2"><label class="f"><span>时长</span><select id="f-dur">${[15, 30, 45, 60, 90, 120, 180, 240].map(v => `<option value="${v}" ${+d.dur === v ? 'selected' : ''}>${v >= 60 ? v / 60 + ' 小时' : v + ' 分钟'}</option>`).join('')}${[15, 30, 45, 60, 90, 120, 180, 240].includes(+d.dur) ? '' : `<option value="${d.dur}" selected>${d.dur} 分钟</option>`}</select></label>
    <label class="f"><span>状态</span><select id="f-status">${Object.keys(ST).map(k => `<option value="${k}" ${d.status === k ? 'selected' : ''}>${ST[k]}</option>`).join('')}</select></label></div>` : ''}
    <div class="f2"><label class="f"><span>重复</span><select id="f-repeat">${Object.keys(REP).map(k => `<option value="${k}" ${d.repeat === k ? 'selected' : ''}>${REP[k]}</option>`).join('')}</select></label>
    <label class="f" ${d.repeat === 'none' ? 'hidden' : ''}><span>重复截止（可空）</span><input id="f-until" type="date" value="${esc(d.until || '')}"></label></div>
    <div class="f"><span>提醒（可多选）</span><div class="chips">${remChips}</div></div>
    ${isEv ? `<label class="f" style="display:flex;gap:8px;align-items:center"><input id="f-fu" type="checkbox" style="width:auto" ${d.followup ? 'checked' : ''}> <span style="margin:0">结束后提醒我“约后记一笔”</span></label>` : ''}
    <label class="f"><span>备注</span><textarea id="f-notes" rows="2">${esc(d.notes)}</textarea></label>
    <div id="conf">${confl.length ? `<div class="conflictbox">⚠ 时间冲突：${confl.map(o => `「${esc(o.ev.title)}」${esc(relDate(o.date))} ${timeLabel(o)}`).join('；')}</div>` : ''}</div>
    ${ed.delChoice ? `<div class="conflictbox">这是重复事件，删除哪些？<div class="acts"><button class="danger" data-act="del-one">仅此次（${esc(ed.occDate)}）</button><button class="danger" data-act="del-all">整个系列</button><button data-act="del-cancel">取消</button></div></div>` : ''}
    <div class="sheetbtns"><button class="primary" data-act="save" id="f-save">${confl.length ? '仍然保存（有冲突）' : '保存'}</button>${isNew ? '' : `<button class="danger" data-act="del">删除</button>`}<button data-act="close">取消</button></div></div>`;
  }
  function liveConflict() { syncForm(); const confl = C.findConflicts(S.events, ed.d); $('#conf').innerHTML = confl.length ? `<div class="conflictbox">⚠ 时间冲突：${confl.map(o => `「${esc(o.ev.title)}」${esc(relDate(o.date))} ${timeLabel(o)}`).join('；')}</div>` : ''; $('#f-save').textContent = confl.length ? '仍然保存（有冲突）' : '保存'; }
  function saveEditor() {
    syncForm(); const d = ed.d, o = ed.orig;
    if (!d.title) { if (d.who && d.kind === 'event') d.title = `和${d.who}见面`; else { toast('请先填写标题', { warn: true }); return; } }
    if (!d.date) { toast('请选择日期', { warn: true }); return; }
    if (d.kind === 'task') { d.status = 'confirmed'; d.followup = false; }
    const confl = C.findConflicts(S.events, d);
    let changedTime = false;
    if (o) {
      changedTime = o.date !== d.date || o.time !== d.time;
      if (changedTime && d.kind === 'event' && d.who && d.status === o.status && d.status !== 'rescheduled') d.status = 'rescheduled';
      if (changedTime) for (const k of Object.keys(S.fired)) if (k.startsWith(d.id + '@')) delete S.fired[k];
      const i = S.events.findIndex(e => e.id === d.id); S.events[i] = d;
    } else S.events.push(d);
    if (!o || changedTime || JSON.stringify(o.reminders) !== JSON.stringify(d.reminders)) C.markPastFired(d, nowFn(), S.fired);
    save(); closeSheet(); S.sel = d.date; render(); tick();
    toast(`已保存：${d.title}${changedTime && d.status === 'rescheduled' ? '（已标记为已改期，记得和对方确认）' : ''}`);
    if (confl.length) toast(`⚠ 与「${confl.map(x => x.ev.title).join('、')}」时间冲突`, { warn: true, ms: 9000 });
  }
  function deleteEv(ev, mode, ds) {
    const snap = JSON.parse(JSON.stringify(S.events));
    if (mode === 'one') { ev.exceptions = ev.exceptions || []; ev.exceptions.push(ds); } else S.events = S.events.filter(e => e.id !== ev.id);
    save(); closeSheet(); render(); tick();
    toast(mode === 'one' ? '已删除此次' : '已删除', { action: { label: '撤销', fn: () => { S.events = snap; save(); render(); } } });
  }

  // ---------- 快速记录 ----------
  const q = $('#q');
  function previewHTML(text) {
    if (!text.trim()) return '';
    const r = C.parse(text, nowFn()); const chips = [];
    chips.push(r.kind === 'task' ? '☑ 待办' : '📅 约定');
    chips.push(esc(C.describe(r)) + (r.noDate ? '（未识别日期，默认今天）' : ''));
    if (r.who) chips.push('👤 ' + esc(r.who)); if (r.where) chips.push('📍 ' + esc(r.where));
    if (r.repeat !== 'none') chips.push('🔁 ' + REP[r.repeat]); if (r.kind === 'event' && r.time && r.dur !== 60) chips.push('⏱ ' + r.dur + '分钟');
    if (r.kind === 'event') chips.push(ST[r.status]);
    const cf = C.findConflicts(S.events, { kind: r.kind, date: r.date, time: r.time, dur: r.dur || 60, repeat: r.repeat });
    let h = `<span class="chip"><b>${esc(r.title || '（无标题）')}</b></span>` + chips.map(c => `<span class="chip">${c}</span>`).join('');
    if (cf.length) h += `<span class="chip badge b-warn">⚠ 与「${esc(cf.map(o => o.ev.title).join('、'))}」冲突</span>`;
    return h;
  }
  q.addEventListener('input', () => { $('#preview').innerHTML = previewHTML(q.value); });
  $('#quick').addEventListener('submit', e => {
    e.preventDefault(); const text = q.value.trim(); if (!text) return;
    const r = C.parse(text, nowFn());
    if (!r.title) { toast('没读懂标题，换个说法试试，或点＋手动新建', { warn: true }); return; }
    const ev = C.buildEvent({ kind: r.kind, title: r.title, who: r.who, where: r.where, date: r.date, time: r.time, dur: r.dur || 60, repeat: r.repeat, status: r.status, followup: r.kind === 'event' && !!r.who, reminders: r.kind === 'event' ? S.settings.reminders.slice() : [0] });
    const confl = C.findConflicts(S.events, ev);
    S.events.push(ev); C.markPastFired(ev, nowFn(), S.fired); save();
    q.value = ''; $('#preview').innerHTML = ''; S.sel = ev.date; render(); tick();
    toast(`已记下：${C.describe(r)} ${ev.title}${ev.status === 'pending' ? ' · 待确认' : ''}`, { action: { label: '撤销', fn: () => { S.events = S.events.filter(x => x.id !== ev.id); save(); render(); } }, ms: 6000 });
    if (confl.length) toast(`⚠ 与「${confl.map(o => o.ev.title).join('、')}」时间冲突，请检查`, { warn: true, ms: 10000 });
  });

  // ---------- 设置 / 数据 ----------
  function download(name, text, mime) { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: mime })); a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  function openSettings() {
    const perm = 'Notification' in window ? Notification.permission : 'unsupported';
    sheet.innerHTML = `<div class="panel" role="dialog" aria-label="设置"><h3>设置</h3>
    <div class="f"><span>外观</span><div class="seg">${[['auto', '跟随系统'], ['light', '浅色'], ['dark', '深色']].map(([k, l]) => `<button class="${S.settings.theme === k ? 'on' : ''}" data-act="theme" data-v="${k}">${l}</button>`).join('')}</div></div>
    <div class="f"><span>新约定默认提醒</span><div class="chips">${[1440, 120, 60, 15, 0].map(v => `<button class="${S.settings.reminders.includes(v) ? 'on' : ''}" data-act="defrem" data-v="${v}">${C.reminderLabel(v)}</button>`).join('')}</div></div>
    <div class="f"><span>系统通知（页面打开时有效；页内醒目提醒始终可用）</span><div class="acts"><button data-act="perm">${perm === 'granted' ? '✓ 已开启' : perm === 'denied' ? '已被浏览器拒绝' : perm === 'unsupported' ? '浏览器不支持' : '开启通知'}</button><button data-act="testalert">测试提醒</button></div></div>
    <div class="f"><span>数据（仅保存在本机浏览器）</span><div class="acts"><button class="primary" data-act="ics">导出 .ics 日历</button><button data-act="exportjson">备份 JSON</button><button data-act="importjson">导入 JSON</button><button data-act="seed">载入示例数据</button><button class="danger" data-act="wipe">清空全部</button></div></div>
    <input id="importfile" type="file" accept="application/json" hidden>
    <div class="sheetbtns"><button class="primary" data-act="close">完成</button></div></div>`;
    sheet.classList.remove('hidden');
  }
  function seed() {
    const now = nowFn(); const phrases = ['明天下午3点和蒋宇飞喝咖啡在国贸星巴克', '明天下午3点半开会评审方案', '周五晚上7点和老王吃饭在三里屯', '每周一早上9点站会', '提醒我明天交报告', '后天上午10点和陈医生复诊 已确认', '下周三下午2点半和张总电话沟通 待确认'];
    for (const p of phrases) { const r = C.parse(p, now); const ev = C.buildEvent({ kind: r.kind, title: r.title, who: r.who, where: r.where, date: r.date, time: r.time, dur: r.dur || 60, repeat: r.repeat, status: r.status, followup: r.kind === 'event' && !!r.who, reminders: r.kind === 'event' ? S.settings.reminders.slice() : [0] }); S.events.push(ev); C.markPastFired(ev, now, S.fired); }
    const y = C.fmtDate(C.addDays(now, -1));
    S.events.push(C.buildEvent({ kind: 'event', title: '和刘总开会', who: '刘总', where: '公司', date: y, time: '10:00', dur: 60, status: 'confirmed', followup: true, reminders: [15] }));
    save(); closeSheet(); render(); tick(); toast('已载入示例数据');
  }

  // ---------- 事件委托 ----------
  function shift(n) {
    const d = C.parseDate(S.sel);
    if (S.view === 'day') S.sel = C.fmtDate(C.addDays(d, n)); else if (S.view === 'week') S.sel = C.fmtDate(C.addDays(d, 7 * n));
    else { const t = new Date(d.getFullYear(), d.getMonth() + n, 1); const last = new Date(t.getFullYear(), t.getMonth() + 1, 0).getDate(); S.sel = C.fmtDate(new Date(t.getFullYear(), t.getMonth(), Math.min(d.getDate(), last))); }
    render();
  }
  document.addEventListener('click', e => {
    const tab = e.target.closest('#tabs button'); if (tab) { S.view = tab.dataset.view; S.person = null; lastScroll = ''; render(); if (S.view !== 'day' && S.view !== 'week') window.scrollTo(0, 0); return; }
    const col = e.target.closest('.col');
    if (col && !e.target.closest('.ev')) { const g = $('#grid'); const H = +g.dataset.h; const y = e.clientY - col.getBoundingClientRect().top; const hr = Math.max(0, Math.min(23, Math.floor(y / H))); openEditor(null, col.dataset.date, { draft: { date: col.dataset.date, time: C.pad(hr) + ':00' } }); return; }
    const b = e.target.closest('[data-act]'); if (!b) { if (e.target === sheet) closeSheet(); return; }
    const a = b.dataset.act, id = b.dataset.id, ds = b.dataset.date, i = +b.dataset.i;
    switch (a) {
      case 'prev': shift(-1); break; case 'next': shift(1); break;
      case 'today': S.sel = C.fmtDate(nowFn()); render(); break;
      case 'gotoday': S.sel = ds; S.view = 'day'; render(); break;
      case 'gotoday-m': S.sel = ds; render(); break;
      case 'new': openEditor(null, ['day', 'week', 'month'].includes(S.view) ? S.sel : C.fmtDate(nowFn()), { draft: q.value.trim() ? (() => { const r = C.parse(q.value, nowFn()); return { kind: r.kind, title: r.title, who: r.who, where: r.where, date: r.date, time: r.time, dur: r.dur || 60, repeat: r.repeat, status: r.status, followup: !!r.who && r.kind === 'event' }; })() : undefined }); break;
      case 'edit': { const ev = byId(id); if (ev) openEditor(ev, ds); break; }
      case 'toggle': { const ev = byId(id); ev.doneOcc = ev.doneOcc || {}; if (ev.doneOcc[ds]) delete ev.doneOcc[ds]; else ev.doneOcc[ds] = true; save(); render(); break; }
      case 'confirm': { const ev = byId(id); ev.status = 'confirmed'; save(); render(); toast(`已确认：${ev.title}`); break; }
      case 'resched': { const ev = byId(id); openEditor(ev, ds, { resched: true }); break; }
      case 'fu-save': { const ev = byId(id); const t = $('[id="fu-' + id + '@' + ds + '"]'); ev.followups = ev.followups || {}; ev.followups[ds] = (t && t.value.trim()) || '（已跟进）'; S.alerts = S.alerts.filter(x => !(x.kind === 'follow' && x.evId === id && x.date === ds)); save(); render(); toast('已记录，可在“人物”里按人查看'); break; }
      case 'fu-skip': { const ev = byId(id); ev.followups = ev.followups || {}; ev.followups[ds] = '__skip'; S.alerts = S.alerts.filter(x => !(x.kind === 'follow' && x.evId === id && x.date === ds)); save(); render(); break; }
      case 'alert-all': S.alerts = S.alerts.filter(a => a.kind === 'follow'); save(); render(); break;
      case 'alert-ack': S.alerts.splice(i, 1); save(); render(); break;
      case 'alert-confirm': { const al = S.alerts[i]; const ev = byId(al.evId); ev.status = 'confirmed'; S.alerts.splice(i, 1); save(); render(); toast(`已确认：${ev.title}`); break; }
      case 'alert-snooze': { const al = S.alerts[i]; S.snooze[al.key] = { until: nowFn().getTime() + 10 * 60000, evId: al.evId, date: al.date, key: al.key }; S.alerts.splice(i, 1); save(); render(); toast('10分钟后再提醒你'); break; }
      case 'alert-open': { const al = S.alerts[i]; openEditor(byId(al.evId), al.date); break; }
      case 'alert-follow': S.alerts.splice(i, 1); S.view = 'brief'; save(); render(); window.scrollTo(0, 0); break;
      case 'person': S.person = b.dataset.name; render(); window.scrollTo(0, 0); break;
      case 'person-back': S.person = null; render(); break;
      case 'person-new': q.value = '和' + b.dataset.name; q.focus(); q.dispatchEvent(new Event('input')); break;
      case 'settings': openSettings(); break;
      case 'close': closeSheet(); break;
      case 'kind': syncForm(); ed.d.kind = b.dataset.v; if (ed.d.kind === 'task' && (ed.d.reminders || []).length > 1) ed.d.reminders = [0]; drawEditor(); break;
      case 'rem': { syncForm(); const v = +b.dataset.v; const r = new Set(ed.d.reminders || []); r.has(v) ? r.delete(v) : r.add(v); ed.d.reminders = [...r].sort((x, y) => y - x); drawEditor(); break; }
      case 'save': saveEditor(); break;
      case 'del': { const ev = byId(ed.d.id); if (!ev) break; syncForm(); if (ev.repeat && ev.repeat !== 'none') { ed.delChoice = true; drawEditor(); } else deleteEv(ev, 'all', ed.occDate); break; }
      case 'del-one': deleteEv(byId(ed.d.id), 'one', ed.occDate); break;
      case 'del-all': deleteEv(byId(ed.d.id), 'all', ed.occDate); break;
      case 'del-cancel': ed.delChoice = false; drawEditor(); break;
      case 'theme': S.settings.theme = b.dataset.v; save(); render(); openSettings(); break;
      case 'defrem': { const v = +b.dataset.v, r = new Set(S.settings.reminders); r.has(v) ? r.delete(v) : r.add(v); S.settings.reminders = [...r].sort((x, y) => y - x); save(); openSettings(); break; }
      case 'perm': if ('Notification' in window) Notification.requestPermission().then(() => openSettings()); break;
      case 'testalert': { const now = nowFn(); const ev = C.buildEvent({ kind: 'event', title: '测试提醒：和蒋宇飞喝咖啡', who: '蒋宇飞', where: '星巴克', date: C.fmtDate(now), time: C.pad(now.getHours()) + ':' + C.pad(Math.min(59, now.getMinutes() + 15)), status: 'pending', reminders: [15] }); S.events.push(ev); closeSheet(); addAlert({ key: ev.id + '@' + ev.date + '|15', kind: 'remind', evId: ev.id, date: ev.date, offset: 15 }); save(); render(); break; }
      case 'ics': download('dongfeng-calendar.ics', C.toICS(S.events, nowFn()), 'text/calendar;charset=utf-8'); toast('已导出 .ics（可导入 Apple/Google 日历）'); break;
      case 'exportjson': download('dongfeng-backup.json', JSON.stringify({ events: S.events, settings: S.settings }, null, 1), 'application/json'); break;
      case 'importjson': $('#importfile').click(); break;
      case 'seed': seed(); break;
      case 'wipe': if (b.dataset.sure) { S.events = []; S.fired = {}; S.alerts = []; S.snooze = {}; save(); closeSheet(); render(); } else { b.dataset.sure = 1; b.textContent = '再点一次确认清空'; } break;
    }
  });
  document.addEventListener('input', e => {
    if (e.target.id === 'pq') { S.peopleQ = e.target.value; const pos = e.target.selectionStart; render(); const el = $('#pq'); el.focus(); el.setSelectionRange(pos, pos); return; }
    if (ed && sheet.contains(e.target)) { if (e.target.id === 'f-repeat') { syncForm(); drawEditor(); return; } liveConflict(); }
  });
  document.addEventListener('change', e => {
    if (e.target.id === 'f-allday' && ed) { syncForm(); if (!e.target.checked && !ed.d.time) ed.d.time = '09:00'; drawEditor(); }
    if (e.target.id === 'importfile') { const f = e.target.files[0]; if (!f) return; f.text().then(t => { try { const j = JSON.parse(t); if (!Array.isArray(j.events)) throw 0; S.events = j.events; if (j.settings) Object.assign(S.settings, j.settings); save(); closeSheet(); render(); toast(`已导入 ${j.events.length} 条`); } catch (er) { toast('导入失败：文件格式不对', { warn: true }); } }); }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && ed) closeSheet(); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) { tick(); render(); } });

  // ---------- 启动 ----------
  render(); tick(); setInterval(tick, 15000); setInterval(() => { if (!document.hidden && !ed && ['brief', 'day', 'week'].includes(S.view) && document.activeElement !== q && !(document.activeElement && document.activeElement.tagName === 'TEXTAREA') && ![...document.querySelectorAll('textarea.fu')].some(x => x.value)) { const y = window.scrollY; render(); window.scrollTo(0, y); } }, 60000);
  window.__dfc = { S, C, tick, render, save, openEditor, addEvent: ev => { S.events.push(ev); save(); render(); } };
})();
