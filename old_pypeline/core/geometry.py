from models.structures import RowCluster

def cluster_rows(atoms, y_threshold=6):
    rows = []

    for atom in sorted(atoms, key=lambda a: (a.page, a.y_center)):
        placed = False

        for row in rows:
            if atom.page == row.page and abs(atom.y_center - row.y_center) <= y_threshold:
                row.atoms.append(atom)
                row.y_center = sum(a.y_center for a in row.atoms) / len(row.atoms)
                placed = True
                break

        if not placed:
            rows.append(RowCluster(
                page=atom.page,
                y_center=atom.y_center,
                atoms=[atom]
            ))

    return rows
