import {makeProject} from '@revideo/core';
import counter from './scenes/counter';
import newyork from './scenes/newyork';
import blueprint from './scenes/blueprint';
import tokyo from './scenes/tokyo';

export default makeProject({
  scenes: [counter, newyork, blueprint, tokyo],
  settings: {shared: {size: {x: 1080, y: 1920}, background: '#000000'}},
});
