using System.Diagnostics;
using System.Net.WebSockets;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;

namespace EverydayDials;

record DialSpec(string Id,string App,string Title,string Icon,string Color,string Left,string Right,string Press,string LeftLabel,string RightLabel,string PressLabel,bool Volume);
record AudioState(float Percent,bool Muted);
interface IDesktop { string Foreground(); bool Send(string app,string chord); string InputFailure {get;} AudioState Audio(); bool AdjustAudio(int delta,bool toggle); }
class Context(DialSpec spec) { public DialSpec Spec=spec; public bool Held; public bool CancelPress; public DateTime DirectionUntil; public DateTime PressUntil; public string LastBackground=""; public string Status=""; public DateTime Until; public int Direction; public string LastEncoderImage=""; }

class Engine
{
    public const string Uuid="com.ezerche.everydaydials.control";
    readonly Dictionary<string,DialSpec> specs;
    readonly IDesktop desktop;
    readonly Func<object,Task> send;
    readonly IMediaProvider media;
    readonly Func<DateTime> now;
    readonly Dictionary<string,Context> contexts=new();
    public Engine(IEnumerable<DialSpec> definitions,IDesktop d,Func<object,Task> output,IMediaProvider? m=null,Func<DateTime>? clock=null) { specs=definitions.ToDictionary(x=>x.Id);desktop=d;send=output;media=m??new NoMedia();now=clock??(()=>DateTime.UtcNow); }
    public int Count=>contexts.Count;
    public async Task Handle(JsonElement e)
    {
        string name=e.GetProperty("event").GetString()??"";
        if(!e.TryGetProperty("context",out var ce))return;
        string ctx=ce.GetString()??"";
        if(ctx.Length==0)return;
        if(e.TryGetProperty("action",out var action) && action.GetString()!=Uuid)return;
        JsonElement payload=e.TryGetProperty("payload",out var p)?p:default;
        if(name=="willDisappear") {contexts.Remove(ctx);return;}
        if(name is "willAppear" or "didReceiveSettings")
        {
            if(payload.ValueKind!=JsonValueKind.Object || !payload.TryGetProperty("settings",out var settings) || !settings.TryGetProperty("dialId",out var id) || !specs.TryGetValue(id.GetString()??"",out var spec))return;
            contexts[ctx]=new(spec);
            await send(new { @event="setFeedbackLayout",context=ctx,payload=new { layout=YouTubeFeedback.Layout(spec) } });
            await Feedback(ctx,contexts[ctx]);return;
        }
        if(!contexts.TryGetValue(ctx,out var c))return;
        if(name=="dialDown") {c.Held=true;c.CancelPress=false;if(YouTubeFeedback.IsYouTube(c.Spec))await Feedback(ctx,c);return;}
        if(name=="dialUp")
        {
            if(!c.Held)return;
            c.Held=false;
            if(c.CancelPress){c.CancelPress=false;if(YouTubeFeedback.IsYouTube(c.Spec))await Feedback(ctx,c);return;}
            await Execute(ctx,c,c.Spec.Press,c.Spec.PressLabel,1);return;
        }
        if(name=="touchTap") {if(YouTubeFeedback.IsYouTube(c.Spec))c.PressUntil=now().AddMilliseconds(YouTubeFeedback.FeedbackMilliseconds);await Execute(ctx,c,c.Spec.Press,c.Spec.PressLabel,1);return;}
        if(name=="dialRotate")
        {
            if(!payload.TryGetProperty("ticks",out var t)||!t.TryGetInt32(out int ticks)||ticks==0)return;
            // Holding and turning is not a subsequent click (avoid an accidental play/pause on release).
            if(c.Held){if(YouTubeFeedback.IsYouTube(c.Spec))c.CancelPress=true;else c.Held=false;}
            bool right=ticks>0; int count=(int)Math.Min(8,Math.Abs((long)ticks));
            await Execute(ctx,c,right?c.Spec.Right:c.Spec.Left,right?c.Spec.RightLabel:c.Spec.LeftLabel,count,right?1:-1);
        }
    }
    async Task Execute(string ctx,Context c,string chord,string label,int count,int direction=0)
    {
        bool audio=chord is "VOLDOWN" or "VOLUP" or "MUTE";
        bool ok;string failure="Open "+AppName(c.Spec.App);
        if(audio) ok=desktop.AdjustAudio(chord=="VOLDOWN"?-2*count:chord=="VOLUP"?2*count:0,chord=="MUTE");
        else
        {
            ok=StringComparer.OrdinalIgnoreCase.Equals(desktop.Foreground(),c.Spec.App);
            for(int i=0;ok&&i<count;i++)
            {
                ok=MediaDispatch.IsMedia(chord)?await MediaDispatch.Execute(desktop,media,c.Spec.App,chord):desktop.Send(c.Spec.App,chord);
                if(!ok&&!string.IsNullOrEmpty(desktop.InputFailure))failure=desktop.InputFailure;
            }
        }
        c.Status=ok?label+(count>1?$" ×{count}":""):failure;
        // YouTube's direction art acknowledges the physical turn, including a
        // blocked shortcut. Dispatch success is never inferred as player state.
        c.Direction=YouTubeFeedback.IsYouTube(c.Spec)||ok?direction:0;
        if(YouTubeFeedback.IsYouTube(c.Spec))c.DirectionUntil=direction!=0?now().AddMilliseconds(YouTubeFeedback.FeedbackMilliseconds):DateTime.MinValue;
        c.Until=now().AddMilliseconds(1200);
        await Feedback(ctx,c);
    }
    static string AppName(string app)=>app switch {"chrome.exe"=>"Chrome","stremio-shell-ng.exe"=>"Stremio","Spotify.exe"=>"Spotify","Telegram.exe"=>"Telegram","WhatsApp.Root.exe"=>"WhatsApp","bambu-studio.exe"=>"Bambu Studio",_=>"app"};
    public async Task Tick(bool youtubeOnly=false)
    {
        foreach(var pair in contexts.ToArray())
        {
            var c=pair.Value;
            bool youtube=YouTubeFeedback.IsYouTube(c.Spec);
            bool expireDirection=youtube&&c.Direction!=0&&now()>=c.DirectionUntil;
            bool expirePress=youtube&&c.PressUntil!=DateTime.MinValue&&now()>=c.PressUntil;
            if(expireDirection)c.Direction=0;
            if(expirePress)c.PressUntil=DateTime.MinValue;
            // Fast ticks only service an elapsed YouTube animation deadline.
            // Idle audio and other applications retain the 750 ms poll cadence.
            if(!youtubeOnly||(youtube&&(expireDirection||expirePress)))await Feedback(pair.Key,c);
        }
    }
    public async Task Feedback(string ctx,Context c)
    {
        var s=c.Spec;
        if(YouTubeFeedback.IsYouTube(s))
        {
            bool? muted=null;
            if(s.Volume)try{muted=desktop.Audio().Muted;}catch{/* Neutral if output state is unavailable. */}
            string encoderImage=YouTubeFeedback.EncoderImage(s);
            if(encoderImage!=c.LastEncoderImage)
            {
                await send(new { @event="setImage",context=ctx,payload=new { image=encoderImage } });
                c.LastEncoderImage=encoderImage;
            }
            string background=YouTubeFeedback.Background(s,now()<c.DirectionUntil?c.Direction:0,c.Held||now()<c.PressUntil,muted);
            if(background!=c.LastBackground)
            {
                await send(new { @event="setFeedback",context=ctx,payload=new Dictionary<string,object>{["canvas"]=background} });
                c.LastBackground=background;
            }
            return;
        }
        bool active=now()<c.Until;
        string value=active?c.Status:"Turn or tap"; float bar=active?100:0;
        string detail=WheelDispatcher.IsWheel(s.Left)?"Point at the pane to scroll":"Controls the active app";
        if(s.Volume)
        {
            try {var a=desktop.Audio();value=a.Muted?"Muted":$"{Math.Round(a.Percent)}%";bar=a.Percent;detail=active?c.Status:"Windows output volume";}
            catch {value="Audio unavailable";bar=0;detail="Check output device";}
        }
        await send(new { @event="setFeedback",context=ctx,payload=new Dictionary<string,object>{
            ["title"]=s.Title,["icon"]=s.Icon,["value"]=new {value,font=new {size=value.Length>17?12:16,weight=700}},["directions"]=$"‹ {s.LeftLabel}  |  {s.RightLabel} ›",
            ["press"]="Press / tap: "+s.PressLabel,["detail"]=detail,["activity"]=new { value=bar,bar_fill_c=s.Color }
        }});
    }
}

