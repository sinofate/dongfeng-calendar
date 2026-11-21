===FILE: project.bitcoin-ahr999.json===
{
  "case": "2026-11-21-bitcoin-ahr999-bottom",
  "engine": "us3day-vertical-recovery",
  "timeline": {
    "duration_seconds": 109.051,
    "vo_duration_seconds": 109.050604,
    "fps": 30,
    "main_stage": {
      "x": 0,
      "y": 312,
      "width": 1080,
      "height": 1128
    },
    "title_and_captions_outside_main_stage": true
  },
  "fonts": {
    "family": "Noto Sans CJK SC",
    "regular": "inputs/fonts/NotoSansCJK-Regular.ttc",
    "bold": "inputs/fonts/NotoSansCJK-Bold.ttc",
    "face_index": 2,
    "substitute_forbidden": true
  },
  "subtitles": {
    "file": "inputs/subtitles/main_LR90.ass",
    "format": "ass"
  },
  "audio": {
    "vo": "inputs/audio/vo_p1_s16le.wav",
    "vo_duration_seconds": 109.050604,
    "bgm_plan": "inputs/audio/bgm_plan.json",
    "sfx_events": "inputs/audio/sfx_events.json",
    "loudness": {
      "target_i_lufs": -14.0,
      "true_peak_ceiling_dbtp": -1.5,
      "speech_gap_lu": 20
    }
  },
  "library_roots": {
    "hf_components": "inputs/components"
  },
  "opening": {
    "cover_until_seconds": 1.5,
    "cover": "inputs/covers/cover_1080x1920.jpg",
    "cut": "hard",
    "component": {
      "id": "hf_components:cover-push-3",
      "variables": {
        "image": "inputs/covers/cover_1080x1920.jpg",
        "duration_seconds": 1.5,
        "push_percent": 3,
        "status": "reconstructed"
      }
    }
  },
  "shots": [
    {
      "id": "s01",
      "t0": 0.0,
      "t1": 16.518,
      "media": "inputs/media/S01_makkler_btc_chart_21Nov2026.png",
      "component": {
        "id": "hf_components:number-pop-in",
        "variables": {
          "value": "55,298",
          "unit": "2026-11-21 当日低点",
          "lift": "standard",
          "tone": "paper"
        }
      }
    },
    {
      "id": "s02",
      "t0": 16.518,
      "t1": 27.26,
      "media": "TITLE_CARD_OK",
      "component": {
        "id": "hf_components:kinetic-center-build",
        "variables": {
          "text": "值得关注 ≠ 已经见底",
          "font_size": 72,
          "entry_offset": 48,
          "color": "#FFFFFF",
          "font_weight": 700
        }
      }
    },
    {
      "id": "s03",
      "t0": 27.26,
      "t1": 39.997,
      "media": "inputs/media/S03_algoros_ahr999_bitstamp_chart.png",
      "component": {
        "id": "hf_components:number-pop-in",
        "variables": {
          "value": "0.228",
          "unit": "2020-03-12 历史回算；当前逼近 0.23",
          "lift": "standard",
          "tone": "paper"
        }
      }
    },
    {
      "id": "s04",
      "t0": 39.997,
      "t1": 47.07,
      "media": "inputs/media/S03_owlchart_ahr999_bitstamp.png",
      "component": {
        "id": "hf_components:panel-reveal",
        "variables": {
          "title": "2011 年早期市场：约 0.15",
          "width": "wide",
          "tone": "ink",
          "reveal": "fade"
        }
      }
    },
    {
      "id": "s05",
      "t0": 47.07,
      "t1": 58.206,
      "media": "COMPONENT_price_decline",
      "component": {
        "id": "hf_components:price-decline-56000-44800",
        "variables": {
          "start_price": 56000,
          "end_price": 44800,
          "scenario_label": "压力情景，不是预测底",
          "duration_seconds": 11.136
        }
      }
    },
    {
      "id": "s06",
      "t0": 58.206,
      "t1": 72.717,
      "media": "inputs/media/S06_bitmain_s21_official_spec.png",
      "component": {
        "id": "hf_components:panel-reveal",
        "variables": {
          "title": "六美分／度电 · 约五万四美元／枚（仅电费估算）",
          "width": "wide",
          "tone": "ink",
          "reveal": "fade"
        }
      }
    },
    {
      "id": "s07",
      "t0": 72.717,
      "t1": 89.859,
      "media": "inputs/media/S07_farside_etf_table_19Nov2026.png",
      "component": {
        "id": "hf_components:number-pop-in",
        "variables": {
          "value": "约 5.8 亿",
          "unit": "美元净流出 · 2026-11-19；比较的是金额",
          "lift": "standard",
          "tone": "paper"
        }
      }
    },
    {
      "id": "s08",
      "t0": 89.859,
      "t1": 99.932,
      "media": "TITLE_CARD_OK",
      "component": {
        "id": "hf_components:kinetic-center-build",
        "variables": {
          "text": "观察：五日资金净流向／回踩低点能否守住",
          "font_size": 72,
          "entry_offset": 40,
          "color": "#FFFFFF",
          "font_weight": 700
        }
      }
    },
    {
      "id": "s09",
      "t0": 99.932,
      "t1": 109.051,
      "media": "TITLE_CARD_OK",
      "component": {
        "id": "hf_components:panel-reveal",
        "variables": {
          "title": "估值值得看；有人接，买点才更有说服力",
          "width": "wide",
          "tone": "ink",
          "reveal": "fade"
        }
      }
    }
  ],
  "output": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "source_corner_labels": false,
    "yellow_outline": false
  }
}
===FILE: inputs/subtitles/main_LR90.ass===
[Script Info]
Title: bitcoin-ahr999 script-v4 locked VO
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans CJK SC,76,&H0000D7FF,&H0000D7FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,3,2,90,90,370,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:01.25,Main,,0,0,0,,比特币跌到五万六千美元，
Dialogue: 0,0:00:01.25,0:00:02.22,Main,,0,0,0,,有一个指标，
Dialogue: 0,0:00:02.22,0:00:03.56,Main,,0,0,0,,我觉得值得拿出来聊聊。
Dialogue: 0,0:00:04.18,0:00:05.72,Main,,0,0,0,,这个指标叫 Ahr999，
Dialogue: 0,0:00:05.72,0:00:07.31,Main,,0,0,0,,通常也叫九神指数。
Dialogue: 0,0:00:08.00,0:00:08.99,Main,,0,0,0,,为了好理解，
Dialogue: 0,0:00:08.99,0:00:09.96,Main,,0,0,0,,咱们就叫它抄底指数。
Dialogue: 0,0:00:10.86,0:00:12.57,Main,,0,0,0,,抄底指数已经掉到了
Dialogue: 0,0:00:12.57,0:00:13.86,Main,,0,0,0,,零点二三附近，
Dialogue: 0,0:00:13.86,0:00:15.96,Main,,0,0,0,,快到二零二零年三一二币灾时的位置了。
Dialogue: 0,0:00:16.52,0:00:17.04,Main,,0,0,0,,这算不算买点？
Dialogue: 0,0:00:17.69,0:00:19.04,Main,,0,0,0,,我的看法是，
Dialogue: 0,0:00:19.04,0:00:20.39,Main,,0,0,0,,单看历史估值，
Dialogue: 0,0:00:20.39,0:00:21.69,Main,,0,0,0,,这个位置已经值得认真关注了。
Dialogue: 0,0:00:22.35,0:00:23.62,Main,,0,0,0,,但五万六到底是不是底，
Dialogue: 0,0:00:23.62,0:00:24.69,Main,,0,0,0,,还得看市场上的币卖出来，
Dialogue: 0,0:00:24.69,0:00:25.73,Main,,0,0,0,,有没有人接。
Dialogue: 0,0:00:27.26,0:00:27.72,Main,,0,0,0,,零点二三到底有多少见？
Dialogue: 0,0:00:28.58,0:00:30.04,Main,,0,0,0,,从这份历史回算看，
Dialogue: 0,0:00:30.04,0:00:31.64,Main,,0,0,0,,二零一七年到二零二五年，
Dialogue: 0,0:00:31.64,0:00:33.10,Main,,0,0,0,,整整九年，
Dialogue: 0,0:00:33.10,0:00:34.54,Main,,0,0,0,,低于零点二五的只有两天，
Dialogue: 0,0:00:34.54,0:00:35.78,Main,,0,0,0,,都在二零二零年三月。
Dialogue: 0,0:00:36.58,0:00:37.94,Main,,0,0,0,,三月十二日大约零点二二八，
Dialogue: 0,0:00:37.94,0:00:39.39,Main,,0,0,0,,跟现在已经很接近了。
Dialogue: 0,0:00:40.00,0:00:41.55,Main,,0,0,0,,再往前，
Dialogue: 0,0:00:41.55,0:00:43.09,Main,,0,0,0,,二零一一年还到过零点一五附近。
Dialogue: 0,0:00:43.75,0:00:45.06,Main,,0,0,0,,当然，那时候比特币还很早期，
Dialogue: 0,0:00:45.06,0:00:46.43,Main,,0,0,0,,跟今天差别很大。
Dialogue: 0,0:00:47.07,0:00:48.52,Main,,0,0,0,,我们就拿零点一五做个压力测试：
Dialogue: 0,0:00:48.52,0:00:50.07,Main,,0,0,0,,假设现在模型里的参考条件不动，
Dialogue: 0,0:00:50.07,0:00:51.62,Main,,0,0,0,,对应的币价大约四万四千八，
Dialogue: 0,0:00:51.62,0:00:53.03,Main,,0,0,0,,比五万六还低两成。
Dialogue: 0,0:00:53.03,0:00:54.52,Main,,0,0,0,,{\alpha&HFF&}
Dialogue: 0,0:00:55.31,0:00:56.43,Main,,0,0,0,,这个可能的下跌空间，
Dialogue: 0,0:00:56.43,0:00:57.54,Main,,0,0,0,,也得摆在桌面上。
Dialogue: 0,0:00:58.21,0:00:59.47,Main,,0,0,0,,有人可能会问，
Dialogue: 0,0:00:59.47,0:01:00.72,Main,,0,0,0,,五万六都快跌到挖矿成本了，
Dialogue: 0,0:01:00.72,0:01:01.90,Main,,0,0,0,,还能往哪儿跌？
Dialogue: 0,0:01:02.60,0:01:04.13,Main,,0,0,0,,按一度电六美分估算，
Dialogue: 0,0:01:04.13,0:01:05.74,Main,,0,0,0,,普通 S21 挖一枚光电费
Dialogue: 0,0:01:05.74,0:01:07.25,Main,,0,0,0,,就要五万四美元左右，
Dialogue: 0,0:01:07.25,0:01:09.91,Main,,0,0,0,,场租、维修和折旧还没算。
Dialogue: 0,0:01:10.56,0:01:11.92,Main,,0,0,0,,但这个成本只算矿机用电。
Dialogue: 0,0:01:12.72,0:01:13.52,Main,,0,0,0,,我更关心的是资金。
Dialogue: 0,0:01:14.45,0:01:16.00,Main,,0,0,0,,十一月十九日，
Dialogue: 0,0:01:16.00,0:01:17.58,Main,,0,0,0,,美国现货比特币 ETF
Dialogue: 0,0:01:17.58,0:01:19.16,Main,,0,0,0,,一天净流出大约五亿八千万美元。
Dialogue: 0,0:01:19.91,0:01:21.18,Main,,0,0,0,,按当天币价算，
Dialogue: 0,0:01:21.18,0:01:22.45,Main,,0,0,0,,这笔钱相当于二十一天
Dialogue: 0,0:01:22.45,0:01:23.61,Main,,0,0,0,,新挖出来的币的价值。
Dialogue: 0,0:01:24.38,0:01:25.06,Main,,0,0,0,,这里比的是金额。
Dialogue: 0,0:01:25.94,0:01:27.03,Main,,0,0,0,,矿工可以关机器，
Dialogue: 0,0:01:27.03,0:01:28.08,Main,,0,0,0,,市场上已经流通的币，
Dialogue: 0,0:01:28.08,0:01:29.13,Main,,0,0,0,,照样有人卖。
Dialogue: 0,0:01:29.86,0:01:31.16,Main,,0,0,0,,接下来，我会看两件事：
Dialogue: 0,0:01:31.16,0:01:32.67,Main,,0,0,0,,ETF 连续五个交易日加起来，
Dialogue: 0,0:01:32.67,0:01:34.16,Main,,0,0,0,,资金能不能转成净流入？
Dialogue: 0,0:01:34.16,0:01:35.59,Main,,0,0,0,,{\alpha&HFF&}
Dialogue: 0,0:01:36.26,0:01:37.70,Main,,0,0,0,,反弹之后，再回到这次低点附近，
Dialogue: 0,0:01:37.70,0:01:39.14,Main,,0,0,0,,能不能守住？
Dialogue: 0,0:01:39.93,0:01:41.33,Main,,0,0,0,,估值低，说明这个位置值得看。
Dialogue: 0,0:01:41.98,0:01:43.28,Main,,0,0,0,,跌下来的时候有人接，
Dialogue: 0,0:01:43.28,0:01:44.57,Main,,0,0,0,,这个买点才更有说服力。
Dialogue: 0,0:01:45.18,0:01:46.50,Main,,0,0,0,,以上只是市场数据分析
Dialogue: 0,0:01:46.50,0:01:47.65,Main,,0,0,0,,和我的个人判断，
Dialogue: 0,0:01:47.65,0:01:48.84,Main,,0,0,0,,不构成投资建议。
===FILE: inputs/audio/bgm_plan.json===
{
  "duration_seconds": 109.051,
  "xfade_seconds": 1.5,
  "excerpts": [
    {
      "role": "hook",
      "track_id": "bgm:pb569428",
      "file": "inputs/audio/bgm_hook_pb569428_off8_31s.mp3",
      "source_offset_seconds": 8.0,
      "t0": 0.0,
      "t1": 27.26,
      "shots": ["s01", "s02"]
    },
    {
      "role": "body",
      "track_id": "bgm:pb622408",
      "file": "inputs/audio/bgm_data_s03s04_pb622408_off10_23s.mp3",
      "source_offset_seconds": 10.0,
      "t0": 27.26,
      "t1": 47.07,
      "shots": ["s03", "s04"]
    },
    {
      "role": "climax",
      "track_id": "bgm:pb623319",
      "file": "inputs/audio/bgm_risk_pb623319_off18_29s.mp3",
      "source_offset_seconds": 18.0,
      "t0": 47.07,
      "t1": 72.717,
      "shots": ["s05", "s06"]
    },
    {
      "role": "body",
      "track_id": "bgm:pb622408",
      "file": "inputs/audio/bgm_data_s07_pb622408_off40_20s.mp3",
      "source_offset_seconds": 40.0,
      "t0": 72.717,
      "t1": 89.859,
      "shots": ["s07"]
    },
    {
      "role": "outro",
      "track_id": "bgm:pb628035",
      "file": "inputs/audio/bgm_outro_pb628035_off6_22s.mp3",
      "source_offset_seconds": 6.0,
      "t0": 89.859,
      "t1": 109.051,
      "shots": ["s08", "s09"]
    }
  ]
}
===FILE: inputs/audio/sfx_events.json===
{
  "events": [
    {
      "id": "sfx_legacy:whoosh_s",
      "file": "inputs/audio/sfx/whoosh_s.wav",
      "t0": 1.5,
      "duration_seconds": 0.45,
      "shot": "s01",
      "purpose": "cover-to-chart hard cut"
    },
    {
      "id": "sfx_semantic:tech_ui_bleep_notify_03",
      "file": "inputs/audio/sfx/tech_ui_bleep_notify_03.wav",
      "t0": 37.94,
      "duration_seconds": 0.392,
      "shot": "s03",
      "purpose": "0.228 number land"
    },
    {
      "id": "sfx_semantic:tech_ui_bleep_notify_03",
      "file": "inputs/audio/sfx/tech_ui_bleep_notify_03.wav",
      "t0": 65.74,
      "duration_seconds": 0.392,
      "shot": "s06",
      "purpose": "五万四 number land"
    },
    {
      "id": "sfx_semantic:tech_ui_bleep_notify_03",
      "file": "inputs/audio/sfx/tech_ui_bleep_notify_03.wav",
      "t0": 77.58,
      "duration_seconds": 0.392,
      "shot": "s07",
      "purpose": "五亿八千万 number land"
    }
  ],
  "disabled_shots": ["s02", "s04", "s09"]
}
===FILE: inputs/components/cover-push-3/registry-item.json===
{
  "id": "hf_components:cover-push-3",
  "name": "cover-push-3",
  "status": "reconstructed; original source missing",
  "variables": {
    "image": {
      "type": "string",
      "default": "inputs/covers/cover_1080x1920.jpg"
    },
    "duration_seconds": {
      "type": "number",
      "default": 1.5
    },
    "push_percent": {
      "type": "number",
      "default": 3
    },
    "status": {
      "type": "string",
      "default": "reconstructed"
    }
  },
  "files": [
    {
      "path": "cover-push-3.html",
      "target": "main",
      "type": "hyperframes:snippet"
    }
  ]
}
===FILE: inputs/components/cover-push-3/cover-push-3.html===
<div class="cover-push-3" aria-label="重建封面轻推">
  <img src="{{image}}" alt="" />
