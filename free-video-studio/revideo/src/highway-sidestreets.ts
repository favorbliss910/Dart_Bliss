import {makeProject} from '@revideo/core';
import {sidestreets} from './highway/map';
export default makeProject({
  scenes: [sidestreets],
  settings: {
    shared: {size: {x: 1440, y: 2560}, background: '#000000'},
    rendering: {exporter: {name: '@revideo/core/wasm'}, fps: 60, resolutionScale: 1, colorSpace: 'srgb'},
  } as any,
});
