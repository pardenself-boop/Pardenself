"""Original lightweight master-rack DSP; processes mono engine samples before safety bus."""
import math

DSP_KINDS=frozenset(('eq','compressor','density','clipper'))
NAMES={'eq':'BLOCK EQ','compressor':'BROWNSTONE COMP','density':'DUST DRIVE','clipper':'IRON CEILING',
       'transient':'TRANSIENT / PLANNED','phase':'PHASE / PLANNED'}

class StreetFX:
    def __init__(self):self.states={}
    def process(self,samples,modules,sample_rate):
        out=list(samples)
        for module in tuple(modules):
            if not module.enabled or module.kind not in DSP_KINDS:continue
            params=dict(module.params);kind=module.kind;identity=id(module)
            stored=self.states.get(identity)
            state=stored[1] if stored is not None and stored[0] is module else (0.,0.)
            rendered=[]
            if kind=='eq':
                low,high=state;a=1-math.exp(-2*math.pi*200/sample_rate);b=1-math.exp(-2*math.pi*4000/sample_rate)
                gl,gm,gh=(10**(params[key]/20)-1 for key in ('low_gain_db','mid_gain_db','high_gain_db'))
                for x in out:
                    low+=a*(x-low);high+=b*(x-high)
                    rendered.append(x+low*gl+(high-low)*gm+(x-high)*gh)
                self.states[identity]=(module,(low,high))
            elif kind=='compressor':
                envelope=state[0];attack=math.exp(-1/(sample_rate*params['attack_ms']/1000));release=math.exp(-1/(sample_rate*params['release_ms']/1000))
                threshold=10**(params['threshold_db']/20);exponent=1-1/params['ratio']
                for x in out:
                    level=abs(x);coefficient=attack if level>envelope else release
                    envelope=coefficient*envelope+(1-coefficient)*level
                    gain=(threshold/envelope)**exponent if envelope>threshold else 1.
                    rendered.append(x*gain)
                self.states[identity]=(module,(envelope,0.))
            elif kind=='density':
                drive=1+params['amount']*8;mix=params['mix'];normal=math.tanh(drive)
                for x in out:
                    wet=x if params['amount']==0 else math.tanh(x*drive)/normal
                    rendered.append(x*(1-mix)+wet*mix)
            else:
                drive=10**(params['drive_db']/20);ceiling=10**(params['ceiling_db']/20);mix=params['mix']
                for x in out:rendered.append(x*(1-mix)+max(-ceiling,min(ceiling,x*drive))*mix)
            out=rendered
        alive={id(module) for module in modules}
        self.states={key:value for key,value in self.states.items() if key in alive}
        return out
