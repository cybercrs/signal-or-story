from browser_base import run
from pathlib import Path
import json
C=json.loads((Path(__file__).resolve().parents[1]/'content.js').read_text().removeprefix('export const DATA = ').removesuffix(';\n'))
def walk(page,origin,ready,click,passed,out):
 def pick(key,value=None,index=None):
  options=page.locator('input[name="'+key+'"]')
  if index is not None:options.nth(index).check()
  else:options.evaluate_all('(nodes,v)=>nodes.find(x=>x.value===v).click()',value)
  ready(page)
 for team in range(1,13):
  if team>1:click(page,'Start over')
  page.locator('#team').fill(str(team));click(page,'Open your case');assert page.get_by_text('TEAM '+str(team).zfill(2),exact=True).is_visible();click(page,'Begin the interview')
  click(page,'Ask the selected question · 1 token');assert page.get_by_role('alert').count()>0
  pick('q0',index=0);click(page,'Back');click(page,'Forward');assert page.locator('input[name=q0]:checked').count()==1;click(page,'Ask the selected question · 1 token');click(page,'Move to evidence')
  pick('e0',index=0);click(page,'Obtain selected source · 1 token');assert page.get_by_text('What the source shows',exact=True).is_visible();click(page,'Move to the pressure decision')
  pick('p0',C['PRESSURE_CHOICES']['close']['label']+' — '+C['PRESSURE_CHOICES']['close']['stance']);click(page,'Commit response · 1 token');click(page,'Revise your response once · 1 token');pick('p1',C['PRESSURE_CHOICES']['narrow']['label']+' — '+C['PRESSURE_CHOICES']['narrow']['stance']);click(page,'Commit revised response · 1 token');assert page.get_by_role('button',name='Revise your response once · 1 token',exact=True).count()==0;click(page,'Keep response and shape the conclusion')
  pick('j0',index=1);pick('f0',index=1);click(page,'Test this judgment · 1 token');click(page,'Revise your judgment once · 1 token');pick('j1',index=0);pick('f1',index=0);click(page,'Test revised judgment · 1 token');assert page.get_by_role('button',name='Revise your judgment once · 1 token',exact=True).count()==0;click(page,'See what your investigation changed');assert page.get_by_text('0 OF 6 TOKENS LEFT',exact=True).is_visible();assert page.get_by_text('Your route-specific takeaway',exact=True).is_visible()
  if team in [1,4,7,10]:page.screenshot(path=str(out/('team-'+str(team)+'-complete.png')),full_page=True)
  # Strictly readonly revisit and preserving the exact token budget.
  click(page,'Back');assert page.get_by_role('button',name='Test this judgment · 1 token',exact=True).count()==0;assert page.get_by_role('button',name='Start over',exact=True).is_disabled();click(page,'Forward');assert page.get_by_text('0 OF 6 TOKENS LEFT',exact=True).is_visible()
  passed(f'Team {team}: complete original route, wrong response/judgment, both revisions, six-token budget and draft review')
 # Two interviews/two evidence sources consume all tokens before any optional revisions.
 click(page,'Start over');click(page,'Open your case');click(page,'Begin the interview');pick('q0',index=0);click(page,'Ask the selected question · 1 token');click(page,'Choose one follow-up question · 1 token');pick('q1',index=0);click(page,'Ask the selected question · 1 token');click(page,'Move to evidence');pick('e0',index=0);click(page,'Obtain selected source · 1 token');pick('e1',index=0);click(page,'Obtain selected source · 1 token');click(page,'Move to the pressure decision');pick('p0',C['PRESSURE_CHOICES']['narrow']['label']+' — '+C['PRESSURE_CHOICES']['narrow']['stance']);click(page,'Commit response · 1 token');assert page.get_by_role('button',name='Revise your response once · 1 token',exact=True).count()==0;click(page,'Keep response and shape the conclusion');pick('j0',index=0);pick('f0',index=0);click(page,'Test this judgment · 1 token');assert page.get_by_role('button',name='Revise your judgment once · 1 token',exact=True).count()==0;click(page,'See what your investigation changed');passed('Two-question/two-source route preserves mandatory response and judgment tokens')
 assert 'test' not in page.title().lower() and 'pilot' not in page.title().lower() and 'preview' not in page.title().lower();passed('Final student-facing title and all twelve rendered route variants')
run(walk,session_only=True)
