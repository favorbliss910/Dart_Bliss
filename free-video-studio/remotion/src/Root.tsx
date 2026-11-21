import {Composition} from 'remotion';
import {CaptionShort} from './CaptionShort';
import {Teleport} from './Teleport';
import {Combined} from './Combined';
import {Film} from './highway/Film';

export const Root: React.FC = () => (
  <>
  <Composition id="Highway" component={Film} durationInFrames={9204} fps={60} width={1440} height={2560} defaultProps={{only: undefined}} />
  <Composition id="Combined" component={Combined} durationInFrames={480} fps={30} width={1080} height={1920} />
  <Composition id="Teleport" component={Teleport} durationInFrames={480} fps={30} width={1080} height={1920} />
  <Composition id="CaptionShort" component={CaptionShort} durationInFrames={150} fps={30}
    width={1080} height={1920}
    defaultProps={{words: ['This', 'town', 'has', 'one', 'weird', 'rule...', 'never', 'press', 'the', 'button!']}} />
  </>
);
