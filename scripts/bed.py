# soft explainer bed: EP chords + sub + soft kick/shaker, 92 BPM, F major, pure numpy
import numpy as np, wave, sys
SR=48000; BPM=92; beat=60/BPM; DUR=float(sys.argv[1]) if len(sys.argv)>1 else 280
N=int(SR*DUR); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def n2f(n): return 440*2**((n-69)/12)
def add(sig,t,pan=0.5,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N: return
    L[i:j]+=sig[:j-i]*g*(1-pan)*2**0.5*0.7; R[i:j]+=sig[:j-i]*g*pan*2**0.5*0.7
def ep(f,d):
    t=np.arange(int(SR*d))/SR
    mod=np.sin(2*np.pi*f*t)*1.2*np.exp(-t*3)
    s=np.sin(2*np.pi*f*t+mod)*np.exp(-t*1.1)+0.25*np.sin(2*np.pi*2*f*t)*np.exp(-t*3)
    a=np.minimum(1,t/0.01); r=np.minimum(1,(d-t)/0.3).clip(0,1)
    return s*a*r
def sub(f,d):
    t=np.arange(int(SR*d))/SR
    return np.sin(2*np.pi*f*t)*np.minimum(1,t/0.02)*np.minimum(1,(d-t)/0.2).clip(0,1)
def kick():
    t=np.arange(int(SR*0.35))/SR; f=50+90*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def shaker():
    t=np.arange(int(SR*0.08))/SR; x=rng.standard_normal(len(t))
    x=np.diff(np.concatenate([[0],x])); return x*np.exp(-t*60)*0.5
# Fmaj9 - Am7 - Bbmaj7 - C6/9  (F major)
prog=[[53,57,60,64,67],[57,60,64,67],[58,62,65,69],[60,62,64,67,69]]
bass=[41,45,46,48]
bar=4*beat; nb=int(DUR/bar)+1
K=kick(); S=shaker()
for b in range(nb):
    t0=b*bar; ch=prog[b%4]
    intro = b<2; outro = t0>DUR-bar*2
    for k,n in enumerate(ch):
        add(ep(n2f(n),bar*1.05),t0+k*0.012,pan=0.3+0.1*k,g=0.10)
    # little arpeggio on beat 3.5
    add(ep(n2f(ch[-1]+12),beat*1.5),t0+2.5*beat,pan=0.7,g=0.05)
    add(sub(n2f(bass[b%4]-12),bar*0.95),t0,g=0.22)
    if not intro:
        for q in range(4):
            if q in (0,2): add(K,t0+q*beat,g=0.32)
            for e in range(2): add(S,t0+q*beat+e*beat/2+0.01,pan=0.65,g=0.06 if e else 0.035)
fade=np.minimum(1,np.arange(N)/(SR*2.5))*np.minimum(1,(N-np.arange(N))/(SR*4))
L*=fade; R*=fade
# gentle lowpass-ish smoothing
k=np.ones(6)/6; L=np.convolve(L,k,'same'); R=np.convolve(R,k,'same')
m=max(abs(L).max(),abs(R).max()); L/=m*1.12; R/=m*1.12
out=(np.stack([L,R],1)*32767).astype('<i2')
w=wave.open(sys.argv[2] if len(sys.argv)>2 else 'bed.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
print('ok',DUR)
