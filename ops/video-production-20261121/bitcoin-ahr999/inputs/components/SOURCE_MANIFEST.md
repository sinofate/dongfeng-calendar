# 三项组件真实源码包（只读素材库，未改片/未改码）

打包时间：2026-11-21 16:30 HKT。案卷 2026-11-21-bitcoin-ahr999-bottom。目的：给 cloud 补真实组件调用，避免把 ASS 变量重绘当成 number-pop-in / kinetic-center-build / panel-reveal。本轮成片已交 videoReview，不要用此包直接改已交审看片。

777 catalog：`/workspace/pub/ops/video-production-20261121/asset_catalog.json`（version 2026-11-21，777 条）。三个官方 id 的 status 均为 `source_present_not_render_tested`。本机核对：**HTML snippet 都在**，不是“只索引无源码”。

## 真实源路径（官方 hf_components）

| id | catalog.path（registry-item.json） | snippet | 本机 |
|---|---|---|---|
| hf_components:number-pop-in | `/workspace/pub/video-clone/knowledge/motion-templates/hyperframes/registry/components/number-pop-in/registry-item.json` | `number-pop-in.html`（hyperframes:snippet） | 在 |
| hf_components:kinetic-center-build | `.../registry/components/kinetic-center-build/registry-item.json` | `kinetic-center-build.html` | 在 |
| hf_components:panel-reveal | `.../registry/components/panel-reveal/registry-item.json` | `panel-reveal.html` | 在 |

各目录另有 `demo.html` 与 `registry-item.json`，已原样收入 `hf_components/<name>/`。

catalog `files[].target` 写的是 `compositions/components/<name>.html`，这三个目标路径**本机不存在**。那是安装目标，不是缺失源码：源码就是 registry 目录里的同名 html。

## 别名

- `motion_curated:number-pop-in` / `motion_curated:kinetic-center-build`：`alias_of` 指向官方 id，源码 sha256 与官方 html 完全相同，包内不重复。
- catalog 中**没有** `motion_curated:panel-reveal`。

## 本地依赖（未伪造）

- 三个 snippet 本身带内联 CSS/JS，无相对路径引用其它本地 html/css。
- `kinetic-center-build.html` 与三份 `demo.html` 引用 CDN `gsap@3.14.2`。素材库中已有相同版本本地文件，已附 `vendor/gsap/gsap-3.14.2.min.js`（sha256=`7b2c91e3bff9022bef50054413b365a945c93f87285dcf8bdfb92076c4c56304`）及 `GSAP-NOTICE.txt`，来源见该目录 PROVENANCE.txt。
- `kinetic-center-build.html` 还引用 CDN `CustomEase.min.js`。素材库中**没有** `CustomEase.min.js`（仅有 packages/core 的 TypeScript，未打包、不当作已有 min.js）。不可伪造。
- 字体系 CSS 名称（Inter / Geist），不在这三项的 `files[]` 里。`vendor/fonts/` 只是同库其它条目里已有的可选本地文件，来源见 PROVENANCE.txt；不是组件官方附件。
- 预览图 catalog 指向 `https://static.heygen.ai/...`，本机无对应 png，未打包、未下载。

catalog 状态 `source_present_not_render_tested` 仍然成立：源码在，本包不证明已按真实 HTML 渲进成片。当前成片这三项仍是 `catalog_variables_rendered`（ASS），`qualified=false`。

## 包内文件与 sha256

- `catalog-excerpts.json`  12275  sha256=`8415c556b67bee79ae881af4f6a8dd42ce26ec708b905b39c133e84810775b02`
- `hf_components/kinetic-center-build/demo.html`  2093  sha256=`4b8a7913038eec1f5cad91acfa48eb5a11d7c1e59d3a3c3de580afc6c9bd46ae`
- `hf_components/kinetic-center-build/kinetic-center-build.html`  11084  sha256=`774f75b80d82fbc0c6226b85743804fb7a2229fb038eb0d38fa2e9503072c2e0`
- `hf_components/kinetic-center-build/registry-item.json`  2383  sha256=`65ffed0a2b3f793658ae07d643e384a1865140837c495879b9f2167f8d0404c8`
- `hf_components/number-pop-in/demo.html`  6777  sha256=`b12a62158e7b25eb015e5b5e219fa67d5d7da4ba5821c03438dd5ef23732947c`
- `hf_components/number-pop-in/number-pop-in.html`  5481  sha256=`25bb2a0a3e2dc9a067cfb016d7d8a971b70774652a0a4dca200c9173a1fc4e48`
- `hf_components/number-pop-in/registry-item.json`  2158  sha256=`183a0f2707ff60a3161494ce0e7e57ac47cdc9c1f0ae717d5689170ac44d2262`
- `hf_components/panel-reveal/demo.html`  6929  sha256=`c814d6593c4e32621cb7952aa48db0c1a235d4b732fae0fb3a1ba354af5db74f`
- `hf_components/panel-reveal/panel-reveal.html`  5321  sha256=`0fbb1c9685a80e10e577d405544bf8db35ec1a27cb0c8bed55a4a1f5fd88d376`
- `hf_components/panel-reveal/registry-item.json`  1960  sha256=`bcb72a2990d1fa079c233506741a5ada7e669bbd58a0510440b5a98f74c3072b`
- `vendor/fonts/Geist-Bold.ttf`  66588  sha256=`f032f37d12e82a37977fd1159c01e1a14415672244d2e6865d57e28c74886d03`
- `vendor/fonts/Geist-Regular.ttf`  66584  sha256=`09af32bab931f1ccc6e4776c5c39c8ea6c0d59b096f6f6c2959b1fdf18df0901`
- `vendor/fonts/Geist-SemiBold.ttf`  66620  sha256=`4c11a19d17e7a608f797e6a7e1f266778cc75510861f61063acaa2c0dec7c906`
- `vendor/fonts/Inter-latin-400-normal.woff2`  23664  sha256=`8909904ab6c872eb994093482a88a28eca2cd95912d7b6fecd72103b0dc07edc`
- `vendor/fonts/Inter-latin-600-normal.woff2`  24452  sha256=`f9a06e79cd3a2a20951c0f0e28f66dd0e6d3fda73911d640a2125c8fcb78f21a`
- `vendor/fonts/Inter-latin-700-normal.woff2`  24356  sha256=`6f56409fd3d64bb85f7d070bce20749db2d66b6d63cec586cc22d1c761be2491`
- `vendor/fonts/PROVENANCE.txt`  2133  sha256=`7a4e4fd3c307e3da3ea509f6e947da0fdf11684f2816ddde8cf2658d4b476d40`
- `vendor/gsap/GSAP-NOTICE.txt`  145  sha256=`bd9160e95a8b1de40754454659793462743dc12a0bc1e314ab7e71741e3bc362`
- `vendor/gsap/PROVENANCE.txt`  638  sha256=`bcb4cc966f20385a530b616bf3d5206680f73b3a4b729119a5372a1088bf5f54`
- `vendor/gsap/gsap-3.14.2.min.js`  131276  sha256=`7b2c91e3bff9022bef50054413b365a945c93f87285dcf8bdfb92076c4c56304`