static class Program
{
    static readonly JsonSerializerOptions JsonOptions=new() {PropertyNameCaseInsensitive=true};
    static async Task<int> Main(string[] args)
    {
        if(args.Contains("--self-test"))return await Tests.Run();
        if(args.Contains("--audio-probe")) {try {Console.WriteLine(JsonSerializer.Serialize(new WindowsDesktop().Audio()));return 0;}catch(Exception e){Console.WriteLine(e.Message);return 1;}}
        if(args.Contains("--media-probe")){await MediaSessions.Probe();return 0;}
        if(args.Contains("--keyboard-probe")){WindowsDesktop.ProbeKeyboard();return 0;}
        Dictionary<string,string> options=new();for(int i=0;i+1<args.Length;i+=2)options[args[i]]=args[i+1];
        if(!options.TryGetValue("-port",out var portText)||!int.TryParse(portText,out int port)||port is <1 or >65535 || !options.TryGetValue("-pluginUUID",out var uuid)||!options.TryGetValue("-registerEvent",out var registration)||registration!="registerPlugin")return 2;
        var specs=JsonSerializer.Deserialize<List<DialSpec>>(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"../catalog.json")),JsonOptions)??[];
        var keySpecs=JsonSerializer.Deserialize<List<KeySpec>>(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"../key-catalog.json")),JsonOptions)??[];
        var media=await MediaSessions.Create();
        // Stream Deck controls lifetime. A bounded reconnect avoids orphan processes if the host exits.
        for(int attempt=0;attempt<4;attempt++)
        {
            using var socket=new ClientWebSocket();using var cancel=new CancellationTokenSource();
            var outputLock=new SemaphoreSlim(1,1);var engineLock=new SemaphoreSlim(1,1);
            async Task Send(object message) {await outputLock.WaitAsync(cancel.Token);try{await socket.SendAsync(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(message)),WebSocketMessageType.Text,true,cancel.Token);}finally{outputLock.Release();}}
            try
            {
                await socket.ConnectAsync(new Uri($"ws://127.0.0.1:{port}"),cancel.Token);
                await Send(new { @event=registration,uuid });
                await Send(new { @event="logMessage",payload=new { message=$"Interactive App Dials started; {specs.Count} catalog controls" } });
                var desktop=new WindowsDesktop();var engine=new Engine(specs,desktop,Send,media);
                var artwork=new ArtworkCache(Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,"..")));
                var keys=new KeyEngine(keySpecs,desktop,media,Send,artwork.Load,launcher:new FixedYouTubeLauncher());
                var timer=Task.Run(async()=> {DateTime nextGeneric=DateTime.UtcNow.AddMilliseconds(750);while(!cancel.IsCancellationRequested){await Task.Delay(20,cancel.Token);await engineLock.WaitAsync(cancel.Token);try {bool generic=DateTime.UtcNow>=nextGeneric;if(engine.Count>0)await engine.Tick(youtubeOnly:!generic);if(generic){if(keys.Count>0)await keys.Tick();nextGeneric=DateTime.UtcNow.AddMilliseconds(750);}}finally{engineLock.Release();}}},cancel.Token);
                byte[] buffer=new byte[65536];
                while(socket.State==WebSocketState.Open)
                {
                    using var ms=new MemoryStream();WebSocketReceiveResult result;
                    do {result=await socket.ReceiveAsync(buffer,cancel.Token);if(result.MessageType==WebSocketMessageType.Close)break;ms.Write(buffer,0,result.Count);if(ms.Length>1048576)throw new InvalidDataException("Oversized SDK event");}while(!result.EndOfMessage);
                    if(result.MessageType==WebSocketMessageType.Close)break;
                    using var doc=JsonDocument.Parse(ms.ToArray());await engineLock.WaitAsync(cancel.Token);try{await engine.Handle(doc.RootElement);await keys.Handle(doc.RootElement);}finally{engineLock.Release();}
                }
                cancel.Cancel();try{await timer;}catch(OperationCanceledException){} return 0;
            }
            catch(Exception e) when(e is WebSocketException or OperationCanceledException or IOException or JsonException or InvalidOperationException)
            { cancel.Cancel(); Console.Error.WriteLine($"SDK connection: {e.GetType().Name}"); if(attempt==3)return 1;await Task.Delay(1000); }
        }
        return 0;
    }
}

