import {makeProject} from '@motion-canvas/core';
import counter from './scenes/counter?scene';
import newyork from './scenes/newyork?scene';
import blueprint from './scenes/blueprint?scene';
import tokyo from './scenes/tokyo?scene';
export default makeProject({scenes: [counter, newyork, blueprint, tokyo]});
