def migrate(cr, version):
    cr.execute("""
        ALTER TABLE res_partner
        ADD COLUMN identificacion varchar;
    """)
