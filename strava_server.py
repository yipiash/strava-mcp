#!/usr/bin/env python3
"""
Strava MCP Server
Exposes ALL Strava API v3 endpoints as MCP tools for Claude Desktop.
"""

import os
import json
import time
import httpx
from pathlib import Path
from mcp.server.fastmcp import FastMCP

STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET", "")
TOKENS_PATH = Path(os.environ.get("STRAVA_TOKENS_PATH", str(Path(__file__).parent / "tokens.json")))
BASE_URL = "https://www.strava.com/api/v3"

mcp = FastMCP("Strava")


def _load_tokens():
    if TOKENS_PATH.exists():
        return json.loads(TOKENS_PATH.read_text())
    return None


def _save_tokens(tokens):
    TOKENS_PATH.write_text(json.dumps(tokens, indent=2))


def _refresh_access_token():
    tokens = _load_tokens()
    if not tokens:
        raise RuntimeError("Not authenticated. Run authorize.py first.")
    resp = httpx.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
        },
        timeout=15,
    )
    resp.raise_for_status()
    new_tokens = resp.json()
    _save_tokens(new_tokens)
    return new_tokens["access_token"]


def _get_access_token():
    tokens = _load_tokens()
    if not tokens:
        raise RuntimeError("Not authenticated. Run authorize.py first.")
    if tokens.get("expires_at", 0) < time.time():
        return _refresh_access_token()
    return tokens["access_token"]


def _api(method, endpoint, params=None, json_body=None):
    token = _get_access_token()
    headers = {"Authorization": "Bearer " + token}
    url = BASE_URL + endpoint
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    resp = httpx.request(method, url, headers=headers, params=params, json=json_body, timeout=30)
    resp.raise_for_status()
    if resp.status_code == 204:
        return {"status": "success"}
    return resp.json()


# ── ATHLETE ──────────────────────────────────────────────────────────────────

@mcp.tool()
def get_authenticated_athlete() -> dict:
    """Get the currently authenticated athlete's profile (name, bio, city, weight, clubs, bikes, shoes, etc.)."""
    return _api("GET", "/athlete")


@mcp.tool()
def get_athlete_zones() -> dict:
    """Get the authenticated athlete's heart-rate and power zones."""
    return _api("GET", "/athlete/zones")


@mcp.tool()
def get_athlete_stats(athlete_id: int) -> dict:
    """Get an athlete's aggregate stats (total runs, rides, swims, recent efforts, all-time totals, YTD totals).
    Args:
        athlete_id: The athlete's numeric ID. Use get_authenticated_athlete() to find your own ID.
    """
    return _api("GET", "/athletes/" + str(athlete_id) + "/stats")


@mcp.tool()
def update_athlete(weight: float) -> dict:
    """Update the authenticated athlete's weight.
    Args:
        weight: The athlete's weight in kilograms.
    """
    return _api("PUT", "/athlete", json_body={"weight": weight})


# ── ACTIVITIES ───────────────────────────────────────────────────────────────

@mcp.tool()
def list_activities(page: int = 1, per_page: int = 30, before: int = 0, after: int = 0) -> list:
    """List the authenticated athlete's activities (most recent first).
    Args:
        page: Page number (default 1).
        per_page: Number of items per page (max 200, default 30).
        before: Only activities before this Unix timestamp. Use 0 to skip.
        after: Only activities after this Unix timestamp. Use 0 to skip.
    """
    p = {"page": page, "per_page": per_page}
    if before > 0:
        p["before"] = before
    if after > 0:
        p["after"] = after
    return _api("GET", "/athlete/activities", params=p)


@mcp.tool()
def get_activity(activity_id: int, include_all_efforts: bool = False) -> dict:
    """Get full details of a single activity.
    Args:
        activity_id: The activity's numeric ID.
        include_all_efforts: Whether to include all segment efforts (default False).
    """
    return _api("GET", "/activities/" + str(activity_id), params={"include_all_efforts": include_all_efforts})


@mcp.tool()
def create_activity(name: str, sport_type: str, start_date_local: str, elapsed_time: int, description: str = "", distance: float = 0.0, trainer: bool = False, commute: bool = False) -> dict:
    """Create a manual activity.
    Args:
        name: The name of the activity.
        sport_type: Sport type (e.g. Run, Ride, Swim, Hike, Walk, WeightTraining, Yoga, etc.).
        start_date_local: ISO 8601 local start time (e.g. "2024-01-15T08:30:00Z").
        elapsed_time: Duration in seconds.
        description: Optional description.
        distance: Optional distance in meters. Use 0 to skip.
        trainer: Whether this is a trainer/indoor activity.
        commute: Whether this is a commute.
    """
    body = {
        "name": name,
        "sport_type": sport_type,
        "start_date_local": start_date_local,
        "elapsed_time": elapsed_time,
        "trainer": int(trainer),
        "commute": int(commute),
    }
    if description:
        body["description"] = description
    if distance > 0:
        body["distance"] = distance
    return _api("POST", "/activities", json_body=body)


