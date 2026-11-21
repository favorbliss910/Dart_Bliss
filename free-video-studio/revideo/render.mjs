process.env.DISABLE_TELEMETRY = 'true';
const {renderVideo} = await import('@revideo/renderer');
const out = await renderVideo({
  projectFile: './src/project.ts',
  settings: {
    outFile: process.env.OUT || 'revideo_raw.mp4', outDir: '../compare', logProgress: true, workers: 1,
    puppeteer: {executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', args: ['--no-sandbox']},
  },
});
console.log('rendered', out);
