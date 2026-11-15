// node make_pdf.js <build_dir> — prints cover.html (full bleed) and book.html (with header/footer) via Chromium
const { chromium } = require('playwright');
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file://' + dir + '/cover.html'); await pg.waitForTimeout(500);
  await pg.pdf({ path: dir + '/cover.pdf', width: '210mm', height: '297mm', printBackground: true, margin: { top: 0, bottom: 0, left: 0, right: 0 }, pageRanges: '1' });
  await pg.goto('file://' + dir + '/book.html'); await pg.waitForTimeout(800);
  await pg.pdf({ path: dir + '/body.pdf', format: 'A4', printBackground: true,
    margin: { top: '18mm', bottom: '18mm', left: '16mm', right: '16mm' }, displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:7px;color:#8a7a6a;width:100%;padding:0 16mm;font-family:Inter,sans-serif;letter-spacing:1px">WHAT IF YOU…? · PROMPT BOOK v1.0</div>',
    footerTemplate: '<div style="font-size:8px;color:#8a7a6a;width:100%;text-align:right;padding:0 16mm;font-family:Inter,sans-serif"><span class="pageNumber"></span></div>' });
  await b.close();
})();