interface IWheelNative
{
    string Foreground();string CursorRootApp();bool ModifiersHeld {get;}bool SubmitWheel(int delta);
}
static class WheelDispatcher
{
    public static bool IsWheel(string command)=>command is "SCROLLUP" or "SCROLLDOWN";
    public static int Delta(string command)=>command switch {"SCROLLUP"=>120,"SCROLLDOWN"=>-120,_=>0};
    public static uint NativeData(int delta)=>unchecked((uint)delta);
    public static bool Send(string app,string command,IWheelNative native,out string failure)
    {
        failure="";
        if(!IsWheel(command)||!StringComparer.OrdinalIgnoreCase.Equals(app,"Spotify.exe"))return false;
        if(!StringComparer.OrdinalIgnoreCase.Equals(native.Foreground(),"Spotify.exe"))return false;
        if(native.ModifiersHeld){failure="Release modifier keys";return false;}
        if(!StringComparer.OrdinalIgnoreCase.Equals(native.CursorRootApp(),"Spotify.exe")){failure="Point at Spotify pane";return false;}
        // Recheck both targets immediately before insertion; no focus or cursor movement.
        if(!StringComparer.OrdinalIgnoreCase.Equals(native.Foreground(),"Spotify.exe"))return false;
        if(!StringComparer.OrdinalIgnoreCase.Equals(native.CursorRootApp(),"Spotify.exe")){failure="Point at Spotify pane";return false;}
        if(!native.SubmitWheel(Delta(command))){failure="Scroll blocked by Windows";return false;}
        return true;
    }
}
class WindowsDesktop:IDesktop,IWheelNative
{
    public static void ProbeKeyboard()
    {
        uint thread=GetWindowThreadProcessId(GetForegroundWindow(),out _);IntPtr layout=GetKeyboardLayout(thread);
        var resolved=new[]{"CTRL+ALT+SLASH","SHIFT+COMMA","SHIFT+PERIOD","CTRL+BRACKETLEFT","CTRL+BRACKETRIGHT","MINUS","EQUAL"}.ToDictionary(command=>command,command=>layout==IntPtr.Zero?Array.Empty<ushort>():Chord.Resolve(command,ch=>VkKeyScanExW(ch,layout)));
        Console.WriteLine(JsonSerializer.Serialize(new{layout=layout.ToInt64().ToString("X"),resolved,commandsSent=false}));
    }
    public string InputFailure {get;private set;}="";
    public string Foreground()
    {
        try {GetWindowThreadProcessId(GetForegroundWindow(),out uint pid);return Process.GetProcessById((int)pid).ProcessName+".exe";}catch{return "";}
    }
    static readonly HashSet<string> Allowed=new(StringComparer.OrdinalIgnoreCase){"chrome.exe","stremio-shell-ng.exe","Spotify.exe","Telegram.exe","WhatsApp.Root.exe","bambu-studio.exe"};
    public bool Send(string app,string chord)
    {
        InputFailure="";
        if(MediaDispatch.IsMedia(chord)||chord=="STOP")return false; // No global media virtual keys.
        if(WheelDispatcher.IsWheel(chord))
        {
            bool ok=WheelDispatcher.Send(app,chord,this,out string failure);InputFailure=failure;return ok;
        }
        if(!Allowed.Contains(app)||!StringComparer.OrdinalIgnoreCase.Equals(Foreground(),app))return false;
        // Do not interfere with a user-held modifier or inject a chord into a different foreground window.
        if(ModifiersHeld)return false;
        uint thread=GetWindowThreadProcessId(GetForegroundWindow(),out _);IntPtr layout=GetKeyboardLayout(thread);
        if(layout==IntPtr.Zero){InputFailure="Keyboard layout unavailable";return false;}
        if(YouTubeSpeed.IsCommand(chord)&&!StringComparer.OrdinalIgnoreCase.Equals(app,"chrome.exe"))return false;
        var packets=YouTubeSpeed.IsCommand(chord)?YouTubeSpeed.Packets(chord):new[]{Chord.Resolve(chord,character=>VkKeyScanExW(character,layout))};
        if(packets.Length==0||packets.Any(keys=>keys.Length==0)){InputFailure="Shortcut unavailable in layout";return false;}
        var keys=packets.SelectMany(packet=>packet).Distinct().ToArray();
        var input=packets.SelectMany(packet=>packet.Select(k=>Make(k,false)).Concat(packet.Reverse().Select(k=>Make(k,true)))).ToArray();
        if(!StringComparer.OrdinalIgnoreCase.Equals(Foreground(),app))return false;
        uint sent=SendInput((uint)input.Length,input,Marshal.SizeOf<INPUT>());
        if(sent!=input.Length)
        {
            // Release only keys submitted by this batch if Windows reports partial insertion.
            var release=keys.Reverse().Select(k=>Make(k,true)).ToArray();SendInput((uint)release.Length,release,Marshal.SizeOf<INPUT>());
            return false;
        }
        return true;
    }
    public bool ModifiersHeld=>new[]{0x10,0x11,0x12,0x5B,0x5C}.Any(k=>(GetAsyncKeyState(k)&0x8000)!=0);
    public string CursorRootApp()
    {
        try
        {
            if(!GetCursorPos(out var point))return "";
            IntPtr root=GetAncestor(WindowFromPoint(point),2); // GA_ROOT, not the owned-root chain.
            if(root==IntPtr.Zero)return "";
            GetWindowThreadProcessId(root,out uint pid);return Process.GetProcessById((int)pid).ProcessName+".exe";
        }
        catch{return "";}
    }
    public bool SubmitWheel(int delta)
    {
        if(delta is not (120 or -120))return false;
        var input=new[]{new INPUT{type=0,u=new INPUTUNION{mi=new MOUSEINPUT{mouseData=WheelDispatcher.NativeData(delta),dwFlags=0x0800}}}};
        return SendInput(1,input,Marshal.SizeOf<INPUT>())==1;
    }
    static INPUT Make(ushort k,bool up)=>new(){type=1,u=new INPUTUNION{ki=new KEYBDINPUT{wVk=k,dwFlags=(up?2u:0u)|(k is >=0x21 and <=0x28 or 0xB0 or 0xB1 or 0xB3?1u:0u)}}};
    public AudioState Audio()=>AudioEndpoint.With(v=>{v.GetMasterVolumeLevelScalar(out float scalar);v.GetMute(out bool muted);return new AudioState(scalar*100,muted);});
    public bool AdjustAudio(int delta,bool toggle)
    {try{return AudioEndpoint.With(v=>{Guid g=Guid.Empty;if(toggle){v.GetMute(out bool m);v.SetMute(!m,ref g);}else {v.GetMasterVolumeLevelScalar(out float x);v.SetMasterVolumeLevelScalar(Math.Clamp(x+delta/100f,0,1),ref g);}return true;});}catch{return false;}}
    [DllImport("user32.dll")]static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]static extern uint GetWindowThreadProcessId(IntPtr h,out uint id);
    [DllImport("user32.dll")]static extern short GetAsyncKeyState(int key);
    [DllImport("user32.dll")]static extern IntPtr GetKeyboardLayout(uint thread);
    [DllImport("user32.dll",CharSet=CharSet.Unicode)]static extern short VkKeyScanExW(char character,IntPtr layout);
    [StructLayout(LayoutKind.Sequential)]struct POINT {public int x,y;}
    [DllImport("user32.dll")]static extern bool GetCursorPos(out POINT point);
    [DllImport("user32.dll")]static extern IntPtr WindowFromPoint(POINT point);
    [DllImport("user32.dll")]static extern IntPtr GetAncestor(IntPtr hwnd,uint flags);
    [DllImport("user32.dll",SetLastError=true)]static extern uint SendInput(uint n,INPUT[] input,int size);
    [StructLayout(LayoutKind.Sequential)]struct INPUT {public uint type;public INPUTUNION u;}
    [StructLayout(LayoutKind.Explicit)]struct INPUTUNION {[FieldOffset(0)]public KEYBDINPUT ki;[FieldOffset(0)]public MOUSEINPUT mi;}
    [StructLayout(LayoutKind.Sequential)]struct KEYBDINPUT {public ushort wVk,wScan;public uint dwFlags,time;public UIntPtr dwExtraInfo;}
    [StructLayout(LayoutKind.Sequential)]struct MOUSEINPUT {public int dx,dy;public uint mouseData,dwFlags,time;public UIntPtr dwExtraInfo;}
}

