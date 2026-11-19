"""Unrestricted control for the temporary restricted Unity startup probe."""
import importlib.util, json, shutil, tempfile, time
from pathlib import Path
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('job_experiment',here.parent/'windows-job'/'job_experiment.py')
job=importlib.util.module_from_spec(spec);spec.loader.exec_module(job)
source=here.parent/'CleanComparisonProject'; editor=r'C:\Program Files\Unity\Hub\Editor\6000.6.9f1\Editor\Unity.exe'
result={'experiment':'unrestricted synthetic Unity startup control','result':'incomplete'}
with tempfile.TemporaryDirectory(prefix='unity-control-',dir=here) as d:
 root=Path(d);project=root/'SyntheticUnityProject';project.mkdir()
 for sub in ('Assets','Packages','ProjectSettings'):shutil.copytree(source/sub,project/sub)
 log=root/'unity-probe.log'; start=time.monotonic()
 try:
  status,code,count=job.run([editor,'-batchmode','-nographics','-projectPath',str(project),'-quit','-logFile',str(log)],90000)
  result.update(result=status,exit_code=code,job_total_processes=count,elapsed_seconds=round(time.monotonic()-start,3),log_exists=log.exists())
  if log.exists():
   raw=log.read_text(encoding='utf-8',errors='replace')[:131072]
   result['log_lines']=[line.replace(str(root),'<temporary-project>') for line in raw.splitlines() if any(word in line.lower() for word in ('error','fail','license','package manager','exit','exception'))][:30]
 except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)
print(json.dumps(result,indent=2))
