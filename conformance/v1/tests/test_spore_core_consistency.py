"""spore-core.json must match spore.json's $defs/spore_core.

This file lives in cmn-spec only: it reads the authoritative schemas next to
the conformance suite, and the suite's copy in cmn-substrate excludes it.
"""

import json
from pathlib import Path
import unittest


SCHEMAS = Path(__file__).resolve().parents[3] / "schemas" / "v1"


def load(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


class SporeCoreConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spore = load("spore.json")
        cls.core = load("spore-core.json")
        cls.core_def = cls.spore["$defs"]["spore_core"]

    def test_required_fields_match(self):
        # $schema is required in spore-core.json (a standalone document) but not
        # in spore.json's $defs/spore_core (embedded inside capsule).
        core_required = sorted(r for r in self.core.get("required", []) if r != "$schema")
        self.assertEqual(sorted(self.core_def.get("required", [])), core_required)

    def test_properties_match(self):
        # spore-core.json has an extra $schema const.
        core_props = {k: v for k, v in self.core.get("properties", {}).items() if k != "$schema"}
        self.assertEqual(self.core_def.get("properties", {}), core_props)

    def test_shared_defs_are_identical(self):
        # bond is intentionally different: spore-core.json forbids historical
        # relations (spawned_from, absorbed_from) while spore.json allows them
        # in published manifests.
        for name in ("tree", "cmn_uri"):
            with self.subTest(definition=name):
                self.assertEqual(self.spore["$defs"].get(name), self.core.get("$defs", {}).get(name))


if __name__ == "__main__":
    unittest.main()
