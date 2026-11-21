namespace EverydayDials;

record KeySpec(string Id,string App,string Label,string Command,string Kind,string Fallback,string Image,string PlayImage,string PauseImage,string UnknownImage,string MutedImage,string UnmutedImage);
class KeyContext(KeySpec spec)
{
    public KeySpec Spec=spec;public bool Held;public DateTime FlashUntil;public string LastImage="";
}
class ArtworkCache(string root)
{
    readonly Dictionary<string,string> cache=new();
    public string Load(string relative)
    {
        if(cache.TryGetValue(relative,out string? existing))return existing;
        string path=Path.GetFullPath(Path.Combine(root,relative));
        if(!path.StartsWith(Path.GetFullPath(root)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Artwork path outside plugin");
        string value="data:image/png;base64,"+Convert.ToBase64String(File.ReadAllBytes(path));cache[relative]=value;return value;
    }
}
class KeyEngine
{
    public const string Uuid="com.ezerche.everydaydials.key";
    readonly Dictionary<string,KeySpec> specs;readonly Dictionary<string,KeyContext> contexts=new();
    readonly IDesktop desktop;readonly IMediaProvider media;readonly Func<object,Task> send;readonly Func<string,string> image;readonly Func<DateTime> now;
    readonly IWebsiteLauncher website;
    public KeyEngine(IEnumerable<KeySpec> definitions,IDesktop d,IMediaProvider m,Func<object,Task> output,Func<string,string>? artwork=null,Func<DateTime>? clock=null,IWebsiteLauncher? launcher=null)
    {specs=definitions.ToDictionary(s=>s.Id);desktop=d;media=m;send=output;image=artwork??(path=>path);now=clock??(()=>DateTime.UtcNow);website=launcher??new NoWebsiteLauncher();}
    public int Count=>contexts.Count;
    public async Task Handle(System.Text.Json.JsonElement e)
    {
        if(!e.TryGetProperty("action",out var action)||action.GetString()!=Uuid||!e.TryGetProperty("context",out var ce))return;
        string context=ce.GetString()??"";if(context.Length==0)return;
        string name=e.GetProperty("event").GetString()??"";
        if(name=="willDisappear"){contexts.Remove(context);return;}
        if(name is "willAppear" or "didReceiveSettings")
        {
            if(!e.TryGetProperty("payload",out var p)||!p.TryGetProperty("settings",out var settings)||!settings.TryGetProperty("keyId",out var id)||!specs.TryGetValue(id.GetString()??"",out var spec)){contexts.Remove(context);return;}
            contexts[context]=new(spec);await send(new{@event="setTitle",context,payload=new{title="",target=0}});await Feedback(context,contexts[context]);return;
        }
        if(!contexts.TryGetValue(context,out var c))return;
        if(name=="keyUp"){c.Held=false;await Feedback(context,c);return;}
        if(name!="keyDown"||c.Held)return;
        c.Held=true;c.FlashUntil=safeYouTube(c.Spec)?DateTime.MinValue:now().AddMilliseconds(350);await Feedback(context,c);
        bool ok=false;
        if(c.Spec.Id=="chrome-daily-key-7"&&c.Spec.App=="chrome.exe"&&c.Spec.Kind=="website"&&c.Spec.Command=="OPENYOUTUBE")ok=website.OpenYouTube();
        else if(StringComparer.OrdinalIgnoreCase.Equals(desktop.Foreground(),c.Spec.App))
        {
            ok=c.Spec.Command switch
            {
                "MUTE"=>desktop.AdjustAudio(0,true),"VOLDOWN"=>desktop.AdjustAudio(-2,false),"VOLUP"=>desktop.AdjustAudio(2,false),
                _ when c.Spec.Kind is "media" or "media-command"=>await MediaDispatch.Execute(desktop,media,c.Spec.App,c.Spec.Command,c.Spec.Fallback),
                _=>desktop.Send(c.Spec.App,c.Spec.Command)
            };
        }
        if(!ok)await send(new{@event="showAlert",context});
        await Feedback(context,c);
    }
    public async Task Tick(){foreach(var pair in contexts.ToArray())await Feedback(pair.Key,pair.Value);}
    public static string Pressed(string path)=>path[..^4]+"-pressed.png";
    static bool safeYouTube(KeySpec spec)=>spec.Id.StartsWith("youtube-controls-key-",StringComparison.Ordinal);
    public async Task Feedback(string context,KeyContext c)
    {
        var s=c.Spec;string path=s.Image;
        if(s.Kind=="media"&&!safeYouTube(s))
        {
            var state=media.Read(s.App);path=state.Reliable?state.State switch {Playback.Playing=>s.PauseImage,Playback.Paused=>s.PlayImage,_=>s.UnknownImage}:s.UnknownImage;
        }
        else if(s.Kind=="mute")
        {
            try{path=desktop.Audio().Muted?s.UnmutedImage:s.MutedImage;}catch{path=s.UnknownImage;}
        }
        if(c.Held||now()<c.FlashUntil)path=Pressed(path);
        if(path==c.LastImage)return;
        await send(new{@event="setImage",context,payload=new{image=image(path),target=0}});c.LastImage=path;
    }
}
