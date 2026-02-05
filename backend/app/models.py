from __future__ import annotations

from pydantic import BaseModel


class AddDomainRequest(BaseModel):
    domain: str
    type: str = "blacklist"  # blacklist, whitelist, regex_black, regex_white, wildcard
    comment: str | None = None


class ToggleDomainRequest(BaseModel):
    enabled: bool


class UpdateDeviceRequest(BaseModel):
    nickname: str
    icon: str | None = None


class TimedBlockRequest(BaseModel):
    domains: list[str]
    duration_minutes: int = 30


class TimedBlockResponse(BaseModel):
    id: str
    domain: str
    created_at: int
    expires_at: int
    remaining_seconds: int = 0


DOMAIN_PRESETS = {
    "social": {
        "name": "Social Media",
        "domains": [
            {"domain": "reddit.com", "type": "wildcard"},
            {"domain": "twitter.com", "type": "wildcard"},
            {"domain": "x.com", "type": "wildcard"},
            {"domain": "instagram.com", "type": "wildcard"},
            {"domain": "tiktok.com", "type": "wildcard"},
            {"domain": "facebook.com", "type": "wildcard"},
            {"domain": r"(\.|^)(reddit|redd\.it|redditstatic|redditmedia)\.", "type": "regex_black"},
            {"domain": r"(\.|^)(twimg|t\.co)\.", "type": "regex_black"},
            {"domain": r"(\.|^)(cdninstagram|fbcdn)\.", "type": "regex_black"},
            {"domain": r"(\.|^)(tiktokcdn|musical\.ly)\.", "type": "regex_black"},
        ],
    },
    "video": {
        "name": "Video Streaming",
        "domains": [
            {"domain": "youtube.com", "type": "wildcard"},
            {"domain": "twitch.tv", "type": "wildcard"},
            {"domain": "netflix.com", "type": "wildcard"},
            {"domain": r"(\.|^)(googlevideo|ytimg|yt3\.ggpht)\.", "type": "regex_black"},
            {"domain": r"(\.|^)(ttvnw|jtvnw)\.", "type": "regex_black"},
            {"domain": r"(\.|^)(nflxvideo|nflximg|nflxso)\.", "type": "regex_black"},
        ],
    },
    "news": {
        "name": "News",
        "domains": [
            {"domain": "news.ycombinator.com", "type": "blacklist"},
            {"domain": "cnn.com", "type": "wildcard"},
            {"domain": "bbc.com", "type": "wildcard"},
            {"domain": "nytimes.com", "type": "wildcard"},
            {"domain": "foxnews.com", "type": "wildcard"},
        ],
    },
    "gaming": {
        "name": "Gaming",
        "domains": [
            {"domain": "store.steampowered.com", "type": "blacklist"},
            {"domain": "steamcommunity.com", "type": "blacklist"},
            {"domain": r"(\.|^)(epicgames|unrealengine)\.", "type": "regex_black"},
            {"domain": "discord.com", "type": "wildcard"},
            {"domain": r"(\.|^)discord(app)?\.", "type": "regex_black"},
        ],
    },
}
