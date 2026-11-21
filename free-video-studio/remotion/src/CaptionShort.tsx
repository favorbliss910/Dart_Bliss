// 2.5D test: layered scene with parallax camera push-in + word-by-word pop captions.
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

const Layer: React.FC<{depth: number; children: React.ReactNode}> = ({depth, children}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const zoom = interpolate(f, [0, durationInFrames], [1, 1 + 0.25 * depth]);
  const pan = interpolate(f, [0, durationInFrames], [0, -60 * depth]);
  return <AbsoluteFill style={{transform: `translateX(${pan}px) scale(${zoom})`}}>{children}</AbsoluteFill>;
};

const Bean: React.FC = () => {
  const f = useCurrentFrame();
  const bob = Math.abs(Math.sin(f / 5)) * -18;
  const blink = f % 60 < 4 ? 0.1 : 1;
  return (
    <svg width={420} height={900} viewBox="0 0 420 900" style={{position: 'absolute', left: 330, top: 880 + bob}}>
      <g stroke="#1e1e1e" strokeWidth={14} strokeLinecap="round" fill="none">
        <line x1={170} y1={600} x2={160} y2={860} /><line x1={250} y1={600} x2={262} y2={860} />
        <line x1={110} y1={420} x2={40} y2={560} /><line x1={310} y1={420} x2={380} y2={300} />
      </g>
      <rect x={100} y={360} width={220} height={300} rx={100} fill="#e8473c" stroke="#1e1e1e" strokeWidth={14} />
      <circle cx={210} cy={210} r={160} fill="#fff" stroke="#1e1e1e" strokeWidth={14} />
      <path d="M60 170 A160 160 0 0 1 360 170" stroke="#1e1e1e" strokeWidth={40} fill="none" />
      {[155, 265].map((x) => (
        <g key={x} transform={`translate(${x} 220) scale(1 ${blink})`}>
          <circle r={36} fill="#fff" stroke="#1e1e1e" strokeWidth={10} /><circle r={15} fill="#1e1e1e" />
        </g>
      ))}
      <path d="M170 290 Q210 320 250 290" stroke="#1e1e1e" strokeWidth={10} fill="none" strokeLinecap="round" />
    </svg>
  );
};

const Caption: React.FC<{words: string[]}> = ({words}) => {
  const f = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const per = Math.floor(durationInFrames / words.length);
  const i = Math.min(words.length - 1, Math.floor(f / per));
  const pop = spring({frame: f - i * per, fps, config: {damping: 9, stiffness: 220}});
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', top: -250}}>
      <div style={{fontFamily: 'Poppins, Arial Black, sans-serif', fontWeight: 900, fontSize: 130, color: '#fff',
        WebkitTextStroke: '10px #000', paintOrder: 'stroke fill', transform: `scale(${0.6 + 0.4 * pop})`}}>
        {words[i]}
      </div>
    </AbsoluteFill>
  );
};

export const CaptionShort: React.FC<{words: string[]}> = ({words}) => (
  <AbsoluteFill style={{background: 'linear-gradient(#7cc8ff, #d8f0ff)'}}>
    <Layer depth={0.2}>
      <div style={{position: 'absolute', left: 700, top: 180, width: 220, height: 220, borderRadius: 999, background: '#ffe45c'}} />
    </Layer>
    <Layer depth={0.5}>
      {[[-40, '#f4d35e'], [380, '#ee964b'], [800, '#f95738']].map(([x, c]) => (
        <div key={String(x)} style={{position: 'absolute', left: x as number, top: 900, width: 320, height: 320,
          background: c as string, border: '12px solid #1e1e1e'}} />
      ))}
      <div style={{position: 'absolute', left: -200, top: 1220, width: 1500, height: 800, background: '#5bc453'}} />
    </Layer>
    <Layer depth={1}><Bean /></Layer>
    <Caption words={words} />
  </AbsoluteFill>
);
