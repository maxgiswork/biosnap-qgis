# -*- coding: utf-8 -*-
import os
import sys
plugin_dir = os.path.dirname(os.path.dirname(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)
import json
try:
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import urlopen, Request
    from urllib import urlencode
def _fetch(url):
    req = Request(url)
    req.add_header("User-Agent", "BioSnap-QGIS-Plugin/1.0")
    response = urlopen(req, timeout=10)
    return json.loads(response.read().decode("utf-8"))
def search_gbif(query):
    results = []
    try:
        params = urlencode({"q": query, "limit": 10})
        data = _fetch("https://api.gbif.org/v1/species/suggest?" + params)
        for item in data:
            results.append({
                "key":        str(item.get("key", "")),
                "name":       item.get("canonicalName") or item.get("scientificName", ""),
                "authorship": item.get("authorship", ""),
                "rank":       item.get("rank", "").lower(),
                "status":     item.get("status", ""),
                "source":     "gbif",
            })
    except Exception as e:
        print("BioSnap GBIF search error: {0}".format(e))
    return results
def search_inat(query):
    results = []
    try:
        params = urlencode({"q": query, "per_page": 10})
        data = _fetch("https://api.inaturalist.org/v1/taxa?" + params)
        for item in data.get("results", []):
            status = "ACCEPTED" if item.get("is_active") else "INACTIVE"
            results.append({
                "key":        str(item.get("id", "")),
                "name":       item.get("name", ""),
                "authorship": "",
                "rank":       item.get("rank", "").lower(),
                "status":     status,
                "source":     "inat",
            })
    except Exception as e:
        print("BioSnap iNat search error: {0}".format(e))
    return results
def enrich_gbif_statuses(results):
    enriched = []
    for r in results:
        try:
            data = _fetch("https://api.gbif.org/v1/species/{0}".format(r["key"]))
            r["status"]     = data.get("taxonomicStatus", r.get("status", ""))
            r["authorship"] = data.get("authorship", r.get("authorship", ""))
        except Exception:
            pass
        enriched.append(r)
    return enriched
def search_taxon(query, source):
    if not query or len(query.strip()) < 2:
        return []
    q = query.strip()
    if source == "gbif":
        return enrich_gbif_statuses(search_gbif(q))
    elif source == "inat":
        return search_inat(q)
    elif source == "combined":
        seen  = set()
        items = []
        for r in enrich_gbif_statuses(search_gbif(q)) + search_inat(q):
            key = (r["name"].lower(), r["rank"])
            if key not in seen:
                seen.add(key)
                items.append(r)
        return items
    return []
def fetch_gbif_details(key):
    try:
        data = _fetch("https://api.gbif.org/v1/species/{0}".format(key))
        ancestors = []
        for field in ["kingdom", "phylum", "class", "order", "family", "genus"]:
            val = data.get(field)
            if val:
                ancestors.append(val)
        return {
            "key":        str(data.get("key", key)),
            "name":       data.get("canonicalName") or data.get("scientificName", ""),
            "authorship": data.get("authorship", ""),
            "rank":       data.get("rank", "").lower(),
            "status":     data.get("taxonomicStatus", ""),
            "ancestors":  ancestors,
            "url":        "https://www.gbif.org/species/{0}".format(key),
            "source":     "gbif",
        }
    except Exception as e:
        print("BioSnap GBIF details error: {0}".format(e))
        return None
def fetch_inat_details(key):
    try:
        data = _fetch("https://api.inaturalist.org/v1/taxa/{0}".format(key))
        results = data.get("results", [])
        if not results:
            return None
        item = results[0]
        ancestors = [a.get("name", "") for a in item.get("ancestors", []) if a.get("name")]
        return {
            "key":        str(item.get("id", key)),
            "name":       item.get("name", ""),
            "authorship": "",
            "rank":       item.get("rank", "").lower(),
            "status":     "ACCEPTED" if item.get("is_active") else "INACTIVE",
            "ancestors":  ancestors[-5:] if ancestors else [],
            "url":        "https://www.inaturalist.org/taxa/{0}".format(key),
            "source":     "inat",
        }
    except Exception as e:
        print("BioSnap iNat details error: {0}".format(e))
        return None
def fetch_taxon_details(key, source):
    if source in ("gbif", "combined"):
        return fetch_gbif_details(key)
    elif source == "inat":
        return fetch_inat_details(key)
    return None
