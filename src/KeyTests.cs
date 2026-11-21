using System.Text.Json;
using System.Security.Cryptography;
namespace EverydayDials;

class FakeMedia:IMediaProvider
{
    public MediaSnapshot Snapshot=new(Playback.Playing,true);public MediaAttempt Attempt=MediaAttempt.Succeeded;
    public List<string> Calls=[];public int Reads;
    public MediaSnapshot Read(string app){Reads++;return Snapshot;}
    public Task<MediaAttempt> Execute(string app,string operation){Calls.Add(app+":"+operation);return Task.FromResult(Attempt);}
}
static class KeyTests
{
    public static async Task Run()
    {
        string root=Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,".."));
        var specs=JsonSerializer.Deserialize<List<KeySpec>>(File.ReadAllText(Path.Combine(root,"key-catalog.json")))!;
        void Check(bool value,string label){if(!value)throw new Exception(label);Console.WriteLine("PASS "+label);}
        foreach(var spec in specs)
        {
            foreach(string path in new[]{spec.Image,spec.PlayImage,spec.PauseImage,spec.UnknownImage,spec.MutedImage,spec.UnmutedImage}.Distinct())
            {Check(File.Exists(Path.Combine(root,path))&&File.Exists(Path.Combine(root,KeyEngine.Pressed(path))),"key artwork "+spec.Id+":"+Path.GetFileName(path));}
            if(spec.Kind=="website")Check(spec.Id=="chrome-daily-key-7"&&spec.App=="chrome.exe"&&spec.Command=="OPENYOUTUBE","fixed allowlisted website key definition");
            else if(spec.Command is not ("MUTE" or "VOLDOWN" or "VOLUP"))Check(Chord.Keys(spec.Command).Length>0,"key chord "+spec.Id);
            if(spec.Fallback.Length>0)Check(Chord.Keys(spec.Fallback).Length>0,"key fallback "+spec.Id);
        }
        var play=specs.Single(s=>s.Id=="spotify-media-key-0");var tab=specs.Single(s=>s.Id=="chrome-daily-key-1");var mute=specs.Single(s=>s.Id=="spotify-media-key-3");
        var distinct=new[]{play.PlayImage,play.PauseImage,play.UnknownImage}.Select(p=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(root,p))))).Distinct().Count();
        Check(distinct==3,"play/pause/unknown icons have distinct real content");
        var desktop=new FakeDesktop{App="Spotify.exe"};var media=new FakeMedia();List<JsonElement> output=[];DateTime clock=new(2026,11,15,0,0,0,DateTimeKind.Utc);
        var engine=new KeyEngine([play,tab,mute],desktop,media,o=>{output.Add(JsonSerializer.SerializeToElement(o));return Task.CompletedTask;},clock:()=>clock);
        async Task Event(string name,object payload)=>await engine.Handle(JsonSerializer.SerializeToElement(new{@event=name,action=KeyEngine.Uuid,context="k",payload}));
        string LastImage()=>output.Last(o=>o.GetProperty("event").GetString()=="setImage").GetProperty("payload").GetProperty("image").GetString()!;
        await Event("willAppear",new{settings=new{keyId=play.Id}});Check(LastImage()==play.PauseImage,"playing shows next operation Pause");
        await Event("keyDown",new{});await Event("keyDown",new{});Check(media.Calls.SequenceEqual(new[]{"Spotify.exe:PLAY"}),"duplicate keyDown dispatches exactly once");
        Check(LastImage()==KeyEngine.Pressed(play.PauseImage),"media press acknowledges without fake toggle");
        await Event("keyUp",new{});clock=clock.AddSeconds(1);await engine.Tick();Check(LastImage()==play.PauseImage,"flash resets while real state remains playing");
        media.Snapshot=new(Playback.Paused,true);await engine.Tick();Check(LastImage()==play.PlayImage,"external paused state changes next operation to Play");
        media.Snapshot=new(Playback.Unknown,false);await engine.Tick();Check(LastImage()==play.UnknownImage,"unknown media session stays neutral");
        desktop.App="chrome.exe";int calls=media.Calls.Count;await Event("keyDown",new{});await Event("keyUp",new{});Check(media.Calls.Count==calls&&output.Any(o=>o.GetProperty("event").GetString()=="showAlert"),"wrong foreground refuses media command and alerts");
        await Event("didReceiveSettings",new{settings=new{keyId=tab.Id}});await Event("keyDown",new{});await Event("keyDown",new{});Check(desktop.Sent.SequenceEqual(new[]{"CTRL+T"}),"momentary key dispatches once");
        Check(LastImage()==KeyEngine.Pressed(tab.Image),"momentary key pressed artwork");await Event("keyUp",new{});clock=clock.AddSeconds(1);await engine.Tick();Check(LastImage()==tab.Image,"momentary key returns to neutral artwork");
        desktop.App="Spotify.exe";await Event("willAppear",new{settings=new{keyId=mute.Id}});Check(LastImage()==mute.MutedImage,"unmuted system shows next operation Mute");
        desktop.State=new(42,true);await engine.Tick();Check(LastImage()==mute.UnmutedImage,"external system mute shows next operation Unmute");
        desktop.App="chrome.exe";await Event("keyDown",new{});await Event("keyUp",new{});Check(desktop.State.Muted,"wrong foreground also refuses master-mute key");
        await Event("willDisappear",new{});int reads=media.Reads;await engine.Tick();Check(engine.Count==0&&media.Reads==reads,"hidden key contexts stop polling");
        Check(MediaSessions.Unique("Spotify.exe",new[]{"SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify","Chrome"}),"exact Spotify package session maps independently");
        Check(!MediaSessions.Unique("Spotify.exe",new[]{"Spotify.exe","SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"}),"ambiguous Spotify sessions remain unknown");
        Check(!MediaSessions.Unique("Spotify.exe",new[]{"SpotifyAB.SpotifyMusic_other!Spotify"}),"lookalike package family rejected");
        Check(!MediaSessions.Unique("chrome.exe",new[]{"Chrome"}),"browser session cannot impersonate exact YouTube tab");
        desktop.Sent.Clear();desktop.App="Spotify.exe";media.Attempt=MediaAttempt.Rejected;Check(!await MediaDispatch.Execute(desktop,media,"Spotify.exe","PLAY")&&desktop.Sent.Count==0,"matched but rejected media operation never double-dispatches fallback");
        media.Attempt=MediaAttempt.Unavailable;Check(await MediaDispatch.Execute(desktop,media,"Spotify.exe","PLAY")&&desktop.Sent.SequenceEqual(new[]{"SPACE"}),"unavailable Spotify session uses guarded local shortcut, never global media key");
        Check(Chord.Resolve("CTRL+ALT+SLASH",c=>c=='/'?(short)0x137:(short)-1).SequenceEqual(new ushort[]{17,16,18,55}),"foreground Turkish slash layout adds required Shift");
        Check(Chord.Resolve("SHIFT+COMMA",c=>c=='<'?(short)0xE2:(short)-1).SequenceEqual(new ushort[]{226}),"speed down resolves literal less-than on Turkish layout");
        Check(Chord.Resolve("SHIFT+PERIOD",c=>c=='>'?(short)0x1E2:(short)-1).SequenceEqual(new ushort[]{16,226}),"speed up resolves literal greater-than on Turkish layout");
        Check(Chord.Resolve("CTRL+BRACKETLEFT",c=>c=='['?(short)0x638:(short)-1).SequenceEqual(new ushort[]{17,18,56}),"layout AltGr brackets are translated rather than fixed US VK");
        Check(Chord.Resolve("CTRL+ALT+SLASH",c=>(short)-1).Length==0,"unrepresentable punctuation fails closed");
        var cache=new ArtworkCache(root);Check(cache.Load(play.PlayImage).StartsWith("data:image/png;base64,"),"key feedback sends cached PNG data URI");
        bool escaped=false;try{cache.Load("../not-plugin.png");}catch(InvalidDataException){escaped=true;}Check(escaped,"artwork cache rejects traversal");
        var site=specs.Single(s=>s.Id=="chrome-daily-key-7");var started=new List<System.Diagnostics.ProcessStartInfo>();bool launchOk=true;
        var launcher=new FixedYouTubeLauncher(info=>{started.Add(info);return launchOk;});desktop.App="ChatGPT.exe";output.Clear();desktop.Sent.Clear();
        var siteEngine=new KeyEngine([site,tab],desktop,media,o=>{output.Add(JsonSerializer.SerializeToElement(o));return Task.CompletedTask;},clock:()=>clock,launcher:launcher);
        async Task SiteEvent(string name,object payload)=>await siteEngine.Handle(JsonSerializer.SerializeToElement(new{@event=name,action=KeyEngine.Uuid,context="site",payload}));
        await SiteEvent("willAppear",new{settings=new{keyId=site.Id}});await SiteEvent("keyDown",new{});await SiteEvent("keyDown",new{});
        Check(started.Count==1&&desktop.Sent.Count==0,"YouTube opens once per physical press even with another foreground app");
        var info=started[0];Check(info.FileName==@"C:\Program Files\Google\Chrome\Application\chrome.exe"&&!info.UseShellExecute&&info.ArgumentList.SequenceEqual(new[]{"https://www.youtube.com/"})&&info.Arguments=="","YouTube launcher fixes exact Chrome path and HTTPS URL without a shell");
        await SiteEvent("keyUp",new{});await SiteEvent("keyDown",new{});Check(started.Count==2,"YouTube release permits a new intentional press");
        await SiteEvent("keyUp",new{});launchOk=false;await SiteEvent("keyDown",new{});Check(output.Last(o=>o.GetProperty("event").GetString()=="showAlert").GetProperty("context").GetString()=="site","YouTube launch failure alerts");
        await SiteEvent("keyUp",new{});await SiteEvent("didReceiveSettings",new{settings=new{keyId=tab.Id}});await SiteEvent("keyDown",new{});Check(started.Count==3&&desktop.Sent.Count==0,"website exception does not remove other-key foreground guards");
        Check(!new FixedYouTubeLauncher(_=>throw new InvalidOperationException("simulated")).OpenYouTube(),"YouTube launcher exceptions fail closed without opening a browser");
    }
}