@mcp.tool()
def update_activity(activity_id: int, name: str = "", sport_type: str = "", description: str = "", trainer: str = "", commute: str = "", gear_id: str = "") -> dict:
    """Update an existing activity's editable fields. Only non-empty values are updated.
    Args:
        activity_id: The activity's numeric ID.
        name: New name (leave empty to skip).
        sport_type: New sport type (leave empty to skip).
        description: New description (leave empty to skip).
        trainer: "true" or "false" (leave empty to skip).
        commute: "true" or "false" (leave empty to skip).
        gear_id: Gear ID to associate, or "none" to remove (leave empty to skip).
    """
    body = {}
    if name:
        body["name"] = name
    if sport_type:
        body["sport_type"] = sport_type
    if description:
        body["description"] = description
    if trainer:
        body["trainer"] = trainer.lower() == "true"
    if commute:
        body["commute"] = commute.lower() == "true"
    if gear_id:
        body["gear_id"] = gear_id
    return _api("PUT", "/activities/" + str(activity_id), json_body=body)


@mcp.tool()
def get_activity_comments(activity_id: int, page: int = 1, per_page: int = 30) -> list:
    """List comments on an activity.
    Args:
        activity_id: The activity's numeric ID.
        page: Page number.
        per_page: Items per page (max 200).
    """
    return _api("GET", "/activities/" + str(activity_id) + "/comments", params={"page": page, "per_page": per_page})


@mcp.tool()
def get_activity_kudos(activity_id: int, page: int = 1, per_page: int = 30) -> list:
    """List athletes who gave kudos on an activity.
    Args:
        activity_id: The activity's numeric ID.
        page: Page number.
        per_page: Items per page (max 200).
    """
    return _api("GET", "/activities/" + str(activity_id) + "/kudos", params={"page": page, "per_page": per_page})


@mcp.tool()
def get_activity_laps(activity_id: int) -> list:
    """List laps of an activity.
    Args:
        activity_id: The activity's numeric ID.
    """
    return _api("GET", "/activities/" + str(activity_id) + "/laps")


@mcp.tool()
def get_activity_zones(activity_id: int) -> list:
    """Get heart-rate and power zone distribution for an activity.
    Args:
        activity_id: The activity's numeric ID.
    """
    return _api("GET", "/activities/" + str(activity_id) + "/zones")


@mcp.tool()
def get_activity_streams(activity_id: int, stream_types: str = "time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth") -> dict:
    """Get detailed time-series data streams for an activity.
    Args:
        activity_id: The activity's numeric ID.
        stream_types: Comma-separated stream types. Available: time, distance, latlng, altitude, velocity_smooth, heartrate, cadence, watts, temp, moving, grade_smooth.
    """
    return _api("GET", "/activities/" + str(activity_id) + "/streams", params={"keys": stream_types, "key_by_type": True})


# ── SEGMENTS ─────────────────────────────────────────────────────────────────

@mcp.tool()
def get_segment(segment_id: int) -> dict:
    """Get details of a specific segment.
    Args:
        segment_id: The segment's numeric ID.
    """
    return _api("GET", "/segments/" + str(segment_id))


@mcp.tool()
def explore_segments(south_west_lat: float, south_west_lng: float, north_east_lat: float, north_east_lng: float, activity_type: str = "riding", min_cat: int = 0, max_cat: int = 5) -> dict:
    """Explore segments in a geographic bounding box.
    Args:
        south_west_lat: SW corner latitude.
        south_west_lng: SW corner longitude.
        north_east_lat: NE corner latitude.
        north_east_lng: NE corner longitude.
        activity_type: "riding" or "running" (default "riding").
        min_cat: Minimum climb category (0-5, default 0).
        max_cat: Maximum climb category (0-5, default 5).
    """
    bounds = str(south_west_lat) + "," + str(south_west_lng) + "," + str(north_east_lat) + "," + str(north_east_lng)
    return _api("GET", "/segments/explore", params={"bounds": bounds, "activity_type": activity_type, "min_cat": min_cat, "max_cat": max_cat})


@mcp.tool()
def list_starred_segments(page: int = 1, per_page: int = 30) -> list:
    """List segments the authenticated athlete has starred.
    Args:
        page: Page number.
        per_page: Items per page (max 200).
    """
    return _api("GET", "/segments/starred", params={"page": page, "per_page": per_page})


@mcp.tool()
def star_segment(segment_id: int, starred: bool = True) -> dict:
    """Star or unstar a segment.
    Args:
        segment_id: The segment's numeric ID.
        starred: True to star, False to unstar.
    """
    return _api("PUT", "/segments/" + str(segment_id) + "/starred", json_body={"starred": starred})


