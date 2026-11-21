import {Composition} from 'remotion';
import {CaptionShort} from './CaptionShort';

export const Root: React.FC = () => (
  <Composition id="CaptionShort" component={CaptionShort} durationInFrames={150} fps={30}
    width={1080} height={1920}
    defaultProps={{words: ['This', 'town', 'has', 'one', 'weird', 'rule...', 'never', 'press', 'the', 'button!']}} />
);
