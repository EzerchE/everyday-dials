using System.Text.Json;
using System.Security.Cryptography;
using System.Buffers.Binary;
namespace EverydayDials;

sealed class UnavailableAudio:IDesktop
{
    public string Foreground()=>"chrome.exe";public string InputFailure=>"";
    public AudioState Audio()=>throw new IOException("no endpoint");
    public bool AdjustAudio(int delta,bool toggle)=>false;public bool Send(string app,string chord)=>true;
}
static class YouTubeTests
{
    public static async Task Run(List<DialSpec> definitions)
    {
        void Check(bool value,string label){if(!value)throw new Exception(label);Console.WriteLine("PASS "+label);}
        string root=Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,".."));
        var youtube=definitions.Where(YouTubeFeedback.IsYouTube).ToArray();
        Check(youtube.Length==4,"exact four YouTube definitions use V7 canvas");
        foreach(var s in definitions)Check(YouTubeFeedback.Layout(s)==(s.Id.StartsWith("youtube-controls-")?"layouts/youtube.json":"layouts/control.json"),"layout selection "+s.Id);
        var layout=JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"layouts/youtube.json"))).RootElement;
        var items=layout.GetProperty("items").EnumerateArray().ToArray();
        Check(items.Length==1&&items[0].GetProperty("key").GetString()=="canvas"&&items[0].GetProperty("type").GetString()=="pixmap"&&items[0].GetProperty("rect").EnumerateArray().Select(n=>n.GetInt32()).SequenceEqual(new[]{0,0,200,100}),"V7 exactly one 200x100 pixmap eliminates text/bar and overlap layers");
        foreach(var spec in youtube)
        {
            foreach(int direction in new[]{-1,0,1})foreach(bool pressed in new[]{false,true})
            {
                var bytes=File.ReadAllBytes(Path.Combine(root,YouTubeFeedback.Background(spec,direction,pressed)));
                Check(BinaryPrimitives.ReadInt32BigEndian(bytes.AsSpan(16,4))==200&&BinaryPrimitives.ReadInt32BigEndian(bytes.AsSpan(20,4))==100,"native V7 canvas PNG dimensions "+spec.Id+":"+direction+":"+pressed);
            }
        }
        DateTime clock=new(2026,11,21,0,0,0,DateTimeKind.Utc);var desktop=new FakeDesktop();List<JsonElement> output=[];
        var engine=new Engine(youtube,desktop,o=>{output.Add(JsonSerializer.SerializeToElement(o));return Task.CompletedTask;},clock:()=>clock);
        async Task Event(string name,object payload,string context="youtube")=>await engine.Handle(JsonSerializer.SerializeToElement(new{@event=name,action=Engine.Uuid,context,payload}));
        string Background(string context="youtube")=>output.Last(o=>o.GetProperty("event").GetString()=="setFeedback"&&o.GetProperty("context").GetString()==context).GetProperty("payload").GetProperty("canvas").GetString()!;
        int Images()=>output.Count(o=>o.GetProperty("event").GetString()=="setImage");
        await Event("willAppear",new{settings=new{dialId="youtube-controls-2"}});
        Check(Background().EndsWith("dial-volume.png"),"Windows volume starts neutral with no fabricated percentage");
        int unchanged=output.Count;await engine.Tick();Check(output.Count==unchanged&&Images()==1,"V7 canvas and editor image cache avoid unchanged SDK sends");
        await Event("dialRotate",new{ticks=2});Check(desktop.State.Percent==46&&Background().EndsWith("-right.png"),"global master volume remains two percent per detent");
        clock=clock.AddMilliseconds(100);await Event("dialRotate",new{ticks=-1});
        clock=clock.AddMilliseconds(100);await engine.Tick(youtubeOnly:true);Check(Background().EndsWith("-left.png"),"direction deadline is renewed by last tick");
        clock=clock.AddMilliseconds(39);await engine.Tick(youtubeOnly:true);Check(Background().EndsWith("-left.png"),"direction remains before 140ms last-tick deadline");
        clock=clock.AddMilliseconds(1);await engine.Tick(youtubeOnly:true);Check(Background().EndsWith("dial-volume.png"),"YouTube fast tick expires direction at 140ms independently of generic poll");
        Check(Images()==1,"direction never enlarges or decorates the stable transparent editor glyph");
        await Event("dialDown",new{});Check(Background().EndsWith("dial-volume-pressed.png"),"dialDown immediately selects supplied held-press artwork");
        clock=clock.AddSeconds(2);await engine.Tick();Check(Background().EndsWith("-pressed.png")&&!desktop.State.Muted,"held press persists without premature action");
        await Event("dialUp",new{});Check(desktop.State.Muted&&Background().EndsWith("dial-volume-muted.png"),"release dispatches once and reads actual Windows master mute");
        await Event("dialUp",new{});Check(desktop.State.Muted,"duplicate release is ignored");
        desktop.State=new(44,false);await engine.Tick();Check(Background().EndsWith("dial-volume.png"),"external Windows unmute updates canvas without guessed browser state");
        await Event("touchTap",new{});Check(desktop.State.Muted&&Background().EndsWith("dial-volume-muted-pressed.png"),"touch dispatches one command with brief press feedback");
        clock=clock.AddMilliseconds(140);await engine.Tick(youtubeOnly:true);Check(desktop.State.Muted&&Background().EndsWith("dial-volume-muted.png"),"touch expires without second dispatch");
        await Event("willAppear",new{settings=new{dialId="youtube-controls-1"}},"speed");
        await Event("dialRotate",new{ticks=1},"speed");clock=clock.AddMilliseconds(80);await Event("dialRotate",new{ticks=-1});
        clock=clock.AddMilliseconds(60);await engine.Tick(youtubeOnly:true);
        Check(Background("speed").EndsWith("dial-speed.png")&&Background().EndsWith("-left.png"),"each dial context owns its last-tick expiry");
        desktop.Sent.Clear();await Event("dialDown",new{},"speed");await Event("dialRotate",new{ticks=2,pressed=true},"speed");await Event("dialUp",new{},"speed");
        Check(desktop.Sent.SequenceEqual(new[]{"YTSPEEDUP","YTSPEEDUP"}),"held rotation cancels the release action without losing ticks");
        await Event("dialDown",new{},"speed");await Event("dialUp",new{},"speed");Check(desktop.Sent.Last()=="YTSPEEDRESET","speed push preserves accepted reset operation");
        await Event("touchTap",new{},"speed");Check(desktop.Sent.Count(s=>s=="YTSPEEDRESET")==2&&!desktop.Sent.Contains("K"),"speed touch sends reset once without playback toggle");
        clock=clock.AddMilliseconds(140);await engine.Tick(youtubeOnly:true);desktop.App="ChatGPT.exe";int blockedCount=desktop.Sent.Count;
        await Event("dialRotate",new{ticks=-1},"speed");
        Check(desktop.Sent.Count==blockedCount&&Background("speed").EndsWith("dial-speed-left.png"),"YouTube physical direction feedback remains visible when foreground guard blocks command");
        clock=clock.AddMilliseconds(140);await engine.Tick(youtubeOnly:true);
        Check(Background("speed").EndsWith("dial-speed.png"),"blocked YouTube turn still expires to neutral after 140ms");
        await Event("dialDown",new{},"speed");Check(Background("speed").EndsWith("dial-speed-pressed.png"),"blocked YouTube press still shows held feedback before dispatch");
        await Event("dialUp",new{},"speed");Check(desktop.Sent.Count==blockedCount&&Background("speed").EndsWith("dial-speed.png"),"blocked YouTube release restores neutral without injecting shortcut");
        Check(output.Where(o=>o.GetProperty("event").GetString()=="setFeedback").All(o=>o.GetProperty("payload").EnumerateObject().Count()==1),"YouTube feedback contains only the V7 canvas, no overlay text or fake values");
        List<JsonElement> unknown=[];var unknownEngine=new Engine(youtube,new UnavailableAudio(),o=>{unknown.Add(JsonSerializer.SerializeToElement(o));return Task.CompletedTask;});
        await unknownEngine.Handle(JsonSerializer.SerializeToElement(new{@event="willAppear",action=Engine.Uuid,context="unknown",payload=new{settings=new{dialId="youtube-controls-2"}}}));
        Check(unknown.Last().GetProperty("payload").GetProperty("canvas").GetString()!.EndsWith("dial-volume.png"),"unavailable Windows endpoint shows neutral volume artwork");
        var keys=JsonSerializer.Deserialize<List<KeySpec>>(File.ReadAllText(Path.Combine(root,"key-catalog.json")))!;
        var hashes=JsonSerializer.Deserialize<Dictionary<string,string>>(File.ReadAllText(Path.Combine(root,"youtube-v7-key-sha256.json")))!;
        var media=new FakeMedia();List<JsonElement> keyOutput=[];
        var keyEngine=new KeyEngine(keys,desktop,media,o=>{keyOutput.Add(JsonSerializer.SerializeToElement(o));return Task.CompletedTask;},clock:()=>clock);
        foreach(var s in keys.Where(s=>s.Id.StartsWith("youtube-controls-key-")))
        {
            foreach(string path in new[]{s.Image,s.PlayImage,s.PauseImage,s.UnknownImage,s.MutedImage,s.UnmutedImage}.Distinct())foreach(string selected in new[]{path,KeyEngine.Pressed(path)})
            {var bytes=File.ReadAllBytes(Path.Combine(root,selected));Check(Convert.ToHexString(SHA256.HashData(bytes)).Equals(hashes[selected],StringComparison.OrdinalIgnoreCase)&&BinaryPrimitives.ReadInt32BigEndian(bytes.AsSpan(16,4))==144&&BinaryPrimitives.ReadInt32BigEndian(bytes.AsSpan(20,4))==144,"YouTube exact supplied native 144px key bytes "+selected);}
            async Task KeyEvent(string name,object payload)=>await keyEngine.Handle(JsonSerializer.SerializeToElement(new{@event=name,action=KeyEngine.Uuid,context="key",payload}));
            string KeyImage()=>keyOutput.Last(o=>o.GetProperty("event").GetString()=="setImage").GetProperty("payload").GetProperty("image").GetString()!;
            await KeyEvent("willAppear",new{settings=new{keyId=s.Id}});await KeyEvent("keyDown",new{});Check(KeyImage()==KeyEngine.Pressed(s.Image),"YouTube key pressed only while held "+s.Id);
            await KeyEvent("keyUp",new{});Check(KeyImage()==s.Image,"YouTube keyUp restores neutral immediately without 350ms linger "+s.Id);
        }
        Check(media.Reads==0,"YouTube feedback does not treat generic Chrome media state as exact browser state");
        Check(desktop.Sent.Count==blockedCount,"YouTube key press artwork does not bypass foreground guard");
        List<JsonElement> genericOutput=[];var other=new Engine([definitions.Single(s=>s.Id=="chrome-daily-0")],desktop,o=>{genericOutput.Add(JsonSerializer.SerializeToElement(o));return Task.CompletedTask;});
        await other.Handle(JsonSerializer.SerializeToElement(new{@event="willAppear",action=Engine.Uuid,context="generic",payload=new{settings=new{dialId="chrome-daily-0"}}}));
        int genericCount=genericOutput.Count;await other.Tick(youtubeOnly:true);Check(genericOutput.Count==genericCount,"fast YouTube ticks never poll/send generic application feedback");
        Check(genericOutput.All(o=>o.GetProperty("event").GetString()!="setImage"),"non-YouTube encoder images remain untouched");
    }
}
