"""Export original route content and exhaustive independent route/choice oracles."""
import ast,itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'native'))
import case_content as c,case_logic as e
from capture import Recorder,Container,State
source=(ROOT/'streamlit_app.py').read_text();tree=ast.parse(source);driver=next(n.lineno for n in tree.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='initialize_state')
nodes=[n for n in tree.body if n.lineno<driver and not isinstance(n,(ast.Import,ast.Expr))];ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ROOT/'streamlit_app.py'),'exec'),ns);rec=Recorder();ns['st']=rec
rec.form=lambda key:Container(rec,rec.node('form',key=key,children=[]));rec.number_input=lambda label,**kw:rec.node('number',label=label,**kw) or kw.get('value',1);rec.form_submit_button=rec.button
rec.session_state=State(stage=0,route=None)
with rec.capture() as setup:ns['stage_setup']()
rec.session_state.route=e.get_route(1)
with rec.capture() as briefing:ns['stage_briefing']()
# Capture pristine text before controls. Dynamic route histories are rendered natively.
def strip_controls(items):
 return [x for x in items if x['kind'] not in ['form','button']]
data={k:v for k,v in vars(c).items() if k.isupper()};data.update({'setup':strip_controls(setup),'briefing':strip_controls(briefing),'interviewConsequences':{x:ns['interview_consequence'](x) for x in ['trace','scope','challenge']},'pressureConsequences':{impact:{x:ns['pressure_consequence'](x,impact) for x in c.PRESSURE_CHOICES} for impact in ['increase','decrease','mixed','limited']},'pressureFeedback':{impact:{x:e.pressure_feedback(x,impact) for x in c.PRESSURE_CHOICES} for impact in ['increase','decrease','mixed','limited']},'takeaways':{x:e.takeaway_for_impact(x) for x in ['increase','decrease','mixed','limited']}})
(ROOT/'native/content.js').write_text('export const DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
css=ns['APP_CSS'].strip().removeprefix('<style>').removesuffix('</style>');(ROOT/'native/original.css').write_text(css)
# Every route, all zero/one/two interview sequences, and all one/two evidence sequences.
oracles=[]
for team in range(1,13):
 route=e.get_route(team);questions=list(route['lens_content']['question_tactics']);evidence=list(route['lens_content']['evidence_options'])
 for count in range(3):
  for q in itertools.permutations(questions,count):
   prepared=e.prepared_evidence_ids(route,list(q));entries=[]
   for evidence_id in evidence:
    result=e.get_evidence(route['code'],evidence_id);profile=e.evidence_profile(route,evidence_id);guidance=c.EVIDENCE_GUIDANCE[route['lens']][evidence_id];ready=evidence_id in prepared
    entries.append({'id':evidence_id,'result':result['result'] if ready else guidance['without_context'],'impact':result['impact'] if ready else 'limited','strength':profile['strength'] if ready else 1})
   for count_e in [1,2]:
    for trail in itertools.permutations(entries,count_e):oracles.append({'team':team,'questions':q,'evidence':[x['id'] for x in trail],'effect':e.interview_effect(list(q)),'impact':e.aggregate_evidence_impact(list(trail)),'conclusions':e.build_aggregate_conclusion_choices(route,list(trail))})
(ROOT/'native/tests/python-oracles.json').write_text(json.dumps(oracles,ensure_ascii=False,separators=(',',':'))+'\n');print('Exported all 12 routes and',len(oracles),'Python route/choice outcomes')
