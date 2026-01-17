def detect_tables(rows, min_columns=2):
    tables = []

    for page in set(r.page for r in rows):
        page_rows = [r for r in rows if r.page == page]

        column_positions = set()
        for row in page_rows:
            for atom in row.atoms:
                column_positions.add(round(atom.x_center, 1))

        if len(column_positions) >= min_columns:
            tables.append(page)

    return tables
