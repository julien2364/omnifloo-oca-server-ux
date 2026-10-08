# Copyright 2026 Omnifloo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase, new_test_user


class TestDateRangeAccess(TransactionCase):
    """Multi-company restriction carried by ``security/ir.access.csv``.

    In Odoo 20 the former ``ir.rule`` records became ``ir.access`` lines without
    group, i.e. restrictions: a user must not see the date ranges (and types) of
    a company he is not allowed in, while shared ones (no company) stay visible.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env["res.company"].create({"name": "Company A"})
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})
        cls.user = new_test_user(
            cls.env,
            login="date_range_user_a",
            groups="base.group_user",
            company_id=cls.company_a.id,
            company_ids=[(6, 0, cls.company_a.ids)],
        )
        cls.types = {}
        cls.ranges = {}
        for key, company in (
            ("a", cls.company_a),
            ("b", cls.company_b),
            ("shared", cls.env["res.company"]),
        ):
            cls.types[key] = cls.env["date.range.type"].create(
                {"name": f"Type {key}", "company_id": company.id}
            )
            cls.ranges[key] = cls.env["date.range"].create(
                {
                    "name": f"Range {key}",
                    "type_id": cls.types[key].id,
                    "company_id": company.id,
                    "date_start": "2026-01-01",
                    "date_end": "2026-12-31",
                }
            )

    def test_user_sees_own_and_shared_ranges_only(self):
        visible = self.env["date.range"].with_user(self.user).search([])
        self.assertIn(self.ranges["a"], visible)
        self.assertIn(self.ranges["shared"], visible)
        self.assertNotIn(self.ranges["b"], visible)

    def test_user_sees_own_and_shared_types_only(self):
        visible = self.env["date.range.type"].with_user(self.user).search([])
        self.assertIn(self.types["a"], visible)
        self.assertIn(self.types["shared"], visible)
        self.assertNotIn(self.types["b"], visible)
