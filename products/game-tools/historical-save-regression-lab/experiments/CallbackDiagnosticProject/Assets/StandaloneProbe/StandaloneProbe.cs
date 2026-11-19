using System;
using System.Collections;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Runtime.InteropServices;
using UnityEngine;

// Original synthetic player probe; not a buyer's actual gameplay loader.
public static class StandaloneProbe
{
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool IsProcessInJob(IntPtr process,IntPtr job,out bool inJob);
    [DllImport("advapi32.dll",SetLastError=true)] private static extern bool OpenProcessToken(IntPtr process,uint access,out IntPtr token);
    [DllImport("advapi32.dll",SetLastError=true)] private static extern bool GetTokenInformation(IntPtr token,int type,out int value,int length,out int returned);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool CloseHandle(IntPtr handle);
    [StructLayout(LayoutKind.Sequential)] private struct FileInfoNative { public uint attributes,creationLow,creationHigh,accessLow,accessHigh,writeLow,writeHigh,volume,sizeHigh,sizeLow,links,indexHigh,indexLow; }
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool GetFileInformationByHandle(IntPtr handle,out FileInfoNative info);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool WriteFile(IntPtr handle,byte[] bytes,uint count,out uint written,IntPtr overlapped);
    [Serializable] private sealed class Result { public string status; public string path; public bool outsideWriteBlocked; public string outsideWriteError; public bool loopbackConnected; public string loopbackResult; public bool childStarted; public int childExit; public string childError; public bool childJobKnown; public bool childInJob; public bool childTokenKnown; public bool childAppContainer; public bool inheritedHandleMatched; public bool inheritedHandleWrite; public int inheritedHandleError; }
    private sealed class Worker : MonoBehaviour
    {
        // Simulates an event-based gameplay restoration. Completion is explicitly
        // signaled after state is applied; this is not a real game's loader.
        public IEnumerator Restore(string input,string mode,string started,string holdMarker,Action<SyntheticGameRuntime.SampleSaveLoader.State> completed)
        {
            yield return null;
            File.WriteAllText(started,"restore_pending");
            if(mode=="hang-child")
            {
                var exe=Path.Combine(Directory.GetParent(Application.dataPath).FullName,"SyntheticProbe.exe");
                var log=Path.Combine(Path.GetDirectoryName(holdMarker),"child-hold.log");
                var cmd="-batchmode -nographics -logFile \""+log+"\" --synthetic-child-hold \""+holdMarker+"\"";
                using(var child=System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo { FileName=exe,Arguments=cmd,UseShellExecute=false,CreateNoWindow=true }))
                { if(child==null) throw new InvalidOperationException("Child launch failed"); }
                yield break;
            }
            if(mode=="hang") yield break;
            var state=SyntheticGameRuntime.SampleSaveLoader.Load(File.ReadAllText(input),mode=="regression");
            if(mode=="quest-regression") state.questComplete=false;
            completed(state);
        }
    }
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void Run()
    {
        string stage="arguments";
        try
        {
            var args=Environment.GetCommandLineArgs();
            for(int i=0;i+1<args.Length;i++) if(args[i]=="--synthetic-child-hold")
            {
                bool inJob;var jobKnown=IsProcessInJob(System.Diagnostics.Process.GetCurrentProcess().Handle,IntPtr.Zero,out inJob);
                int app=0,len;bool tokenKnown=false;IntPtr token;
                if(OpenProcessToken(System.Diagnostics.Process.GetCurrentProcess().Handle,0x0008,out token))
                { try { tokenKnown=GetTokenInformation(token,29,out app,sizeof(int),out len); } finally { CloseHandle(token); } }
                File.WriteAllText(args[i+1],System.Diagnostics.Process.GetCurrentProcess().Id+","+(jobKnown&&inJob)+","+(tokenKnown&&app!=0));
                return; // Remain alive until externally terminated.
            }
            string input=null,output=null,canary=null,mode=null,started=null,portText=null,childMarker=null,childCanary=null,holdMarker=null,handleText=null,volumeText=null,indexHighText=null,indexLowText=null,expectedQuest=null,expectedPotions=null;
            for(int i=0;i+1<args.Length;i++) { if(args[i]=="--synthetic-fixture") input=args[++i]; else if(args[i]=="--synthetic-result") output=args[++i]; else if(args[i]=="--synthetic-canary") canary=args[++i]; else if(args[i]=="--synthetic-mode") mode=args[++i]; else if(args[i]=="--synthetic-started") started=args[++i]; else if(args[i]=="--synthetic-loopback-port") portText=args[++i]; else if(args[i]=="--synthetic-child-marker") childMarker=args[++i]; else if(args[i]=="--synthetic-child-canary") childCanary=args[++i]; else if(args[i]=="--synthetic-hold-marker") holdMarker=args[++i]; else if(args[i]=="--synthetic-handle") handleText=args[++i]; else if(args[i]=="--synthetic-volume") volumeText=args[++i]; else if(args[i]=="--synthetic-index-high") indexHighText=args[++i]; else if(args[i]=="--synthetic-index-low") indexLowText=args[++i]; else if(args[i]=="--expected-quest") expectedQuest=args[++i]; else if(args[i]=="--expected-potions") expectedPotions=args[++i]; }
            if(String.IsNullOrWhiteSpace(input)||String.IsNullOrWhiteSpace(output)||String.IsNullOrWhiteSpace(started)||(mode!="pass"&&mode!="regression"&&mode!="hang"&&mode!="hang-child"&&mode!="forged"&&mode!="quest-regression")) throw new ArgumentException("Missing synthetic inputs");
            stage="fixture_read";if(!File.Exists(input)) throw new FileNotFoundException();
            if(expectedQuest!="true" && expectedQuest!="false") throw new ArgumentException("Expected quest required");
            var expectedPotionsValue=Int32.Parse(expectedPotions);
            if(mode=="forged")
            {
                // Deliberately dishonest worker: emit the same type of marker and
                // a passing report without invoking the gameplay restoration.
                File.WriteAllText(started,"restore_pending");
                File.WriteAllText(output,JsonUtility.ToJson(new Result{status="pass",path=""}));
                Application.Quit(0);return;
            }
            var worker=new GameObject("SyntheticRestoreProbe").AddComponent<Worker>();
            worker.StartCoroutine(worker.Restore(input,mode,started,holdMarker,state=>{
                var code=1;var callbackStage="canary_write";
                try
                {
                    bool blocked=false;string writeError="";
                    if(!String.IsNullOrWhiteSpace(canary)) { try { File.WriteAllText(canary,"synthetic"); } catch(Exception e) when(e is UnauthorizedAccessException || e is DirectoryNotFoundException) { blocked=true; writeError=e.GetType().Name; } }
                    bool connected=false;string networkResult="not_requested";
                    if(!String.IsNullOrWhiteSpace(portText))
                    {
                        callbackStage="loopback";
                        try { using(var client=new TcpClient()) { var operation=client.BeginConnect(IPAddress.Loopback,Int32.Parse(portText),null,null); if(operation.AsyncWaitHandle.WaitOne(2000)) { client.EndConnect(operation);connected=true;networkResult="connected"; } else networkResult="timeout"; } }
                        catch(Exception e) { networkResult=e.GetType().Name; }
                    }
                    bool childStarted=false, childJobKnown=false, childInJob=false, childTokenKnown=false, childAppContainer=false;int childExit=-1;string childError="not_requested";
                    if(!String.IsNullOrWhiteSpace(childMarker) && !String.IsNullOrWhiteSpace(childCanary))
                    {
                        callbackStage="child_process";
                        try {
                            var command="/d /c \"echo child > \""+childMarker+"\" & echo child > \""+childCanary+"\"\"";
                            using(var child=System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo { FileName=@"C:\Windows\System32\cmd.exe",Arguments=command,UseShellExecute=false,CreateNoWindow=true }))
                            {
                                childStarted=child!=null;
                                if(child==null) childError="no_process";
                                else
                                {
                                    childJobKnown=IsProcessInJob(child.Handle,IntPtr.Zero,out childInJob);
                                    if(OpenProcessToken(child.Handle,0x0008,out var token))
                                    {
                                        try { childTokenKnown=GetTokenInformation(token,29,out var flag,sizeof(int),out var length); childAppContainer=childTokenKnown && flag!=0; }
                                        finally { CloseHandle(token); }
                                    }
                                }
                                if(child!=null && child.WaitForExit(5000)) { childExit=child.ExitCode;childError=""; }
                                else if(child!=null) { child.Kill();child.WaitForExit();childError="timeout"; }
                            }
                        } catch(Exception e) { childError=e.GetType().Name; }
                    }
                    bool handleMatched=false,handleWrite=false;int handleError=0;
                    if(!String.IsNullOrWhiteSpace(handleText))
                    {
                        callbackStage="inherited_handle";var handle=new IntPtr(Int64.Parse(handleText));
                        if(GetFileInformationByHandle(handle,out var info))
                        {
                            handleMatched=info.volume==UInt32.Parse(volumeText) && info.indexHigh==UInt32.Parse(indexHighText) && info.indexLow==UInt32.Parse(indexLowText);
                            if(handleMatched) { var bytes=System.Text.Encoding.ASCII.GetBytes("inherited-synthetic");handleWrite=WriteFile(handle,bytes,(uint)bytes.Length,out var written,IntPtr.Zero) && written==bytes.Length; if(!handleWrite) handleError=Marshal.GetLastWin32Error(); }
                        }
                        else handleError=Marshal.GetLastWin32Error();
                    }
                    var failedPath=!state.shield?"inventory.shield":state.questComplete!=(expectedQuest=="true")?"quests.complete":state.potions!=expectedPotionsValue?"inventory.potions":"";
                    var ok=failedPath=="";callbackStage="result_write";
                    File.WriteAllText(output,JsonUtility.ToJson(new Result{status=ok?"pass":"regression",path=failedPath,outsideWriteBlocked=blocked,outsideWriteError=writeError,loopbackConnected=connected,loopbackResult=networkResult,childStarted=childStarted,childExit=childExit,childError=childError,childJobKnown=childJobKnown,childInJob=childInJob,childTokenKnown=childTokenKnown,childAppContainer=childAppContainer,inheritedHandleMatched=handleMatched,inheritedHandleWrite=handleWrite,inheritedHandleError=handleError}));code=ok?0:1;
                }
                catch(Exception e) { Debug.LogError("Synthetic probe failed at "+callbackStage+": "+e.GetType().Name); }
                Application.Quit(code);
            }));
        }
        catch(Exception e) { Debug.LogError("Synthetic probe failed at "+stage+": "+e.GetType().Name);Application.Quit(1); }
    }
}