</div>
<style>
  .cover-push-3 {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #090d17;
  }
  .cover-push-3 img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform-origin: center center;
    animation: cover-push-3-move {{duration_seconds}}s ease-in-out both;
  }
  @keyframes cover-push-3-move {
    from { transform: scale(1); }
    to { transform: scale(1.03); }
  }
</style>
===FILE: inputs/components/price-decline-56000-44800/registry-item.json===
{
  "id": "hf_components:price-decline-56000-44800",
  "name": "price-decline-56000-44800",
  "status": "new; stress-scenario illustration",
  "variables": {
    "start_price": {
      "type": "number",
      "default": 56000
    },
    "end_price": {
      "type": "number",
      "default": 44800
    },
    "scenario_label": {
      "type": "string",
      "default": "压力情景，不是预测底"
    },
    "duration_seconds": {
      "type": "number",
      "default": 11.136
    }
  },
  "files": [
    {
      "path": "price-decline-56000-44800.html",
      "target": "main",
      "type": "hyperframes:snippet"
    }
  ]
}
===FILE: inputs/components/price-decline-56000-44800/price-decline-56000-44800.html===
<div class="price-decline-56000-44800">
  <div class="scenario">{{scenario_label}}</div>
  <svg viewBox="0 0 1080 1128" preserveAspectRatio="xMidYMid meet" role="img" aria-label="价格从约五万六千美元下降到约四万四千八百美元的压力情景，不是预测底">
    <defs>
      <linearGradient id="price-decline-bg" x2="0" y2="1">
        <stop offset="0" stop-color="#131e32"/>
        <stop offset="1" stop-color="#080d17"/>
      </linearGradient>
    </defs>
    <rect width="1080" height="1128" fill="url(#price-decline-bg)"/>
    <path d="M110 260 H970 M110 790 H970" stroke="#43536b" stroke-width="2" stroke-dasharray="10 12"/>
    <path class="decline-line" d="M165 280 C320 315 375 385 505 435 S685 625 875 780" fill="none" stroke="#ffd700" stroke-width="11" stroke-linecap="round"/>
    <circle cx="165" cy="280" r="13" fill="#ffd700"/>
    <circle class="decline-end" cx="875" cy="780" r="16" fill="#ffd700"/>
    <text x="165" y="225" fill="#ffffff" font-family="Noto Sans CJK SC, sans-serif" font-size="60" font-weight="700">约 ${{start_price}}</text>
    <text class="decline-end" x="610" y="895" fill="#ffd700" font-family="Noto Sans CJK SC, sans-serif" font-size="68" font-weight="700">约 ${{end_price}}</text>
    <text x="165" y="995" fill="#cbd5e1" font-family="Noto Sans CJK SC, sans-serif" font-size="36">参考条件不变 · 压力测试</text>
  </svg>
