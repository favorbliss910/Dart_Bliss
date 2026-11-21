import {Composition} from 'remotion';
import {CaptionShort} from './CaptionShort';
import {Teleport} from './Teleport';
import {Combined} from './Combined';

export const Root: React.FC = () => (
  <>
  <Composition id="Combined" component={Combined} durationInFrames={480} fps={30} width={1080} height={1920} />
  <Composition id="Teleport" component={Teleport} durationInFrames={480} fps={30} width={1080} height={1920} />
  <Composition id="CaptionShort" component={CaptionShort} durationInFrames={150} fps={30}
    width={1080} height={1920}
    defaultProps={{words: ['This', 'town', 'has', 'one', 'weird', 'rule...', 'never', 'press', 'the', 'button!']}} />
  </>
);
