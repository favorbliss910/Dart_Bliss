process.env.DISABLE_TELEMETRY = 'true';
const {renderVideo} = await import('@revideo/renderer');
const scene = process.argv[2];
const out = await renderVideo({
  projectFile: `./src/highway-${scene}.ts`,
  settings: {
    outFile: `${scene}.mp4`, outDir: '../remotion/public/highway', logProgress: true, workers: 2,
    puppeteer: {executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', args: ['--no-sandbox']},
  },
});
console.log('rendered', out);