@mcp.tool()
def list_segment_efforts(segment_id: int, start_date_local: str = "", end_date_local: str = "", per_page: int = 30) -> list:
    """List the authenticated athlete's efforts on a segment.
    Args:
        segment_id: The segment's numeric ID.
        start_date_local: Filter efforts after this ISO 8601 date (leave empty to skip).
        end_date_local: Filter efforts before this ISO 8601 date (leave empty to skip).
        per_page: Items per page (max 200).
    """
    p = {"segment_id": segment_id, "per_page": per_page}
    if start_date_local:
        p["start_date_local"] = start_date_local
    if end_date_local:
        p["end_date_local"] = end_date_local
    return _api("GET", "/segment_efforts", params=p)


@mcp.tool()
def get_segment_effort(effort_id: int) -> dict:
    """Get details of a specific segment effort.
    Args:
        effort_id: The segment effort's numeric ID.
    """
    return _api("GET", "/segment_efforts/" + str(effort_id))


@mcp.tool()
def get_segment_effort_streams(effort_id: int, stream_types: str = "time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth") -> dict:
    """Get time-series data streams for a segment effort.
    Args:
        effort_id: The segment effort's numeric ID.
        stream_types: Comma-separated stream types.
    """
    return _api("GET", "/segment_efforts/" + str(effort_id) + "/streams", params={"keys": stream_types, "key_by_type": True})


@mcp.tool()
def get_segment_streams(segment_id: int, stream_types: str = "latlng,distance,altitude") -> dict:
    """Get streams (route shape data) for a segment.
    Args:
        segment_id: The segment's numeric ID.
        stream_types: Comma-separated types. Available for segments: latlng, distance, altitude.
    """
    return _api("GET", "/segments/" + str(segment_id) + "/streams", params={"keys": stream_types, "key_by_type": True})


# ── CLUBS ────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_clubs(page: int = 1, per_page: int = 30) -> list:
    """List clubs the authenticated athlete is a member of.
    Args:
        page: Page number.
        per_page: Items per page (max 200).
    """
    return _api("GET", "/athlete/clubs", params={"page": page, "per_page": per_page})


@mcp.tool()
def get_club(club_id: int) -> dict:
    """Get details of a specific club.
    Args:
        club_id: The club's numeric ID.
    """
    return _api("GET", "/clubs/" + str(club_id))


@mcp.tool()
def get_club_members(club_id: int, page: int = 1, per_page: int = 30) -> list:
    """List members of a club.
    Args:
        club_id: The club's numeric ID.
        page: Page number.
        per_page: Items per page (max 200).
    """
    return _api("GET", "/clubs/" + str(club_id) + "/members", params={"page": page, "per_page": per_page})


@mcp.tool()
def get_club_activities(club_id: int, page: int = 1, per_page: int = 30) -> list:
    """List recent activities posted by members of a club.
    Args:
        club_id: The club's numeric ID.
        page: Page number.
        per_page: Items per page (max 200).
    """
    return _api("GET", "/clubs/" + str(club_id) + "/activities", params={"page": page, "per_page": per_page})


@mcp.tool()
def get_club_admins(club_id: int, page: int = 1, per_page: int = 30) -> list:
    """List admins of a club.
    Args:
        club_id: The club's numeric ID.
        page: Page number.
        per_page: Items per page (max 200).
    """
    return _api("GET", "/clubs/" + str(club_id) + "/admins", params={"page": page, "per_page": per_page})


# ── GEAR ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_gear(gear_id: str) -> dict:
    """Get details of a piece of gear (bike, shoes, etc.).
    Args:
        gear_id: The gear's alphanumeric ID (e.g. "b12345" for bikes, "g12345" for shoes).
    """
    return _api("GET", "/gear/" + gear_id)


# ── ROUTES ───────────────────────────────────────────────────────────────────

@mcp.tool()
def list_routes(athlete_id: int, page: int = 1, per_page: int = 30) -> list:
    """List an athlete's routes.
    Args:
        athlete_id: The athlete's numeric ID.
        page: Page number.
        per_page: Items per page (max 200).
    """
    return _api("GET", "/athletes/" + str(athlete_id) + "/routes", params={"page": page, "per_page": per_page})


@mcp.tool()
def get_route(route_id: int) -> dict:
    """Get details of a specific route.
    Args:
        route_id: The route's numeric ID.
    """
    return _api("GET", "/routes/" + str(route_id))


@mcp.tool()
def get_route_streams(route_id: int) -> dict:
    """Get the streams (GPS track, altitude, distance) for a route.
    Args:
        route_id: The route's numeric ID.
    """
    return _api("GET", "/routes/" + str(route_id) + "/streams")


# ── UPLOADS ──────────────────────────────────────────────────────────────────

@mcp.tool()
def get_upload(upload_id: int) -> dict:
    """Check the status of an activity upload.
    Args:
        upload_id: The upload's numeric ID.
    """
    return _api("GET", "/uploads/" + str(upload_id))


if __name__ == "__main__":
    mcp.run()
