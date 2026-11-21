using System.Text.Json;
using Windows.Media.Control;

namespace EverydayDials;

enum Playback { Unknown, Playing, Paused }
enum MediaAttempt { Unavailable, Rejected, Succeeded }
record MediaSnapshot(Playback State,bool Reliable);
interface IMediaProvider { MediaSnapshot Read(string app);Task<MediaAttempt> Execute(string app,string operation); }
class NoMedia:IMediaProvider
{
    public MediaSnapshot Read(string app)=>new(Playback.Unknown,false);
    public Task<MediaAttempt> Execute(string app,string operation)=>Task.FromResult(MediaAttempt.Unavailable);
}
class MediaSessions:IMediaProvider
{
    readonly GlobalSystemMediaTransportControlsSessionManager manager;
    MediaSessions(GlobalSystemMediaTransportControlsSessionManager value)=>manager=value;
    public static async Task<IMediaProvider> Create()
    {
        try {return new MediaSessions(await GlobalSystemMediaTransportControlsSessionManager.RequestAsync().AsTask().WaitAsync(TimeSpan.FromSeconds(3)));}
        catch{return new NoMedia();}
    }
    // No GetCurrentSession: it may belong to a different app. Never inspect media titles or URLs.
    public static bool Matches(string app,string source)=>app switch
    {
        "Spotify.exe"=>source.Equals("Spotify.exe",StringComparison.OrdinalIgnoreCase)||source.StartsWith("SpotifyAB.SpotifyMusic_zpdnekdrzrea0!",StringComparison.OrdinalIgnoreCase),
        "stremio-shell-ng.exe"=>source.Equals("stremio-shell-ng.exe",StringComparison.OrdinalIgnoreCase),
        _=>false // A generic Chrome session cannot prove which tab/site is controlled.
    };
    public static bool Unique(string app,IEnumerable<string> sources)=>sources.Count(source=>Matches(app,source))==1;
    GlobalSystemMediaTransportControlsSession? Resolve(string app)
    {
        try {var sessions=manager.GetSessions().Where(s=>Matches(app,s.SourceAppUserModelId)).ToArray();return sessions.Length==1?sessions[0]:null;}
        catch{return null;}
    }
    public MediaSnapshot Read(string app)
    {
        var session=Resolve(app);if(session==null)return new(Playback.Unknown,false);
        try {return new(session.GetPlaybackInfo().PlaybackStatus switch {GlobalSystemMediaTransportControlsSessionPlaybackStatus.Playing=>Playback.Playing,GlobalSystemMediaTransportControlsSessionPlaybackStatus.Paused=>Playback.Paused,_=>Playback.Unknown},true);}
        catch{return new(Playback.Unknown,false);}
    }
    public async Task<MediaAttempt> Execute(string app,string operation)
    {
        var session=Resolve(app);if(session==null)return MediaAttempt.Unavailable;
        try
        {
            var info=session.GetPlaybackInfo();var controls=info.Controls;
            Task<bool>? command=operation switch
            {
                "PLAY" when info.PlaybackStatus==GlobalSystemMediaTransportControlsSessionPlaybackStatus.Playing&&controls.IsPauseEnabled=>session.TryPauseAsync().AsTask(),
                "PLAY" when info.PlaybackStatus!=GlobalSystemMediaTransportControlsSessionPlaybackStatus.Playing&&controls.IsPlayEnabled=>session.TryPlayAsync().AsTask(),
                "PREV" when controls.IsPreviousEnabled=>session.TrySkipPreviousAsync().AsTask(),
                "NEXT" when controls.IsNextEnabled=>session.TrySkipNextAsync().AsTask(),
                _=>null
            };
            return command!=null&&await command.WaitAsync(TimeSpan.FromSeconds(2))?MediaAttempt.Succeeded:MediaAttempt.Rejected;
        }
        catch{return MediaAttempt.Rejected;}
    }
    public static async Task Probe()
    {
        var provider=await Create();
        var result=new[]{"Spotify.exe","stremio-shell-ng.exe","chrome.exe"}.ToDictionary(app=>app,app=>provider.Read(app));
        var identities=new List<object>();int otherCount=0;
        if(provider is MediaSessions native)
        {
            foreach(var session in native.manager.GetSessions())
            {
                string id=session.SourceAppUserModelId;
                if(new[]{"spotify","stremio","chrome"}.Any(known=>id.Contains(known,StringComparison.OrdinalIgnoreCase)))
                    identities.Add(new {appIdentity=id,status=session.GetPlaybackInfo().PlaybackStatus.ToString()});
                else otherCount++;
            }
        }
        Console.WriteLine(JsonSerializer.Serialize(new {provider=provider.GetType().Name,apps=result,knownAppIdentities=identities,otherSessionCount=otherCount,metadataRead=false,commandsSent=false}));
    }
}

static class MediaDispatch
{
    public static bool IsMedia(string command)=>command is "PLAY" or "PREV" or "NEXT";
    public static string LocalFallback(string app,string command)=>app switch
    {
        "Spotify.exe"=>command switch {"PLAY"=>"SPACE","PREV"=>"CTRL+LEFT","NEXT"=>"CTRL+RIGHT",_=>""},
        "stremio-shell-ng.exe" when command=="PLAY"=>"SPACE",
        "chrome.exe" when command=="PLAY"=>"K",
        _=>""
    };
    public static async Task<bool> Execute(IDesktop desktop,IMediaProvider media,string app,string command,string? fallback=null)
    {
        if(!StringComparer.OrdinalIgnoreCase.Equals(desktop.Foreground(),app))return false;
        var attempt=await media.Execute(app,command);
        if(attempt!=MediaAttempt.Unavailable)return attempt==MediaAttempt.Succeeded;
        string local=fallback??LocalFallback(app,command);
        return local.Length>0&&desktop.Send(app,local); // Never fall back to a global media virtual key.
    }
}