static class Chord
{
    static readonly Dictionary<string,ushort> Special=new(){["TAB"]=9,["ENTER"]=13,["BACKSPACE"]=8,["ESC"]=27,["SPACE"]=32,["PGUP"]=33,["PGDOWN"]=34,["LEFT"]=37,["UP"]=38,["RIGHT"]=39,["DOWN"]=40,["SUBTRACT"]=0x6D,["ADD"]=0x6B,["F3"]=0x72,["PLAY"]=0xB3,["NEXT"]=0xB0,["PREV"]=0xB1};
    static readonly Dictionary<string,char> Punctuation=new(){["COMMA"]=',',["PERIOD"]='.',["MINUS"]='-',["EQUAL"]='=',["SLASH"]='/',["BRACKETLEFT"]='[',["BRACKETRIGHT"]=']'};
    // This US map validates catalog grammar/tests only. Live dispatch always supplies VkKeyScanExW for the foreground thread's HKL.
    public static ushort[] Keys(string chord)=>Resolve(chord,c=>c switch {','=>0xBC,'.'=>0xBE,'-'=>0xBD,'='=>0xBB,'/'=>0xBF,'['=>0xDB,']'=>0xDD,'<'=>0x1BC,'>'=>0x1BE,_=>-1});
    public static ushort[] Resolve(string chord,Func<char,short> translate)
    {
        var parts=chord.Split('+');if(parts.Length is <1 or >4)return [];
        int flags=0;foreach(string modifier in parts[..^1]){int flag=modifier switch {"SHIFT"=>1,"CTRL"=>2,"ALT"=>4,_=>0};if(flag==0)return [];flags|=flag;}
        string token=parts[^1];ushort vk;
        if(Punctuation.TryGetValue(token,out char character))
        {
            // Documented speed shortcuts are the '<' and '>' characters, not US physical key locations.
            if((flags&1)!=0&&token is "COMMA" or "PERIOD"){character=token=="COMMA"?'<':'>';flags&=~1;}
            short scan=translate(character);if(scan==-1)return [];vk=(ushort)(scan&255);if(vk==0||vk==255)return [];flags|=(scan>>8)&7;
        }
        else if(Special.TryGetValue(token,out ushort special))vk=special;
        else if(token.Length==1&&char.IsAsciiLetterOrDigit(token[0]))vk=token[0];
        else return [];
        List<ushort> keys=[];if((flags&2)!=0)keys.Add(0x11);if((flags&1)!=0)keys.Add(0x10);if((flags&4)!=0)keys.Add(0x12);keys.Add(vk);return keys.ToArray();
    }
}

