"""Shared helpers: the files of 国土数値情報 バスルート (N07, 2022 edition) and how to read them."""

import io
import json
import zipfile

PREFS = {
    "01": "北海道",
    "02": "青森県",
    "03": "岩手県",
    "04": "宮城県",
    "05": "秋田県",
    "06": "山形県",
    "07": "福島県",
    "08": "茨城県",
    "09": "栃木県",
    "10": "群馬県",
    "11": "埼玉県",
    "12": "千葉県",
    "13": "東京都",
    "14": "神奈川県",
    "15": "新潟県",
    "16": "富山県",
    "17": "石川県",
    "18": "福井県",
    "19": "山梨県",
    "20": "長野県",
    "21": "岐阜県",
    "22": "静岡県",
    "23": "愛知県",
    "24": "三重県",
    "25": "滋賀県",
    "26": "京都府",
    "27": "大阪府",
    "28": "兵庫県",
    "29": "奈良県",
    "30": "和歌山県",
    "31": "鳥取県",
    "32": "島根県",
    "33": "岡山県",
    "34": "広島県",
    "35": "山口県",
    "36": "徳島県",
    "37": "香川県",
    "38": "愛媛県",
    "39": "高知県",
    "40": "福岡県",
    "41": "佐賀県",
    "42": "長崎県",
    "43": "熊本県",
    "44": "大分県",
    "45": "宮崎県",
    "46": "鹿児島県",
    "47": "沖縄県",
}
BASE = "https://nlftp.mlit.go.jp/ksj/gml/data/N07/N07-22/"
PAGE_URL = "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N07-v2_0.html"
TERMS_URL = "https://nlftp.mlit.go.jp/ksj/other/agreement.html"
CODELIST_URL = "https://nlftp.mlit.go.jp/ksj/gml/codelist/BusClassCd.html"
NATIONAL_ZIP = "N07-22_SHP.zip"
EPSG = 6668  # JGD2011, as the .prj and the GeoJSON of the source state


def zip_name(code: str) -> str:
    return f"N07-22_{code}_SHP.zip"


def member(names: list[str], suffix: str) -> str:
    found = [n for n in names if n.endswith(suffix) and "KS-META" not in n]
    if len(found) != 1:
        raise ValueError(f"expected one *{suffix} in the zip, found {found}")
    return found[0]


def read_zip(data: bytes, suffix: str) -> bytes:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        return z.read(member(z.namelist(), suffix))


def parse_features(geojson: bytes) -> list[dict]:
    """One dict per route: operator and the line as GeoJSON geometry.

    N07_002 (備考) is empty in every file of this edition; a value there means the source
    changed and the export must be extended, so it stops instead of dropping the text.
    """
    d = json.loads(geojson)
    out = []
    for f in d["features"]:
        p = f["properties"]
        if set(p) != {"N07_001", "N07_002"}:
            raise ValueError(f"unexpected properties {sorted(p)}")
        if p["N07_002"] not in (None, ""):
            raise ValueError(f"N07_002 has a value: {p['N07_002']!r}")
        if f["geometry"]["type"] != "LineString":
            raise ValueError(f"unexpected geometry {f['geometry']['type']}")
        out.append({"operator": p["N07_001"], "geometry": f["geometry"]})
    return out


def geo_metadata(crs: dict) -> dict:
    return {
        "version": "1.1.0",
        "primary_column": "geometry",
        "columns": {"geometry": {"encoding": "WKB", "geometry_types": ["LineString"], "crs": crs}},
    }
