// Builds the public AF Studio catalogue from the live Do.ink storefront.
// Source of truth: https://app.do.ink/stores/navintas (parsed by build_catalog.py)
import { readFileSync, writeFileSync } from 'node:fs';

const products = JSON.parse(readFileSync(new URL('./products.json', import.meta.url)));
const STORE = 'https://app.do.ink/stores/navintas';
const img = (p) => (p.startsWith('http') ? p : 'https://app.do.ink' + p).replace(/&amp;/g, '&');
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const cards = products.map((p) => `      <article class="card">
        <a class="shot" href="${STORE}${p.href.replace('/stores/navintas', '')}" target="_blank" rel="noopener">
          <img loading="lazy" src="${esc(img(p.img))}" alt="${esc(p.title)}">
        </a>
        <div class="body">
          <h3>${esc(p.title)}</h3>
          <p class="meta">กระเป๋าผ้าแคนวาส 100% · พิมพ์ DTG · ผลิตในไทย</p>
          <div class="row"><span class="price">${esc(p.price)}</span>
            <a class="cta" href="${STORE}${p.href.replace('/stores/navintas', '')}" target="_blank" rel="noopener">ซื้อเลย</a>
          </div>
        </div>
      </article>`).join('\n');

const html = `<!doctype html><html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AF Studio · กระเป๋าผ้าแคนวาสพิมพ์ลาย — ${products.length} ดีไซน์</title>
<meta name="description" content="กระเป๋าผ้าแคนวาส 100% Cotton พิมพ์ลายกราฟิกออกแบบเอง ${products.length} ดีไซน์ เริ่ม ฿390 ผลิตในไทย ส่งทั่วไทย 1-3 วัน">
<meta property="og:title" content="AF Studio · กระเป๋าผ้าพิมพ์ลาย ${products.length} ดีไซน์">
<meta property="og:image" content="${esc(img(products[0].img))}">
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:#0b0e13;color:#eef1f6;font:16px/1.6 system-ui,"Noto Sans Thai",sans-serif}
a{color:inherit}
.wrap{max-width:1180px;margin:auto;padding:0 20px}
.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:26px;align-items:center;padding:52px 0 26px}
.hero h1{font-size:40px;line-height:1.15;margin:0 0 14px}
.hero .kicker{color:#f2a13c;font-weight:700;letter-spacing:.5px;margin:0 0 10px}
.hero p{color:#aab4c4;margin:0 0 20px}
.hero img{width:100%;border-radius:16px;border:1px solid #232b38}
.btns{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-block;padding:12px 20px;border-radius:10px;font-weight:700;text-decoration:none}
.btn.p{background:#f2a13c;color:#1a1206}
.btn.s{border:1px solid #38424f;color:#eef1f6}
section{padding:30px 0}
h2{font-size:26px;margin:0 0 6px}
.sub{color:#9aa3b2;margin:0 0 22px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.card{background:#131922;border:1px solid #222a36;border-radius:14px;overflow:hidden;display:flex;flex-direction:column}
.shot{display:block;aspect-ratio:1/1;background:#0e131b}
.shot img{width:100%;height:100%;object-fit:cover;display:block}
.body{padding:13px 15px 15px;display:flex;flex-direction:column;flex:1}
.body h3{font-size:16px;margin:0 0 4px;line-height:1.35}
.meta{color:#8b95a5;font-size:12px;margin:0 0 12px;flex:1}
.row{display:flex;align-items:center;justify-content:space-between}
.price{font-size:18px;font-weight:800;color:#f2a13c}
.cta{background:#1f6feb;color:#fff;text-decoration:none;padding:8px 14px;border-radius:9px;font-weight:700;font-size:14px}
.props{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.prop{background:#131922;border:1px solid #222a36;border-radius:12px;padding:16px}
.prop b{display:block;margin-bottom:6px}
.prop span{color:#9aa3b2;font-size:14px}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;counter-reset:s}
.step{background:#131922;border:1px solid #222a36;border-radius:12px;padding:18px}
.step:before{counter-increment:s;content:counter(s);display:inline-flex;width:28px;height:28px;border-radius:50%;background:#f2a13c;color:#1a1206;font-weight:800;align-items:center;justify-content:center;margin-bottom:10px}
footer{border-top:1px solid #1c232e;margin-top:20px;padding:26px 0;color:#8b95a5;font-size:14px}
@media(max-width:900px){.grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:820px){.hero{grid-template-columns:1fr}.props,.steps{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.grid{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.grid,.props,.steps{grid-template-columns:1fr}}
</style></head><body>
<div class="wrap">
  <div class="hero">
    <div>
      <p class="kicker">AF STUDIO · กระเป๋าผ้าพิมพ์ลาย</p>
      <h1>กระเป๋าผ้าแคนวาส<br>ลายกราฟิกออกแบบเอง</h1>
      <p>ผ้าแคนวาส 100% Cotton · พิมพ์ DTG คมชัด สีติดทน · ${products.length} ดีไซน์ให้เลือก · ผลิตในประเทศไทย ส่งทั่วไทย 1–3 วัน</p>
      <div class="btns">
        <a class="btn p" href="${STORE}" target="_blank" rel="noopener">เปิดร้าน / สั่งซื้อ</a>
        <a class="btn s" href="#designs">ดูดีไซน์ทั้งหมด</a>
      </div>
    </div>
    <img src="${esc(img(products[0].img))}" alt="ตัวอย่างกระเป๋า AF Studio">
  </div>
</div>
<div class="wrap" id="designs">
  <section>
    <h2>ดีไซน์ทั้งหมด (${products.length})</h2>
    <p class="sub">กดที่รูปหรือปุ่ม "ซื้อเลย" เพื่อสั่งซื้อได้ทันที</p>
    <div class="grid">
${cards}
    </div>
  </section>
  <section>
    <h2>ทำไมต้อง AF Studio</h2>
    <p class="sub">งานพิมพ์คุณภาพ ผลิตในไทย ราคาเป็นมิตร</p>
    <div class="props">
      <div class="prop"><b>ผ้าแคนวาสหนา</b><span>100% Cotton Canvas ใช้แทนถุงพลาสติกได้</span></div>
      <div class="prop"><b>พิมพ์ DTG คมชัด</b><span>สีติดทน ไม่ลอกง่าย หลังซักหลายครั้ง</span></div>
      <div class="prop"><b>ผลิตในไทย</b><span>ผลิต 24–48 ชม. ส่ง 1–3 วัน</span></div>
      <div class="prop"><b>เริ่ม ฿390</b><span>ไม่มีขั้นต่ำ สั่ง 1 ใบก็ทำ</span></div>
    </div>
  </section>
  <section>
    <h2>สั่งซื้อง่ายใน 3 ขั้น</h2>
    <div class="steps">
      <div class="step"><b>เลือกดีไซน์</b><p class="sub">กดรูปที่ชอบจากด้านบน</p></div>
      <div class="step"><b>เลือกสี/ขนาด</b><p class="sub">Natural หรือ BLACK · STANDARD / Large</p></div>
      <div class="step"><b>ชำระเงิน</b><p class="sub">Add to cart หรือ Buy now ที่หน้าร้าน</p></div>
    </div>
  </section>
  <footer>
    <p><b>AF Studio</b> — กระเป๋าผ้าพิมพ์ลาย ผลิตในประเทศไทย · <a href="${STORE}" target="_blank" rel="noopener">เปิดร้าน</a></p>
    <p>สั่งซื้อและชำระเงินผ่าน Do.ink · จัดส่งทั่วประเทศไทย</p>
  </footer>
</div></body></html>
`;
writeFileSync(new URL('./index.html', import.meta.url), html);
console.log('wrote index.html with', products.length, 'products');
