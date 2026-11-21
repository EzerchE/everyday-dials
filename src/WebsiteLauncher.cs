using System.Diagnostics;
namespace EverydayDials;

interface IWebsiteLauncher { bool OpenYouTube(); }
class NoWebsiteLauncher:IWebsiteLauncher { public bool OpenYouTube()=>false; }
class FixedYouTubeLauncher:IWebsiteLauncher
{
    public const string ChromePath=@"C:\Program Files\Google\Chrome\Application\chrome.exe";
    public const string Url="https://www.youtube.com/";
    readonly Func<ProcessStartInfo,bool> start;
    public FixedYouTubeLauncher(Func<ProcessStartInfo,bool>? starter=null)=>start=starter??Start;
    static bool Start(ProcessStartInfo info){using var process=Process.Start(info);return process!=null;}
    public bool OpenYouTube()
    {
        // Fixed executable + fixed URL. No shell, configurable URLs, command-line interpolation or focus manipulation.
        var info=new ProcessStartInfo{FileName=ChromePath,UseShellExecute=false,CreateNoWindow=true};info.ArgumentList.Add(Url);
        try{return start(info);}catch{return false;}
    }
}