</div>
<style>
  .price-decline-56000-44800 {
    position: absolute;
    inset: 0;
    overflow: hidden;
    background: #080d17;
  }
  .price-decline-56000-44800 svg {
    display: block;
    width: 100%;
    height: 100%;
  }
  .price-decline-56000-44800 .scenario {
    position: absolute;
    z-index: 1;
    top: 32px;
    left: 7%;
    right: 7%;
    padding: 14px 20px;
    color: #ffffff;
    background: #27354a;
    border-radius: 12px;
    font: 700 42px "Noto Sans CJK SC", sans-serif;
    text-align: center;
  }
  .price-decline-56000-44800 .decline-line {
    stroke-dasharray: 1050;
    stroke-dashoffset: 1050;
    animation: price-decline-draw {{duration_seconds}}s ease-out forwards;
  }
  .price-decline-56000-44800 .decline-end {
    opacity: 0;
    animation: price-decline-land {{duration_seconds}}s ease-out forwards;
  }
  @keyframes price-decline-draw {
    0%, 10% { stroke-dashoffset: 1050; }
    75%, 100% { stroke-dashoffset: 0; }
  }
  @keyframes price-decline-land {
    0%, 72% { opacity: 0; }
    76%, 100% { opacity: 1; }
  }
</style>
===FILE: PRODUCE_README.md===
将本包与 `recovery-runtime` 并列放置，保持所有 `inputs/` 相对路径。必须补齐事实 JSON 所列封面、S01/S03/S04/S06/S07 图片、VO、五段 BGM excerpt 和 SFX 文件；`inputs/components/` 还必须放入现有 `number-pop-in`、`kinetic-center-build`、`panel-reveal` 的原始 registry 与 snippet，本包未重写这三个组件。

