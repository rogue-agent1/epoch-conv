#!/usr/bin/env python3
"""Unix epoch time converter."""
import sys, time
from datetime import datetime, timezone

def now():
    t = time.time()
    dt = datetime.now()
    utc = datetime.now(timezone.utc)
    print(f"  Epoch:     {int(t)}")
    print(f"  Epoch ms:  {int(t*1000)}")
    print(f"  Local:     {dt:%Y-%m-%d %H:%M:%S %Z}")
    print(f"  UTC:       {utc:%Y-%m-%d %H:%M:%S UTC}")
    print(f"  ISO 8601:  {utc.isoformat()}")

def from_epoch(ts):
    if ts > 1e12: ts /= 1000  # ms to s
    dt = datetime.fromtimestamp(ts)
    utc = datetime.fromtimestamp(ts, timezone.utc)
    print(f"  Local: {dt:%Y-%m-%d %H:%M:%S}")
    print(f"  UTC:   {utc:%Y-%m-%d %H:%M:%S UTC}")
    print(f"  Ago:   {format_delta(time.time() - ts)}")

def to_epoch(datestr):
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y']:
        try:
            dt = datetime.strptime(datestr, fmt)
            ts = int(dt.timestamp())
            print(f"  Epoch:  {ts}")
            print(f"  Epoch ms: {ts*1000}")
            return
        except: continue
    print(f"Could not parse: {datestr}")

def format_delta(s):
    if s < 60: return f"{int(s)}s"
    if s < 3600: return f"{int(s//60)}m {int(s%60)}s"
    if s < 86400: return f"{int(s//3600)}h {int(s%3600//60)}m"
    return f"{int(s//86400)}d {int(s%86400//3600)}h"

if __name__ == '__main__':
    if len(sys.argv) < 2: now()
    elif sys.argv[1].replace('.','').replace('-','').isdigit() and len(sys.argv[1]) >= 8:
        try: from_epoch(float(sys.argv[1]))
        except: to_epoch(' '.join(sys.argv[1:]))
    else:
        to_epoch(' '.join(sys.argv[1:]))
