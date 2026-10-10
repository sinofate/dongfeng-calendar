/* 东风日历 core：自然语言解析、重复展开、冲突检测、提醒计算、ICS 导出（无 DOM 依赖，可在 node 测试） */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Core = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  const pad = n => String(n).padStart(2, '0');
  const fmtDate = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const parseDate = s => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
  const addDays = (d, n) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
  const dayNum = d => Math.round(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000);
  const startOfDay = d => new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const WD = ['日', '一', '二', '三', '四', '五', '六'];
  const monIdx = d => (d.getDay() + 6) % 7; // 周一=0 … 周日=6

  // ---------- 中文数字 ----------
  const CN = { 零: 0, 〇: 0, 一: 1, 二: 2, 两: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9 };
  function cnNum(s) {
    s = String(s).trim();
    if (/^\d+(\.\d+)?$/.test(s)) return parseFloat(s);
    if (s === '半') return 0.5;
    if (s === '十') return 10;
    let m = s.match(/^([零〇一二两三四五六七八九]?)十([零〇一二两三四五六七八九]?)$/);
    if (m) return (m[1] ? CN[m[1]] : 1) * 10 + (m[2] ? CN[m[2]] : 0);
    if (s.length === 1 && s in CN) return CN[s];
    if ([...s].every(c => c in CN)) return [...s].reduce((a, c) => a * 10 + CN[c], 0);
    return NaN;
  }
  const NUM = '[零〇一二两三四五六七八九十\\d]+';
  const WDCN = { 一: 0, 二: 1, 三: 2, 四: 3, 五: 4, 六: 5, 日: 6, 天: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6 };
  const WDEN = { mon: 0, tue: 1, wed: 2, thu: 3, fri: 4, sat: 5, sun: 6 };

  const WHO_STOPS = ['一起', '喝', '吃', '开', '见', '聊', '谈', '打', '看', '玩', '逛', '踢', '跑', '唱', '练', '讨', '面试', '通', '电话', '视频', '视', '拜', '汇', '复', '碰', '送', '接', '在', '去', '来', '到', '讲', '说', '买', '写', '做', '修', '订', '签', '带', '陪', '拍', '骑', '爬', '约', '吧', '的', '会', '谈', '商', '签', '健', '游', '补', '取', '办', '交', '对', '核', '检', '问', '请', '叫', '找', '给', '帮', '参', '听', '演', '排', '敲', '定', '确', '提', '分', '汇', '汇报', '聚', '散', '运', '锻', '参观', '试', '谈'];
  const PLACE_STOPS = ['和', '跟', '与', '同', '一起', '喝', '吃', '开', '见', '聊', '谈', '打', '看', '玩', '逛', '踢', '跑', '唱', '练', '讨论', '面试', '拜', '汇', '复', '碰', '送', '接', '讲', '学', '交'];
  const PUNCT = /[\s,，。;；、!！?？:：]/;

  function stopAt(str, i, stops) {
    for (const st of stops) if (str.startsWith(st, i)) return true;
    return false;
  }

  /** 解析一句话 -> 草稿事件。now 可注入以便测试 */
  function parse(input, now) {
    now = now || new Date();
    const today = startOfDay(now);
    let s = String(input || '').trim();
    const r = { title: '', who: '', where: '', date: '', time: '', dur: 0, repeat: 'none', kind: 'event', status: '', allDay: true, noDate: false, until: '' };
    if (!s) return r;
    const cut = (re, fn) => { const m = s.match(re); if (m) { s = s.slice(0, m.index) + ' ' + s.slice(m.index + m[0].length); if (fn) fn(m); return m; } return null; };
    let implied = '';
    let isEnglish = false;

    // 1) 任务前缀
    cut(/^\s*(待办|任务|todo|task|remind me to|remind me)\s*[:：]?\s*/i, () => { r.kind = 'task'; });
    cut(/(提醒我|提醒|记得|别忘了|别忘记)\s*[:：]?\s*/, () => { r.kind = 'task'; });
    // 2) 状态
    cut(/(待确认|未确认|没确认|unconfirmed|tentative)/i, () => { r.status = 'pending'; });
    cut(/(已确认|确认了|\bconfirmed\b)/i, () => { r.status = 'confirmed'; });
    cut(/(已改期|\brescheduled\b)/i, () => { r.status = 'rescheduled'; });

    // 3) 时长
    let m;
    if (cut(new RegExp('(' + NUM + ')\\s*个半\\s*小时'), m => { r.dur = Math.round((cnNum(m[1]) + 0.5) * 60); })) { }
    else if (cut(/半\s*个?\s*小时/, () => { r.dur = 30; })) { }
    else if (cut(new RegExp('(' + NUM + '(?:\\.\\d+)?)\\s*个?\\s*(?:小时|钟头)'), m => { r.dur = Math.round(cnNum(m[1]) * 60); })) { }
    else if (cut(new RegExp('(' + NUM + ')\\s*分钟'), m => { r.dur = Math.round(cnNum(m[1])); })) { }
    else if (cut(/\b(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)\b/i, m => { r.dur = Math.round(parseFloat(m[1]) * 60); })) { }
    else if (cut(/\b(?:for\s+)?(\d+)\s*(?:minutes?|mins?)\b/i, m => { r.dur = parseInt(m[1], 10); })) { }

    // 4) 重复
    let anchorWd = null, anchorMonthDay = null;
    const wdChars = '一二三四五六日天';
    if (cut(/每个?(?:工作日|周一到周五|周一至周五)|工作日|\bweekdays\b|every weekday/i, () => { r.repeat = 'weekdays'; })) { }
    else if (cut(/每(?:隔)?(?:两|2)周(?:的)?(?:周|星期|礼拜)?([一二三四五六日天])?|隔周|biweekly|every (?:other|two) weeks?/i, m => { r.repeat = 'biweekly'; if (m[1]) anchorWd = WDCN[m[1]]; })) { }
    else if (cut(new RegExp('每个?(?:周|星期|礼拜)([' + wdChars + '])'), m => { r.repeat = 'weekly'; anchorWd = WDCN[m[1]]; })) { }
    else if (cut(/every\s+(mon|tue|wed|thu|fri|sat|sun)[a-z]*/i, m => { r.repeat = 'weekly'; anchorWd = WDEN[m[1].toLowerCase()]; isEnglish = true; })) { }
    else if (cut(/每个?(?:周|星期|礼拜)|\bweekly\b|every week/i, () => { r.repeat = 'weekly'; })) { }
    else if (cut(new RegExp('每个?月(?:的)?(?:(' + NUM + ')\\s*[号日])?'), m => { r.repeat = 'monthly'; if (m[1]) anchorMonthDay = cnNum(m[1]); })) { }
    else if (cut(/\bmonthly\b|every month/i, () => { r.repeat = 'monthly'; })) { }
    else if (cut(/每年|\byearly\b|every year|annually/i, () => { r.repeat = 'yearly'; })) { }
    else if (cut(/每天|每日|天天|every ?day|\bdaily\b/i, () => { r.repeat = 'daily'; })) { }

    // 5) 日期
    let date = null, wdTarget = null, wdPrefix = '', wdBare = false;
    const yearOf = (mo, da) => { // 无年份：已过则取明年
      let d = new Date(today.getFullYear(), mo - 1, da);
      if (d < today) d = new Date(today.getFullYear() + 1, mo - 1, da);
      return d;
    };
    if (m = cut(/(\d{4})\s*[-\/年.]\s*(\d{1,2})\s*[-\/月.]\s*(\d{1,2})\s*[日号]?/)) date = new Date(+m[1], +m[2] - 1, +m[3]);
    else if (m = cut(new RegExp('(\\d{1,2})\\s*月\\s*(' + NUM + ')\\s*[日号]?'))) date = yearOf(+m[1], cnNum(m[2]));
    else if (m = cut(/(?<![\d:.])(\d{1,2})[\/\-](\d{1,2})(?![\d:])/)) date = yearOf(+m[1], +m[2]);
    else if (m = cut(/(大后天|后天|明天|明日|今天|今日|今晚|今早|今晨|明早|明晨|明晚|\bday after tomorrow\b|\btomorrow\b|\btoday\b|\btonight\b)/i)) {
      const w = m[1].toLowerCase();
      let off = 0;
      if (/大后天/.test(w)) off = 3; else if (/后天|day after/.test(w)) off = 2; else if (/明|tomorrow/.test(w)) off = 1;
      date = addDays(today, off);
      if (/晚|tonight/.test(w)) implied = '晚上'; else if (/早|晨/.test(w)) implied = '早上';
      if (/[a-z]/i.test(w)) isEnglish = true;
    }
    else if (m = cut(new RegExp('(' + NUM + ')\\s*(天|日|个?周|个?星期|个?礼拜|个?月)\\s*(?:之后|以后|后)'))) {
      const n = cnNum(m[1]), u = m[2];
      if (/月/.test(u)) date = new Date(today.getFullYear(), today.getMonth() + n, today.getDate());
      else if (/周|星期|礼拜/.test(u)) date = addDays(today, n * 7);
      else date = addDays(today, n);
    }
    else if (m = cut(/\bin\s+(\d+)\s*(day|week|month)s?\b/i)) {
      const n = +m[1], u = m[2].toLowerCase(); isEnglish = true;
      date = u === 'month' ? new Date(today.getFullYear(), today.getMonth() + n, today.getDate()) : addDays(today, n * (u === 'week' ? 7 : 1));
    }
    else if (m = cut(new RegExp('(下下|下|本|这)?\\s*个?\\s*(?:周|星期|礼拜)\\s*([' + wdChars + '1-7])'))) {
      wdTarget = WDCN[m[2]]; wdPrefix = m[1] || ''; wdBare = !m[1];
    }
    else if (m = cut(/\b(next|this)?\s*(mon|tue|wed|thu|fri|sat|sun)(?:day|sday|nesday|rsday|urday)?\b/i)) {
      wdTarget = WDEN[m[2].toLowerCase()]; wdPrefix = /next/i.test(m[1] || '') ? '下' : /this/i.test(m[1] || '') ? '本' : ''; wdBare = !m[1]; isEnglish = true;
    }
    else if (m = cut(new RegExp('(下个?月|下月|这个月|本月)\\s*(' + NUM + ')\\s*[日号]'))) {
      const nm = /下/.test(m[1]) ? 1 : 0;
      date = new Date(today.getFullYear(), today.getMonth() + nm, cnNum(m[2]));
    }
    else if (m = cut(new RegExp('(' + NUM + ')\\s*[日号](?!线)'))) {
      const dd = cnNum(m[1]);
      date = new Date(today.getFullYear(), today.getMonth(), dd);
      if (date < today) date = new Date(today.getFullYear(), today.getMonth() + 1, dd);
    }
    if (wdTarget !== null) {
      const weekMon = addDays(today, -monIdx(today));
      if (wdPrefix === '下') date = addDays(weekMon, 7 + wdTarget);
      else if (wdPrefix === '下下') date = addDays(weekMon, 14 + wdTarget);
      else if (wdPrefix === '本' || wdPrefix === '这') date = addDays(weekMon, wdTarget);
      else { const delta = (wdTarget - monIdx(today) + 7) % 7; date = addDays(today, delta); date._bare = true; }
    }

    // 6) 时间
    const pRe = '(凌晨|清晨|早上|早晨|上午|中午|下午|午后|傍晚|晚上|晚间|夜里|夜晚|早|晚)?';
    let hh = null, mm = 0, period = '';
    const resolveHour = (h, p) => {
      p = p || implied;
      if (/凌晨|清晨|早上|早晨|上午|^早$/.test(p)) return h === 12 ? 12 : h;
      if (/中午/.test(p)) return h >= 10 && h <= 12 ? h : h + 12;
      if (/下午|午后|傍晚|晚上|晚间|夜里|夜晚|^晚$/.test(p)) return h < 12 ? h + 12 : h % 24;
      return (h >= 1 && h <= 6) ? h + 12 : h; // 无时段：1-6 点按下午处理（启发式）
    };
    if (m = cut(/\bnoon\b/i)) { hh = 12; mm = 0; isEnglish = true; }
    else if (m = cut(/(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)/i)) {
      let h = +m[1]; const pm = /^p/i.test(m[3]); if (pm && h < 12) h += 12; if (!pm && h === 12) h = 0; hh = h; mm = m[2] ? +m[2] : 0; isEnglish = true;
    }
    else if (m = cut(new RegExp(pRe + '\\s*(' + NUM + ')\\s*(?:点钟?|时|[:：])\\s*(?:(半)|(\\d{1,2})\\s*分?|(一刻)|(三刻))?'))) {
      const h = cnNum(m[2]);
      if (!isNaN(h) && h <= 24) {
        mm = m[3] ? 30 : m[4] ? +m[4] : m[5] ? 15 : m[6] ? 45 : 0;
        hh = /[:：]/.test(m[0]) && !m[1] && !implied && h >= 7 ? h : resolveHour(h, m[1] || '');
        if (/[:：]/.test(m[0]) && !m[1] && !implied && h <= 6) hh = h; // 3:30 写法按 24 小时原样
        if (hh === 24) hh = 0;
      }
    }
    else if (m = cut(/(?<![\d:])(?:at\s+)?(\d{1,2}):(\d{2})(?![\d:])/i)) { hh = +m[1]; mm = +m[2]; }
    else if (m = cut(/(凌晨|清晨|早上|早晨|上午|中午|下午|午后|傍晚|晚上|晚间)/)) {
      const map = { 凌晨: 6, 清晨: 7, 早上: 8, 早晨: 8, 上午: 9, 中午: 12, 下午: 15, 午后: 14, 傍晚: 18, 晚上: 19, 晚间: 19 };
      hh = map[m[1]]; mm = 0;
    }
    else if (implied) { hh = implied === '晚上' ? 19 : 8; mm = 0; }
    if (hh !== null && hh >= 0 && hh < 24) { r.time = pad(hh) + ':' + pad(mm); r.allDay = false; }

    // 7) 地点
    const tryPlace = () => {
      // 中文：在 / 于 / @ / 地点：
      const re = /(?:在|于|@|地点[:：]?|地址[:：]?)/g; let mm2;
      while ((mm2 = re.exec(s))) {
        let i = mm2.index + mm2[0].length, j = i;
        while (j < s.length && !PUNCT.test(s[j]) && !(j > i && stopAt(s, j, PLACE_STOPS)) && !(j === i && stopAt(s, j, PLACE_STOPS)) && j - i < 16) j++;
        const place = s.slice(i, j);
        if (place.length >= 1 && !/^[的了着是]/.test(place)) {
          // “在” 后面是动词（如“在开会”）不算地点
          if (mm2[0] === '在' && stopAt(s, i, PLACE_STOPS)) continue;
          r.where = place.trim();
          s = s.slice(0, mm2.index) + ' ' + s.slice(j);
          return true;
        }
      }
      let me = s.match(/(?:^|\s)(?:at|@)\s+(.+?)(?=\s+(?:with|on|for|every|tomorrow|today|tonight|next)\b|[,;]|$)/i);
      if (me) { r.where = me[1].trim(); s = s.replace(me[0], ' '); isEnglish = true; return true; }
      return false;
    };
    tryPlace();

    // 8) 人物
    const addWho = names => { names = names.map(x => x.trim()).filter(Boolean); if (names.length) r.who = names.join('、'); };
    let whoDone = false, keepVerb = '';
    if (r.kind !== 'task' || /[和跟与同]/.test(s) && /(?:约|见|聊|喝|吃|开会|电话|视频)/.test(s)) {
      const re = /(?:和|跟|与|同|约(?![会定个一下面])|见(?![面到过])|拜访|探望|call |meet(?:ing)?(?: with)? )/ig; let mw;
      const seenEnglishWith = s.match(/\bwith\s+(.+?)(?=\s+(?:at|on|in|for|tomorrow|today|tonight|next|every|@)\b|[,;]|$)/i);
      if (seenEnglishWith && /[A-Za-z]/.test(seenEnglishWith[1])) {
        addWho(seenEnglishWith[1].split(/\s*(?:,|&|\band\b)\s*/i));
        s = s.replace(seenEnglishWith[0], ' '); whoDone = true; isEnglish = true;
      } else {
        while (!whoDone && (mw = re.exec(s))) {
          if (/^[和跟与同]$/.test(mw[0]) && /^(买|带|拿|取|做|写|准备|订|交|整理|洗|煮|修|学)/.test(s.slice(0, mw.index).trim())) continue;
          let i = mw.index + mw[0].length; while (s[i] === ' ') i++;
          const lat = s.slice(i).match(/^[A-Za-z][A-Za-z.'-]*(?:\s+[A-Z][a-z.'-]*)?/);
          if (lat && /[和跟与同约见]/.test(mw[0])) { addWho([lat[0]]); s = s.slice(0, mw.index) + ' ' + s.slice(i + lat[0].length); whoDone = true; isEnglish = isEnglish || false; continue; }
          let j = i; const names = []; let cur = '';
          while (j < s.length && j - i <= 14) {
            if (stopAt(s, j, WHO_STOPS) && !(cur === '' && false)) break;
            const c = s[j];
            if (c === '、' || c === '和' || c === '跟' || c === '与') { if (cur) names.push(cur); cur = ''; j++; continue; }
            if (/[\s,，。;；!！?？:：]/.test(c)) break;
            cur += c; j++;
            if (cur.length > 4) break;
          }
          if (cur.length > 4 || (cur.length === 4 && j < s.length && !stopAt(s, j, WHO_STOPS) && !PUNCT.test(s[j]))) { cur = cur.slice(0, 3); j = i + names.reduce((a, n) => a + n.length + 1, 0) + 3; }
          if (cur) names.push(cur);
          const good = names.filter(n => n.length >= 1 && n.length <= 4 && !/^[的了着是我你他她它这那啥]/.test(n));
          if (good.length && (mw[0] !== '约' || true)) {
            // 一起：紧跟的“一起”一并去掉
            let endJ = j; if (s.startsWith('一起', endJ)) endJ += 2;
            addWho(good);
            if (/^(拜访|探望)$/.test(mw[0])) { keepVerb = mw[0] + good.join('、'); s = s.slice(0, mw.index) + ' ' + s.slice(endJ); }
            else s = s.slice(0, mw.index) + ' ' + s.slice(endJ);
            whoDone = true;
          }
        }
      }
    }

    // 9) 标题
    let act = s.replace(/[\s]+/g, ' ').replace(/^[\s,，。;；、:：的了去]+|[\s,，。;；、:：的]+$/g, '').replace(/\s{2,}/g, ' ').trim();
    if (/^(?:to|a|an)\s+/i.test(act)) act = act.replace(/^(?:to|a|an)\s+/i, '');
    if (r.who && r.kind === 'event' && keepVerb) r.title = act ? `${keepVerb} ${act}` : keepVerb;
    else if (r.who && r.kind === 'event') {
      if (!/[\u4e00-\u9fff]/.test(input)) r.title = act ? `${act} with ${r.who}` : `Meet ${r.who}`;
      else r.title = act ? `和${r.who}${act}` : `和${r.who}见面`;
    } else r.title = act;
    if (!r.title && r.where) r.title = r.where;
    if (r.kind === 'task' && r.who) r.title = act ? `${act}（${r.who}）` : r.who;

    // 10) 日期兜底
    if (!date && r.repeat !== 'none') {
      if (anchorWd !== null) { date = addDays(today, (anchorWd - monIdx(today) + 7) % 7); date._bare = true; }
      else if (anchorMonthDay) { date = new Date(today.getFullYear(), today.getMonth(), anchorMonthDay); if (date < today) date = new Date(today.getFullYear(), today.getMonth() + 1, anchorMonthDay); }
    }
    if (!date) {
      r.noDate = true;
      date = today;
      if (r.time) { const [h, mi] = r.time.split(':').map(Number); if (h * 60 + mi <= now.getHours() * 60 + now.getMinutes()) { date = addDays(today, 1); } r.noDate = false; }
    } else if (date._bare && r.time) {
      const [h, mi] = r.time.split(':').map(Number);
      if (dayNum(date) === dayNum(today) && h * 60 + mi <= now.getHours() * 60 + now.getMinutes()) date = addDays(date, 7);
    }
    r.date = fmtDate(date);
    if (r.kind === 'event' && r.time && !r.dur) r.dur = 60;
    if (r.kind === 'event' && !r.time) r.dur = 0;
    if (r.kind === 'task' && r.time && !r.dur) r.dur = 0;
    if (!r.status) r.status = (r.kind === 'event' && r.who) ? 'pending' : 'confirmed';
    return r;
  }

  const DEFAULT_REMINDERS = [1440, 120, 15];
  function buildEvent(draft, opts) {
    opts = opts || {};
    const id = 'e' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    const isEvent = (draft.kind || 'event') === 'event';
    return Object.assign({
      id, kind: 'event', title: '', who: '', where: '', date: '', time: '', dur: 60, repeat: 'none', until: '',
      status: 'confirmed', notes: '', reminders: isEvent ? (opts.reminders || DEFAULT_REMINDERS).slice() : [0],
      followup: isEvent && !!draft.who, followups: {}, doneOcc: {}, exceptions: [], createdAt: Date.now(),
    }, draft, { id: draft.id || id });
  }

  // ---------- 重复展开 ----------
  function matches(ev, d) {
    const s = parseDate(ev.date); const dn = dayNum(d) - dayNum(s);
    if (dn < 0) return false;
    const ds = fmtDate(d);
    if (ev.until && ds > ev.until) return false;
    if (ev.exceptions && ev.exceptions.includes(ds)) return false;
    switch (ev.repeat || 'none') {
      case 'none': return dn === 0;
      case 'daily': return true;
      case 'weekdays': { const w = d.getDay(); return w >= 1 && w <= 5; }
      case 'weekly': return dn % 7 === 0;
      case 'biweekly': return dn % 14 === 0;
      case 'monthly': return d.getDate() === s.getDate();
      case 'yearly': return d.getMonth() === s.getMonth() && d.getDate() === s.getDate();
    }
    return false;
  }
  function makeOcc(ev, ds) {
    const d = parseDate(ds);
    let start, end, allDay = !ev.time;
    if (ev.time) {
      const [h, m] = ev.time.split(':').map(Number);
      start = new Date(d.getFullYear(), d.getMonth(), d.getDate(), h, m);
      end = new Date(start.getTime() + Math.max(ev.dur || 0, ev.kind === 'task' ? 0 : 15) * 60000);
    } else { start = d; end = addDays(d, 1); }
    return { ev, date: ds, key: ev.id + '@' + ds, start, end, allDay, done: !!(ev.doneOcc && ev.doneOcc[ds]) };
  }
  function occSort(a, b) {
    if (a.allDay !== b.allDay) return a.allDay ? -1 : 1;
    return a.start - b.start || (a.ev.title || '').localeCompare(b.ev.title || '');
  }
  function occurrencesInRange(events, from, to) {
    const out = []; const f = startOfDay(from), t = startOfDay(to);
    const n = dayNum(t) - dayNum(f);
    for (const ev of events) {
      if (!ev.repeat || ev.repeat === 'none') {
        const dn = dayNum(parseDate(ev.date));
        if (dn >= dayNum(f) && dn <= dayNum(t) && !(ev.exceptions || []).includes(ev.date)) out.push(makeOcc(ev, ev.date));
      } else {
        for (let i = 0; i <= n; i++) { const d = addDays(f, i); if (matches(ev, d)) out.push(makeOcc(ev, fmtDate(d))); }
      }
    }
    return out.sort(occSort);
  }
  const occurrencesOn = (events, d) => occurrencesInRange(events, d, d);

  // ---------- 冲突 ----------
  const overlap = (a, b) => a.start < b.end && b.start < a.end;
  const isTimedEvent = o => o.ev.kind === 'event' && !o.allDay;
  /** 一组当日 occ 中互相冲突的 key 集合 */
  function conflictMap(occs) {
    const timed = occs.filter(isTimedEvent); const map = {};
    for (let i = 0; i < timed.length; i++) for (let j = i + 1; j < timed.length; j++) {
      if (overlap(timed[i], timed[j])) {
        (map[timed[i].key] = map[timed[i].key] || []).push(timed[j]);
        (map[timed[j].key] = map[timed[j].key] || []).push(timed[i]);
      }
    }
    return map;
  }
  /** 某个拟保存的事件与已有事件的冲突（检查其未来 60 天内的出现） */
  function findConflicts(events, draft) {
    if (!draft.time || (draft.kind || 'event') !== 'event') return [];
    const others = events.filter(e => e.id !== draft.id);
    const tmp = Object.assign({ repeat: 'none', exceptions: [], dur: 60 }, draft, { id: draft.id || '__new' });
    const start = parseDate(draft.date); const res = []; const seen = new Set();
    const span = tmp.repeat === 'none' ? 0 : 60;
    for (let i = 0; i <= span; i++) {
      const d = addDays(start, i);
      if (!matches(tmp, d)) continue;
      const me = makeOcc(tmp, fmtDate(d));
      for (const o of occurrencesOn(others, d)) if (isTimedEvent(o) && overlap(me, o) && !seen.has(o.ev.id + o.date)) { seen.add(o.ev.id + o.date); res.push(o); }
      if (res.length >= 5) break;
    }
    return res;
  }

  // ---------- 提醒 ----------
  const baseTime = occ => occ.allDay ? new Date(occ.start.getFullYear(), occ.start.getMonth(), occ.start.getDate(), 9, 0) : occ.start;
  function reminderTime(occ, offsetMin) { return new Date(baseTime(occ).getTime() - offsetMin * 60000); }
  /** 当前应触发、尚未触发的提醒 */
  function dueReminders(events, now, fired) {
    const out = [];
    for (const o of occurrencesInRange(events, addDays(now, -1), addDays(now, 2))) {
      const over = o.allDay ? new Date(o.start.getFullYear(), o.start.getMonth(), o.start.getDate(), 23, 59, 59) : (o.ev.kind === 'task' ? new Date(o.start.getTime() + 3600000) : o.end);
      if (over <= now || o.done) continue;
      for (const off of (o.ev.reminders || [])) {
        const k = o.key + '|' + off;
        if (fired && fired[k]) continue;
        if (reminderTime(o, off) <= now) out.push({ occ: o, offset: off, key: k });
      }
    }
    return out;
  }
  /** 把当前已错过的提醒标记为已触发（新建/改期时用，避免立即轰炸） */
  function markPastFired(ev, now, fired) {
    for (const o of occurrencesInRange([ev], addDays(now, -1), addDays(now, 2)))
      for (const off of (ev.reminders || [])) if (reminderTime(o, off) <= now) fired[o.key + '|' + off] = now.getTime();
  }
  function pendingFollowups(events, now, days) {
    days = days || 14; const out = [];
    for (const o of occurrencesInRange(events, addDays(now, -days), now)) {
      if (o.ev.kind !== 'event' || !o.ev.followup || o.end > now) continue;
      if (o.ev.followups && o.ev.followups[o.date] !== undefined) continue;
      out.push(o);
    }
    return out.sort((a, b) => b.end - a.end);
  }
  const reminderLabel = off => off === 0 ? '准时' : off % 1440 === 0 ? `提前${off / 1440}天` : off % 60 === 0 ? `提前${off / 60}小时` : `提前${off}分钟`;

  // ---------- ICS ----------
  const icsEsc = t => String(t || '').replace(/\\/g, '\\\\').replace(/\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;');
  function fold(line) {
    const enc = new TextEncoder(); let out = '', cur = '', bytes = 0;
    for (const ch of line) {
      const b = enc.encode(ch).length;
      if (bytes + b > 73) { out += cur + '\r\n '; cur = ''; bytes = 1; }
      cur += ch; bytes += b;
    }
    return out + cur;
  }
  const icsDT = (ds, time) => ds.replace(/-/g, '') + (time ? 'T' + time.replace(':', '') + '00' : '');
  function toICS(events, now) {
    now = now || new Date();
    const stamp = now.getUTCFullYear() + pad(now.getUTCMonth() + 1) + pad(now.getUTCDate()) + 'T' + pad(now.getUTCHours()) + pad(now.getUTCMinutes()) + pad(now.getUTCSeconds()) + 'Z';
    const L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//东风日历//Prototype//ZH', 'CALSCALE:GREGORIAN', 'X-WR-CALNAME:东风日历', 'X-WR-TIMEZONE:Asia/Hong_Kong'];
    const rr = { daily: 'FREQ=DAILY', weekdays: 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR', weekly: 'FREQ=WEEKLY', biweekly: 'FREQ=WEEKLY;INTERVAL=2', monthly: 'FREQ=MONTHLY', yearly: 'FREQ=YEARLY' };
    const stLabel = { pending: '待确认', confirmed: '已确认', rescheduled: '已改期' };
    for (const ev of events) {
      const isTask = ev.kind === 'task';
      L.push(isTask ? 'BEGIN:VTODO' : 'BEGIN:VEVENT', 'UID:' + ev.id + '@dongfeng-calendar', 'DTSTAMP:' + stamp);
      L.push('SUMMARY:' + icsEsc(ev.title));
      const desc = [ev.who ? '约了：' + ev.who : '', ev.status && !isTask ? '状态：' + stLabel[ev.status] : '', ev.notes].filter(Boolean).join('\n');
      if (desc) L.push('DESCRIPTION:' + icsEsc(desc));
      if (ev.where) L.push('LOCATION:' + icsEsc(ev.where));
      if (isTask) {
        if (ev.time) L.push('DUE:' + icsDT(ev.date, ev.time)); else L.push('DUE;VALUE=DATE:' + icsDT(ev.date));
      } else if (ev.time) {
        const s = parseDate(ev.date); const [h, m] = ev.time.split(':').map(Number);
        const e = new Date(s.getFullYear(), s.getMonth(), s.getDate(), h, m + (ev.dur || 60));
        L.push('DTSTART:' + icsDT(ev.date, ev.time), 'DTEND:' + fmtDate(e).replace(/-/g, '') + 'T' + pad(e.getHours()) + pad(e.getMinutes()) + '00');
      } else {
        L.push('DTSTART;VALUE=DATE:' + icsDT(ev.date), 'DTEND;VALUE=DATE:' + icsDT(fmtDate(addDays(parseDate(ev.date), 1))));
      }
      if (!isTask) L.push('STATUS:' + (ev.status === 'confirmed' ? 'CONFIRMED' : 'TENTATIVE'));
      if (ev.repeat && ev.repeat !== 'none' && rr[ev.repeat]) {
        L.push('RRULE:' + rr[ev.repeat] + (ev.until ? ';UNTIL=' + icsDT(ev.until) + (ev.time ? 'T235959' : '') : ''));
        for (const x of ev.exceptions || []) L.push(ev.time ? 'EXDATE:' + icsDT(x, ev.time) : 'EXDATE;VALUE=DATE:' + icsDT(x));
      }
      if (!isTask) for (const off of ev.reminders || []) {
        L.push('BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + icsEsc('提醒：' + ev.title), 'TRIGGER:-PT' + off + 'M', 'END:VALARM');
      }
      L.push(isTask ? 'END:VTODO' : 'END:VEVENT');
    }
    L.push('END:VCALENDAR');
    return L.map(fold).join('\r\n') + '\r\n';
  }

  // ---------- 人物 ----------
  const splitWho = w => String(w || '').split(/[、,，;；&]|\s+and\s+/i).map(x => x.trim()).filter(Boolean);
  function describe(r) {
    const d = parseDate(r.date); const parts = [];
    parts.push(`${d.getMonth() + 1}月${d.getDate()}日 周${WD[d.getDay()]}${r.time ? ' ' + r.time : '（全天）'}`);
    return parts.join('');
  }


  // ---------- agent 事件（events.json）合并 ----------
  // 远程(agent)事件 + 本地事件合并：以 id 去重；对 agent 事件的本地改动（确认/删除/完成/跟进/编辑）记入覆盖表 ov，不写回仓库
  const clone = x => JSON.parse(JSON.stringify(x));
  function mergeAgent(local, remote, ov) {
    ov = ov || {};
    const ids = new Set((local || []).filter(e => e.source !== 'agent').map(e => e.id));
    const out = (local || []).filter(e => e.source !== 'agent');
    for (const r of (Array.isArray(remote) ? remote : [])) {
      if (!r || typeof r !== 'object' || !r.id || !r.date || ids.has(r.id)) continue;
      ids.add(r.id);
      const o = ov[r.id] || {};
      if (o.__deleted) continue;
      const ev = Object.assign(buildEvent(Object.assign({}, clone(r), { source: 'agent' })), clone(o));
      delete ev.__deleted; ev.source = 'agent';
      out.push(ev);
    }
    return out;
  }
  /** 由当前内存事件与远程原始数据重新计算覆盖表 */
  function diffAgent(events, remote, oldOv) {
    const ov = {}; const cur = new Map((events || []).filter(e => e.source === 'agent').map(e => [e.id, e]));
    for (const r of (Array.isArray(remote) ? remote : [])) {
      if (!r || !r.id) continue;
      const e = cur.get(r.id);
      if (!e) { ov[r.id] = { __deleted: true }; continue; }
      const base = buildEvent(Object.assign({}, clone(r), { source: 'agent' }));
      const d = {};
      for (const k of Object.keys(e)) if (k !== 'createdAt' && JSON.stringify(e[k]) !== JSON.stringify(base[k])) d[k] = clone(e[k]);
      if (Object.keys(d).length) ov[r.id] = d;
    }
    // 远程里已不存在的 id 的旧覆盖：丢弃
    return ov;
  }

  return { mergeAgent, diffAgent, pad, fmtDate, parseDate, addDays, dayNum, startOfDay, WD, monIdx, cnNum, parse, buildEvent, matches, makeOcc, occurrencesInRange, occurrencesOn, conflictMap, findConflicts, dueReminders, markPastFired, reminderTime, pendingFollowups, reminderLabel, toICS, splitWho, describe, DEFAULT_REMINDERS, isTimedEvent, overlap };
});