必须拷贝同 SHA-256 的 `inputs/fonts/NotoSansCJK-Regular.ttc`、`inputs/fonts/NotoSansCJK-Bold.ttc`，使用 Noto Sans CJK SC 的 TTC face_index=2，禁止替代。**缺件记录：提供的事实 JSON 没有这两个文件的 SHA-256 值，也没有上述媒体及现有组件的文件实体；本包无法列出或核验其摘要。** 拷贝后用 `sha256sum inputs/fonts/NotoSansCJK-Regular.ttc inputs/fonts/NotoSansCJK-Bold.ttc` 与案卷原件逐一比对。

**未验证记录：未提供 `representative.s04.json`、现有组件 registry 样本或运行中的 `recovery-runtime`；因此本包 project、BGM/SFX plan 和新组件 registry 的具体解析兼容性尚未经 `produce` 验证，不能声称已可直接渲染。** 不修改工具源码，不改用其他模型或渠道。

文件和原始组件补齐并核验后，从本包所在目录执行：

```sh
cd /workspace/pub/ops/video-production-20261121/recovery-runtime
python3 -m recovery_us3day produce --project ../project.bitcoin-ahr999.json --out ../out
```

若本包不与 runtime 并列，`--project` 改为本 JSON 的实际路径；须先确认该入口如何解析 `inputs/` 相对路径。