static class AudioEndpoint
{
    public static T With<T>(Func<IAudioEndpointVolume,T> fn)
    {
        object? enumerator=null;IMMDevice? device=null;object? endpoint=null;
        try {enumerator=new MMDeviceEnumerator();((IMMDeviceEnumerator)enumerator).GetDefaultAudioEndpoint(0,1,out device);Guid iid=typeof(IAudioEndpointVolume).GUID;device.Activate(ref iid,23,IntPtr.Zero,out endpoint);return fn((IAudioEndpointVolume)endpoint);}
        finally {if(endpoint!=null)Marshal.ReleaseComObject(endpoint);if(device!=null)Marshal.ReleaseComObject(device);if(enumerator!=null)Marshal.ReleaseComObject(enumerator);}
    }
}
[ComImport,Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]class MMDeviceEnumerator {}
[ComImport,Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]interface IMMDeviceEnumerator {void EnumAudioEndpoints(int a,int b,out IntPtr c);void GetDefaultAudioEndpoint(int flow,int role,out IMMDevice device);}
[ComImport,Guid("D666063F-1587-4E43-81F1-B948E807363F"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]interface IMMDevice {void Activate(ref Guid iid,uint ctx,IntPtr p,[MarshalAs(UnmanagedType.IUnknown)]out object o);}
[ComImport,Guid("5CDF2C82-841E-4546-9722-0CF74078229A"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]interface IAudioEndpointVolume
{
    void RegisterControlChangeNotify(IntPtr p);void UnregisterControlChangeNotify(IntPtr p);void GetChannelCount(out uint n);void SetMasterVolumeLevel(float level,ref Guid g);void SetMasterVolumeLevelScalar(float level,ref Guid g);void GetMasterVolumeLevel(out float level);void GetMasterVolumeLevelScalar(out float level);void SetChannelVolumeLevel(uint channel,float level,ref Guid g);void SetChannelVolumeLevelScalar(uint channel,float level,ref Guid g);void GetChannelVolumeLevel(uint channel,out float level);void GetChannelVolumeLevelScalar(uint channel,out float level);void SetMute([MarshalAs(UnmanagedType.Bool)]bool mute,ref Guid g);void GetMute([MarshalAs(UnmanagedType.Bool)]out bool mute);
}

class FakeDesktop:IDesktop
{
    public string App="chrome.exe";public List<string> Sent=[];public AudioState State=new(42,false);
    public string InputFailure {get;private set;}="";public bool PointerOnSpotify=true;
    public string Foreground()=>App;public bool Send(string app,string chord){InputFailure="";if(app!=App)return false;if(WheelDispatcher.IsWheel(chord)&&!PointerOnSpotify){InputFailure="Point at Spotify pane";return false;}Sent.Add(chord);return true;}
    public AudioState Audio()=>State;public bool AdjustAudio(int delta,bool toggle){State=new(Math.Clamp(State.Percent+delta,0,100),toggle?!State.Muted:State.Muted);return true;}
}
class FakeWheelNative:IWheelNative
{
    public string App="Spotify.exe",Hover="Spotify.exe";public bool ModifiersHeld {get;set;}
    public bool LoseForegroundOnRecheck,LosePointerOnRecheck,SubmitOk=true;
    public int ForegroundReads,PointerReads;public List<int> Submitted=[];
    public string Foreground()=>++ForegroundReads>=2&&LoseForegroundOnRecheck?"ChatGPT.exe":App;
    public string CursorRootApp()=>++PointerReads>=2&&LosePointerOnRecheck?"Chrome.exe":Hover;
    public bool SubmitWheel(int delta){Submitted.Add(delta);return SubmitOk;}
}
static class Tests
{
    public static async Task<int> Run()
    {
        string catalogPath=Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,"../catalog.json"));
        var definitions=JsonSerializer.Deserialize<List<DialSpec>>(File.ReadAllText(catalogPath))!;
        foreach(var definition in definitions)
        {
            foreach(string chord in new[]{definition.Left,definition.Right,definition.Press})
                if(WheelDispatcher.IsWheel(chord)) {if(definition.App!="Spotify.exe")throw new Exception("Wheel outside Spotify catalog");}
                else if(chord is not ("VOLUP" or "VOLDOWN" or "MUTE") && !YouTubeSpeed.IsCommand(chord) && Chord.Keys(chord).Length==0)throw new Exception($"Invalid binding: {definition.Id} {chord}");
            if(!File.Exists(Path.Combine(Path.GetDirectoryName(catalogPath)!,definition.Icon)))throw new Exception("Missing icon "+definition.Id);
        }
        Console.WriteLine($"PASS {definitions.Count} catalog definitions, all chords and image paths");
        var spec=new DialSpec("test","chrome.exe","SEEK 10s","images/test.png","#ff4545","J","L","K","Back 10s","Forward 10s","Play / pause",false);
        var fake=new FakeDesktop();List<JsonElement> output=[];var e=new Engine([spec,spec with {Id="volume",Volume=true,Left="VOLDOWN",Right="VOLUP",Press="MUTE"}],fake,o=>{output.Add(JsonSerializer.SerializeToElement(o));return Task.CompletedTask;});
        async Task Event(string name,object payload){await e.Handle(JsonSerializer.SerializeToElement(new {@event=name,action=Engine.Uuid,context="a",payload}));}
        void Check(bool ok,string label){if(!ok)throw new Exception(label);Console.WriteLine("PASS "+label);}
        string FeedbackText(JsonElement item)=>item.GetProperty("payload").GetProperty("value").GetProperty("value").GetString()??"";
        await Event("willAppear",new {settings=new {dialId="test"}});Check(output[0].GetProperty("event").GetString()=="setFeedbackLayout","SDK custom layout assigned");Check(output[1].GetProperty("payload").GetProperty("icon").GetString()==spec.Icon,"logo feedback path");
        await Event("dialRotate",new {ticks=-2});Check(fake.Sent.SequenceEqual(new[]{"J","J"}),"negative ticks map CCW");
        fake.Sent.Clear();await Event("dialRotate",new {ticks=int.MaxValue});Check(fake.Sent.Count==8&&fake.Sent.All(x=>x=="L"),"positive ticks capped at8");
        fake.Sent.Clear();await Event("dialUp",new {});Check(fake.Sent.Count==0,"unpaired up ignored");await Event("dialDown",new {});await Event("dialUp",new {});await Event("dialUp",new {});Check(fake.Sent.SequenceEqual(new[]{"K"}),"one dispatch per push");
        await Event("touchTap",new {});Check(fake.Sent.Count==2,"touch dispatch");fake.App="ChatGPT.exe";await Event("dialRotate",new{ticks=1});Check(fake.Sent.Count==2,"unrelated foreground refused");Check(FeedbackText(output.Last())=="Open Chrome","foreground feedback truthful");
        fake.App="chrome.exe";fake.Sent.Clear();await Event("dialDown",new{});await Event("dialRotate",new{ticks=1,pressed=true});await Event("dialUp",new{});Check(fake.Sent.SequenceEqual(new[]{"L"}),"held rotation does not also click");
        Check(Chord.Keys("CTRL+SHIFT+TAB").SequenceEqual(new ushort[]{17,16,9}),"modifier order");Check(Chord.Keys("SHIFT+COMMA").SequenceEqual(new ushort[]{16,188}),"speed punctuation");Check(Chord.Keys("CTRL+ALT+DELETE").Length==0,"unknown privileged chord refused");
        await Event("willAppear",new {settings=new {dialId="volume"}});await Event("dialRotate",new{ticks=2});Check(fake.State.Percent==46,"audio adjusts actual value");Check(FeedbackText(output.Last())=="46%","audio readback displayed");await Event("dialDown",new{});await Event("dialUp",new{});Check(fake.State.Muted,"audio mute");await Event("willDisappear",new{});Check(e.Count==0,"disappear stops visible polling");
        var focus=definitions.Single(d=>d.Id=="spotify-media-2");var scroll=definitions.Single(d=>d.Id=="spotify-media-3");
        Check(focus.Press=="ENTER"&&focus.PressLabel=="Activate"&&Chord.Keys("ENTER").SequenceEqual(new ushort[]{13}),"Spotify focus press activates focused control with Enter");
        Check(scroll.Title=="SCROLL"&&scroll.Left=="SCROLLUP"&&scroll.Right=="SCROLLDOWN"&&scroll.Press=="ALT+SHIFT+Q","Spotify scroll catalog and queue press preserved");
        List<JsonElement> spotifyOutput=[];fake.App="Spotify.exe";fake.Sent.Clear();
        var spotifyEngine=new Engine([focus,scroll],fake,o=>{spotifyOutput.Add(JsonSerializer.SerializeToElement(o));return Task.CompletedTask;});
        async Task SpotifyEvent(string name,object payload){await spotifyEngine.Handle(JsonSerializer.SerializeToElement(new{@event=name,action=Engine.Uuid,context="s",payload}));}
        await SpotifyEvent("willAppear",new{settings=new{dialId=focus.Id}});await SpotifyEvent("dialDown",new{});await SpotifyEvent("dialUp",new{});Check(fake.Sent.SequenceEqual(new[]{"ENTER"}),"Spotify SDK push dispatches Enter, not CtrlK");
        fake.Sent.Clear();await SpotifyEvent("willAppear",new{settings=new{dialId=scroll.Id}});await SpotifyEvent("dialRotate",new{ticks=-2});await SpotifyEvent("dialRotate",new{ticks=1});
        Check(fake.Sent.SequenceEqual(new[]{"SCROLLUP","SCROLLUP","SCROLLDOWN"}),"Spotify SDK rotation directions use wheel commands");
        fake.Sent.Clear();await SpotifyEvent("dialRotate",new{ticks=int.MinValue});Check(fake.Sent.Count==8,"Spotify wheel tick cap remains8");
        fake.Sent.Clear();fake.PointerOnSpotify=false;await SpotifyEvent("dialRotate",new{ticks=1});Check(fake.Sent.Count==0&&FeedbackText(spotifyOutput.Last())=="Point at Spotify pane","Spotify outside-pointer feedback truthful");
        Check(spotifyOutput.Last().GetProperty("payload").GetProperty("value").GetProperty("font").GetProperty("size").GetInt32()==12,"Spotify pointer instruction fits without truncating");
        Check(spotifyOutput.Last().GetProperty("payload").GetProperty("detail").GetString()=="Point at the pane to scroll","Spotify idle instruction identifies target pane");
        fake.PointerOnSpotify=true;await SpotifyEvent("dialDown",new{});await SpotifyEvent("dialUp",new{});Check(fake.Sent.SequenceEqual(new[]{"ALT+SHIFT+Q"}),"Spotify scroll press still opens queue");
        string wheelFailure;var native=new FakeWheelNative();
        Check(WheelDispatcher.Send("Spotify.exe","SCROLLUP",native,out wheelFailure)&&WheelDispatcher.Send("Spotify.exe","SCROLLDOWN",native,out wheelFailure)&&native.Submitted.SequenceEqual(new[]{120,-120}),"native wheel boundary receives exactly ±120 per detent");
        Check(WheelDispatcher.NativeData(120)==120&&unchecked((int)WheelDispatcher.NativeData(-120))==-120,"native MOUSEINPUT preserves signed down delta");
        native=new(){Hover="Chrome.exe"};Check(!WheelDispatcher.Send("Spotify.exe","SCROLLUP",native,out wheelFailure)&&wheelFailure=="Point at Spotify pane"&&native.Submitted.Count==0,"native wheel refuses other-app hover root");
        native=new(){App="ChatGPT.exe"};Check(!WheelDispatcher.Send("Spotify.exe","SCROLLUP",native,out wheelFailure)&&native.Submitted.Count==0,"native wheel refuses other foreground app");
        native=new();Check(!WheelDispatcher.Send("chrome.exe","SCROLLUP",native,out wheelFailure)&&native.Submitted.Count==0,"wheel commands restricted to Spotify catalog app");
        native=new(){ModifiersHeld=true};Check(!WheelDispatcher.Send("Spotify.exe","SCROLLUP",native,out wheelFailure)&&wheelFailure=="Release modifier keys"&&native.Submitted.Count==0,"native wheel refuses held modifier");
        native=new(){LoseForegroundOnRecheck=true};Check(!WheelDispatcher.Send("Spotify.exe","SCROLLUP",native,out wheelFailure)&&native.Submitted.Count==0,"native wheel rechecks foreground before insertion");
        native=new(){LosePointerOnRecheck=true};Check(!WheelDispatcher.Send("Spotify.exe","SCROLLUP",native,out wheelFailure)&&native.Submitted.Count==0,"native wheel rechecks hover before insertion");
        native=new(){SubmitOk=false};Check(!WheelDispatcher.Send("Spotify.exe","SCROLLUP",native,out wheelFailure)&&wheelFailure=="Scroll blocked by Windows","native input failure is reported without false success");
        Check(YouTubeSpeed.Packets("YTSPEEDDOWN").Single().SequenceEqual(new ushort[]{16,188}),"YouTube slower sends Shift+comma without AltGr");
        Check(YouTubeSpeed.Packets("YTSPEEDUP").Single().SequenceEqual(new ushort[]{16,190}),"YouTube faster sends Shift+period without AltGr");
        var reset=YouTubeSpeed.Packets("YTSPEEDRESET");
        Check(reset.Length==35&&reset.Take(32).All(p=>p.SequenceEqual(new ushort[]{16,188}))&&reset.Skip(32).All(p=>p.SequenceEqual(new ushort[]{16,190})),"YouTube reset clamps to minimum then returns to normal speed without playback key");
        for(double rate=.25;rate<=8;rate+=.25){double result=rate;foreach(var packet in reset)result=Math.Clamp(result+(packet[1]==188?-.25:.25),.25,8);Check(result==1,"YouTube reset from "+rate+"x reaches 1x");}
        await YouTubeTests.Run(definitions);
        await KeyTests.Run();return 0;
    }
}
