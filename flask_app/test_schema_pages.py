from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import app


class SchemaPageTests(unittest.TestCase):
	def setUp(self):
		self.client = app.app.test_client()
		self.no_database = patch(
			"app.get_db_connection", side_effect=AssertionError("Unexpected database access")
		)
		self.no_database.start()
		self.addCleanup(self.no_database.stop)

	def test_schema_pages_and_exports(self):
		for key in app.CCID_VERSIONS:
			with self.subTest(year=key):
				data = app._load_ccid_schema(key)
				self.assertGreater(data["field_count"], 0)
				self.assertEqual(data["table_count"], len(data["schema"]))
				self.assertEqual(data["field_count"], len(data["field_defs"]))
				self.assertEqual(self.client.get(f"/ccid-schema/{key}").status_code, 200)
				export = self.client.get(f"/ccid-schema/{key}/export.md")
				self.assertEqual(export.status_code, 200)
				self.assertIn(data["title"], export.get_data(as_text=True))

	def test_schema_default_and_unknown_version(self):
		response = self.client.get("/ccid-schema")
		self.assertEqual(response.status_code, 302)
		self.assertTrue(response.location.endswith("/ccid-schema/2025"))
		self.assertEqual(self.client.get("/ccid-schema/unknown").status_code, 404)

	def test_missing_workbook_is_explicit(self):
		missing = {**app.CCID_VERSIONS["2024"], "path": Path("/missing/dictionary.xlsx")}
		with patch.dict(app.CCID_VERSIONS, {"2024": missing}):
			response = self.client.get("/ccid-schema/2024")
		self.assertEqual(response.status_code, 404)
		self.assertIn("dictionary.xlsx not found", response.get_data(as_text=True))

	def test_workbooks_are_deployable_through_git(self):
		root = Path(app.__file__).parent
		for version in app.CCID_VERSIONS.values():
			with self.subTest(workbook=version["path"].name):
				self.assertTrue(version["path"].is_file())
				result = subprocess.run(
					["git", "check-ignore", "-q", str(version["path"])],
					cwd=root, check=False,
				)
				self.assertEqual(result.returncode, 1)

	def test_home_has_no_table_sidebar(self):
		response = self.client.get("/")
		self.assertEqual(response.status_code, 200)
		html = response.get_data(as_text=True)
		self.assertNotIn("schema-panel", html)
		self.assertNotIn("schema-list", html)
		self.assertIn('class="col-12"', html)
		self.assertIn('id="run-btn"', html)
		self.assertIn('id="data-table"', html)

	def test_all_ccid_universe_pages_use_large_dialog(self):
		for year in app.CCID_VERSIONS:
			with self.subTest(year=year):
				response = self.client.get(f"/general-info/universe-installs-{year}")
				self.assertEqual(response.status_code, 200)
				html = response.get_data(as_text=True)
				self.assertIn("modal-dialog-scrollable modal-xl", html)
				self.assertIn("max-width: 1600px", html)
				self.assertIn('height: "100%"', html)
				self.assertIn('shown.bs.modal', html)


if __name__ == "__main__":
	unittest.main()
