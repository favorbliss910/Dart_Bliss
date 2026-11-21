import {makeProject} from '@revideo/core';
import {flow} from './highway/map';
export default makeProject({
  scenes: [flow],
  settings: {
    shared: {size: {x: 1440, y: 2560}, background: '#000000'},
    rendering: {exporter: {name: '@revideo/core/wasm'}, fps: 60, resolutionScale: 1, colorSpace: 'srgb'},
  } as any,
});
