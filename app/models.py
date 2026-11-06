# RTI Mitra - models.py
# Record dataclass representing one RTI rule record.

from dataclasses import dataclass

@dataclass
class Record:
    topic: str
    rule: str
    section_or_rule_ref: str
    jurisdiction: str
    amount_or_time_limit: str
    source_url: str

    def __str__(self):
        return (
            f"[{self.jurisdiction}] {self.topic}\n"
            f"  Rule   : {self.rule}\n"
            f"  Ref    : {self.section_or_rule_ref}\n"
            f"  Limit  : {self.amount_or_time_limit}\n"
            f"  Source : {self.source_url}"
        )

    @staticmethod
    def from_dict(data: dict) -> "Record":
        """Create a Record from a dictionary."""
        return Record(
            topic=data["topic"],
            rule=data["rule"],
            section_or_rule_ref=data["section_or_rule_ref"],
            jurisdiction=data["jurisdiction"],
            amount_or_time_limit=data["amount_or_time_limit"],
            source_url=data["source_url"],
        )
