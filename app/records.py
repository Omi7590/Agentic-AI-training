#RTI Mitra - Record Module

import sys
import os 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.sample_records import records as _records

def load_records():
    """Return all RTI relu records."""
    return _records

def search (keyword):
    keyword = keyword.lower()
    return [
        r for r in _records
        if keyword in r['topic'].lower() or keyword in r['rule'].lower()
    ]

def count_by(field):
    """Count records grouped by a given field (e.g. 'jurisdiction')."""
    counts = {}
    for r in _records:
        key = r.get(field, "Unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts

def get_by_id(index):
    """Return a record by its 0-based index, or None if out of range."""
    if 0 <= index < len(_records):
        return _records[index]
    return None