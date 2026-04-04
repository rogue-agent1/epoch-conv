#!/usr/bin/env python3
"""epoch - timestamp converter (unix epoch ↔ human dates, durations, comparisons)."""

import argparse, sys, time, re
from datetime import datetime, timezone, timedelta

FORMATS = [
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M", "%Y-%m-%d", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y",
    "%d %b %Y %H:%M:%S", "%d %b %Y", "%b %d, %Y", "%B %d, %Y",
    "%a, %d %b %Y %H:%M:%S", "%Y%m%d%H%M%S", "%Y%m%d",
]

def parse_ts(s):
    """Parse string to epoch. Handles epoch, ISO, common formats."""
    s = s.strip()
    # Pure number = epoch
    if re.match(r'^-?\d+(\.\d+)?$', s):
        v = float(s)
        # ms if > year 3000 in seconds
        if v > 32503680000:
            v /= 1000
        return v
    # Try formats
    for fmt in FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse: {s}")

def fmt_duration(secs):
    neg = secs < 0
    secs = abs(secs)
    parts = []
    for unit, div in [("y", 31536000), ("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]:
        if secs >= div:
            val = int(secs // div)
            secs %= div
            parts.append(f"{val}{unit}")
    result = " ".join(parts) or "0s"
    return f"-{result}" if neg else result

def show_epoch(ts):
    dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
    dt_local = datetime.fromtimestamp(ts)
    now = time.time()
    diff = now - ts

    print(f"  Epoch:       {int(ts)}")
    print(f"  Epoch (ms):  {int(ts * 1000)}")
    print(f"  UTC:         {dt_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  Local:       {dt_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  ISO 8601:    {dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"  RFC 2822:    {dt_utc.strftime('%a, %d %b %Y %H:%M:%S +0000')}")
    print(f"  Day:         {dt_utc.strftime('%A')}")
    print(f"  Week:        {dt_utc.strftime('%V')} of {dt_utc.year}")
    print(f"  Day of year: {dt_utc.strftime('%j')}")
    if diff > 0:
        print(f"  Ago:         {fmt_duration(diff)}")
    else:
        print(f"  In:          {fmt_duration(-diff)}")

def cmd_now(args):
    print()
    show_epoch(time.time())
    print()

def cmd_convert(args):
    print()
    try:
        ts = parse_ts(args.value)
        show_epoch(ts)
    except ValueError as e:
        print(f"  {e}")
    print()

def cmd_diff(args):
    try:
        ts1 = parse_ts(args.time1)
        ts2 = parse_ts(args.time2)
    except ValueError as e:
        print(f"  {e}")
        return
    d = ts2 - ts1
    print(f"\n  Time 1:    {datetime.fromtimestamp(ts1, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  Time 2:    {datetime.fromtimestamp(ts2, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  Diff:      {fmt_duration(d)}")
    print(f"  Seconds:   {d:.0f}")
    print(f"  Minutes:   {d/60:.1f}")
    print(f"  Hours:     {d/3600:.2f}")
    print(f"  Days:      {d/86400:.3f}")
    print()

def cmd_add(args):
    try:
        ts = parse_ts(args.base) if args.base else time.time()
    except ValueError as e:
        print(f"  {e}")
        return
    # Parse duration
    total = 0
    for m in re.finditer(r'(-?\d+(?:\.\d+)?)\s*(s|sec|m|min|h|hr|d|day|w|week|y|year)', args.duration):
        val = float(m.group(1))
        unit = m.group(2)[0]
        mult = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31536000}
        total += val * mult.get(unit, 1)
    if total == 0:
        # Try pure seconds
        try:
            total = float(args.duration)
        except ValueError:
            print(f"  Cannot parse duration: {args.duration}")
            return
    result = ts + total
    print(f"\n  Base:      {datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  Added:     {fmt_duration(total)}")
    print(f"  Result:    {datetime.fromtimestamp(result, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  Epoch:     {int(result)}")
    print()

def cmd_range(args):
    try:
        start = parse_ts(args.start)
        end = parse_ts(args.end)
    except ValueError as e:
        print(f"  {e}")
        return
    step = int(args.step)
    print()
    ts = start
    while ts <= end:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        print(f"  {int(ts)}  {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        ts += step
    print()

def main():
    p = argparse.ArgumentParser(description="Timestamp converter")
    sp = p.add_subparsers(dest="cmd")

    sp.add_parser("now", help="Current time").set_defaults(func=cmd_now)

    c = sp.add_parser("convert", help="Convert timestamp/date")
    c.add_argument("value", help="Epoch, date string, or ISO format")
    c.set_defaults(func=cmd_convert)

    d = sp.add_parser("diff", help="Difference between two times")
    d.add_argument("time1")
    d.add_argument("time2")
    d.set_defaults(func=cmd_diff)

    a = sp.add_parser("add", help="Add duration to time")
    a.add_argument("duration", help="Duration (e.g. 2h30m, 7d, 3600)")
    a.add_argument("--base", help="Base time (default: now)")
    a.set_defaults(func=cmd_add)

    r = sp.add_parser("range", help="Generate time range")
    r.add_argument("start")
    r.add_argument("end")
    r.add_argument("--step", default="3600", help="Step in seconds (default: 3600)")
    r.set_defaults(func=cmd_range)

    args = p.parse_args()
    if not args.cmd:
        args.func = cmd_now
    args.func(args)

if __name__ == "__main__":
    main()
