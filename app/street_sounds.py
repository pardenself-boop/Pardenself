"""Original TOOLBOXX sound-bank starting points; no external expansion content."""
from labb_engine import LABBS

SOUNDS=(
 ('Queens Low End',3,{'cutoff':.19,'drive':.25,'release':.45}),
 ('Brownstone Keys',7,{'cutoff':.42,'attack':.008,'release':.8}),
 ('Bronx Dust Kit',4,{'cutoff':.31,'drive':.58,'decay':.13}),
 ('Night Train Chord',20,{'attack':.17,'cutoff':.26,'release':1.2}),
 ('Uptown Lead',5,{'cutoff':.61,'drive':.38,'sustain':.7}),
 ('Concrete Perc',15,{'decay':.045,'cutoff':.78,'drive':.2}),
 ('Brooklyn Steel',13,{'cutoff':.29,'drive':.48,'release':.25}),
 ('Afterhours 808',21,{'decay':.75,'cutoff':.24,'release':.65}),
)

def apply_sound(engine,index):
    name,labb,overrides=SOUNDS[index%len(SOUNDS)];patch=LABBS[labb]
    params={'attack':patch.attack,'decay':patch.decay,'sustain':patch.sustain,'release':patch.release,
            'cutoff':patch.cutoff,'resonance':0.,'drive':0.,'width':.5}
    params.update(overrides)
    for key,value in params.items():engine.set_parameter(labb,key,value)
    engine.selected=labb
    return name
